# coding: utf-8

from django.core.management.base import BaseCommand, CommandError

from ...models import get_indexer
from ... import conf as c


class Command(BaseCommand):
    help = 'Updates elasticsearch index'

    def handle(self, *args, **options):
        indexer = get_indexer()
        indexer.reset_index()
        indexer.index_documents()
        indexer.refresh_index()
