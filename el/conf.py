# coding: utf-8

from django.conf import settings

from elasticsearch_dsl import connections


# TODO: update configuration to mirror create_connection
ELASTICSEARCH_CONFIG = getattr(settings, 'ELASTICSEARCH_CONFIG', {})
ELASTICSEARCH_HOST = ELASTICSEARCH_CONFIG.get('host', 'localhost')
ELASTICSEARCH_PORT = ELASTICSEARCH_CONFIG.get('port', 9200)
ELASTICSEARCH_TIMEOUT = ELASTICSEARCH_CONFIG.get('port', 5)
INDEX_NAME = 'elastic'


def create_connection():
    connections.connections.create_connection(
        hosts=['{}:{}'.format(ELASTICSEARCH_HOST, ELASTICSEARCH_PORT)],
        timeout=ELASTICSEARCH_TIMEOUT
    )
