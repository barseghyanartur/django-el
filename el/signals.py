# coding: utf-8

from django.db.models import signals

from . import index


def get_indexed_instance(instance):
    indexed_instance = instance.get_indexed_instance()
    if indexed_instance is None:
        return

    # Make sure that the instance is in its class's indexed objects
    if not type(indexed_instance).get_indexable().filter(
            pk=indexed_instance.pk).exists():
        return

    return indexed_instance


def post_save_signal_handler(instance, **kwargs):
    indexed_instance = get_indexed_instance(instance)

    if indexed_instance:
        index.get_indexer().add_document(indexed_instance)


def post_delete_signal_handler(instance, **kwargs):
    indexed_instance = get_indexed_instance(instance)

    if indexed_instance:
        index.get_indexer().delete_document(indexed_instance)


def register_signal_handlers():
    for model in index.get_indexed_models():
        signals.post_save.connect(post_save_signal_handler, sender=model)
        signals.post_delete.connect(post_delete_signal_handler, sender=model)
