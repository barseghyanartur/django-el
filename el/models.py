# coding: utf-8

from django.db import models

from elasticsearch_dsl import Mapping, String
from elasticsearch_dsl import connections, Search
from elasticsearch_dsl import connections
from elasticsearch.helpers import streaming_bulk
from elasticsearch import NotFoundError
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

from . import managers
from . import conf as c


def get_indexed_models():
    return [
        model for model in apps.get_models()
        if issubclass(model, Indexed) and not model._meta.abstract
    ]


class Indexer:
    def __init__(self, index):
        self.es = connections.connections.get_connection()
        self.index = index

    def reset_index(self):
        # Delete old index
        try:
            self.es.indices.delete(self.index)
        except NotFoundError:
            pass

        # Create new index
        self.es.indices.create(self.index)

    def refresh_index(self):
        self.es.indices.refresh(self.index)

    def save_mapping(self, model_class):
        mapping = model_class.get_mapping()
        mapping.save(self.index)
        print('Saved mapping {}\n'.format(mapping.doc_type))

    def index_documents(self):
        models = list(get_indexed_models())

        for model in models:
            self.save_mapping(model)

            model_instances = model.get_indexable().iterator()
            docs = (self.to_indexable_dict(d) for d in model_instances)
            for ok, info in streaming_bulk(self.es, docs):
                print("  Document with id %s indexed." % info['index']['_id'])

    def add_document(self, doc):
        self.es.index(
            self.index,
            doc.get_mapping().doc_type,
            self.to_indexable_dict(doc),
            doc.id,
        )

    def delete_document(self, doc):
        try:
            self.es.delete(
                self.index,
                doc.get_mapping().doc_type,
                doc.id,
            )
        except NotFoundError:
            pass

    def to_indexable_dict(self, obj):
        cls = obj.__class__
        fields = list(cls.get_mapping().properties.properties.to_dict().keys())

        data = {
            '_index': c.INDEX_NAME,
            '_type': cls.get_mapping_name(),
            '_id': obj.pk,
        }
        for field_name in fields:
            if field_name == 'content_type':
                data['content_type'] = cls.indexed_get_content_type()
            elif field_name == 'pk':
                data['pk'] = obj.pk
            else:
                data[field_name] = self.get_value_from_field(field_name, obj)

        return data

    def get_value_from_field(self, field_name, obj):
        try:
            field = obj.__class__._meta.get_field(field_name)
            value = field._get_val_from_obj(obj)
        except models.fields.FieldDoesNotExist:
            value = getattr(obj, field_name, None)
            if callable(value):
                value = value()

        return value


class DjangoObjectsSearch(Search):

    def __init__(self, *args, **kwargs):
        self.model_class = kwargs.pop('model_class', None)
        super().__init__(*args, **kwargs)

    def _clone(self, *args, **kwargs):
        s = super()._clone(*args, **kwargs)
        s.model_class = self.model_class
        return s

    def execute(self, *args, **kwargs):
        hits = super().execute(*args, **kwargs)

        # Get pks from results
        pks = [int(hit.pk) for hit in hits]

        # Initialise results dictionary
        results = dict((str(pk), None) for pk in pks)

        # Find objects in database and add them to dict
        queryset = self.model_class.objects.filter(pk__in=pks)
        for obj in queryset:
            results[str(obj.pk)] = obj

        # Return results in order given by ElasticSearch
        return [results[str(pk)] for pk in pks if results[str(pk)]]


def get_indexer():
    return Indexer(c.INDEX_NAME)


class Indexed(object):

    @classmethod
    def get_mapping_name(cls):
        return cls.__name__.lower()

    @classmethod
    def get_mapping(cls):
        m = Mapping(cls.get_mapping_name())
        m.field('pk', 'integer')
        m.field('content_type', String(index='not_analyzed'))
        return cls.configure_mapping(m)

    @classmethod
    def configure_mapping(cls, mapping):
        return mapping

    @classmethod
    def indexed_get_parent(cls, require_model=True):
        for base in cls.__bases__:
            if issubclass(base, Indexed) and (issubclass(base, models.Model) or require_model is False):
                return base

    @classmethod
    def indexed_get_content_type(cls):
        content_type = (cls._meta.app_label + '_' + cls.__name__).lower()

        # Get parent content type
        parent = cls.indexed_get_parent()
        if parent:
            parent_content_type = parent.indexed_get_content_type()
            return parent_content_type + '_' + content_type
        else:
            return content_type

    def get_indexed_instance(self):
        # This is accessed on save by the wagtailsearch signal handler, and in edge
        # cases (e.g. loading test fixtures), may be called before the specific instance's
        # entry has been created. In those cases, we aren't ready to be indexed yet, so
        # return None.
        try:
            return self.specific
        except self.specific_class.DoesNotExist:
            return None

    @classmethod
    def search(cls):
        ct = cls.indexed_get_content_type()
        return DjangoObjectsSearch(
            model_class=cls).filter('term', content_type=ct)

    @classmethod
    def get_indexable(cls):
        raise NotImplementedError
