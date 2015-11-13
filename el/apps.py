# coding: utf-8

from django.apps import AppConfig

from .signals import register_signal_handlers
from .conf import create_connections


class DefaultConfig(AppConfig):
    name = 'el'
    verbose_name = 'el'

    def ready(self):
        # импортировать сигналы для их регистрации
        import el.signals
        create_connections()
        register_signal_handlers()
