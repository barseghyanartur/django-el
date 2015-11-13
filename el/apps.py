# coding: utf-8

from django.apps import AppConfig

from .signals import register_signal_handlers



class DefaultConfig(AppConfig):
    name = 'el'
    verbose_name = 'el'

    def ready(self):
        # импортировать сигналы для их регистрации
        import el.signals
        from el.conf import create_connection
        create_connection()
        register_signal_handlers()
