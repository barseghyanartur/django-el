# coding: utf-8

from django.apps import apps
from django.db.models.fields import FieldDoesNotExist

from elasticsearch_dsl import connections
from elasticsearch.helpers import streaming_bulk
from elasticsearch import NotFoundError

from .models import Indexed
from . import conf


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
            '_index': conf.INDEX_NAME,
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
        except FieldDoesNotExist:
            value = getattr(obj, field_name, None)
            if callable(value):
                value = value()

        return value


def get_indexer():
    return Indexer(conf.INDEX_NAME)
