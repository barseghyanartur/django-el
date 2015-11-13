# coding: utf-8

"""
Configuration for django-el.


CONNECTIONS - a dictionary which keys are conneciton aliases, and it's values
are elasticsearc_dsl.connections.create_connection arguments.
"""

from django.conf import settings
from django.utils.module_loading import import_string

from elasticsearch_dsl.connections import connections


DEFAULT_CONNECTIONS = {
    'default': {
        'hosts': ['localhost:9200'],
    }
}
INDEX_NAME = getattr(settings, 'ELASTICSEARCH_INDEX_NAME', 'elastic')
CONNECTIONS = getattr(settings, 'ELASTICSEARCH_CONNECTIONS', DEFAULT_CONNECTIONS)


def create_connections():
    """Create connections to elasticsearch as defined in settings.py."""
    for alias, params in CONNECTIONS.items():
        processed_params = {}
        for param_name, param_value in params.items():

            if param_name == 'serializer' and isinstance(param_value, str):
                param_value = import_string(param_value)

            processed_params[param_name] = param_value

        connections.create_connection(alias, **processed_params)
