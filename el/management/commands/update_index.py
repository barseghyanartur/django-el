# coding: utf-8

from django.core.management.base import BaseCommand, CommandError

from ...index import get_indexer


class Command(BaseCommand):
    help = 'Updates elasticsearch index'

    def handle(self, *args, **options):
        indexer = get_indexer()
        indexer.reset_index()
        indexer.index_documents()
        indexer.refresh_index()
