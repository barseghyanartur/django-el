# coding: utf-8

from django.db import models

from elasticsearch_dsl import Mapping, String
from elasticsearch_dsl import Search


class DjangoObjectsSearch(Search):

    def __init__(self, *args, **kwargs):
        self.model_class = kwargs.pop('model_class', None)
        super().__init__(*args, **kwargs)

    def _clone(self, *args, **kwargs):
        s = super()._clone(*args, **kwargs)
        s.model_class = self.model_class
        return s

    def execute(self, cast=True, *args, **kwargs):
        hits = super().execute(*args, **kwargs)

        if not cast:
            return hits

        # Get pks from results
        pks = [str(hit.pk) for hit in hits]

        # Initialise results dictionary
        results = dict((pk, None) for pk in pks)

        # Find objects in database and add them to dict
        queryset = self.model_class.objects.filter(pk__in=pks)
        for obj in queryset:
            results[str(obj.pk)] = obj

        # Return results in order given by ElasticSearch
        return [results[str(pk)] for pk in pks if results[str(pk)]]


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
