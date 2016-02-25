This is Django application that helps intergrate Django with elasticsearch.
It is built on top of ``elasticsearch-dsl``.

---------------

|python| |pypi| |license|

---------------


Overview
--------

Project aims to support Python 3 and Django 1.8 (at least).

The library is in development, use it carefully, because until stable an API
is a subject to change.

The library supports indexing multiple models with ``el.models.Indexed`` mixin.
Such models are autodiscovered and indexed automatically with an
``update_index`` command.

Currently you can query only one type of models, only Article, or BlogPost,
for example.
The library is just just a thin integration layer of ``elasticsearch-dsl`` and
``django``, because former comes with other persisting layer (a ``DocType`` one).

If you want to query multiple models at once, you can use raw ``elasticsearch-dsl``
query and then cast documents to models using elasticsearch document meta
information (model content_type and pk).

The library was written as an experiment, inspired by ``django-wagtail``,
so it provides just a basic functionality.

If you feel happy with ``elasticsearch-dsl``, this library *might*
suit your needs. If you are not, then maybe it is better idea to use
``django-haystack`` + ``elasticstack``.


Feel free to contribute and improve, if you feel you need it :)


Quickstart
----------

Configure your models to be indexable::

    from django.db import models
    from el.models import Indexed

    class Article(models.Model, Indexed):
        title = models.CharField(max_length=78)

        @classmethod
        def get_indexable(cls):
            return cls.objects.all()

        @classmethod
        def configure_mapping(cls, mapping):
            # mapping is an elasticsearch_dsl Mapping object
            mapping.field('title', 'string')
            return mapping


From this moment, the ``Article`` model will be autodiscovered and indexed.


Update search indexes::

    ./manage.py update_index


Use ``elasticsearch_dsl`` to query::

    # articles is a list of an Article instances
    articles = Article.search().query('match', title="Bob's article").execute()

    # articles is a list of elasticsearch_dsl hits
    articles = Article.search().query('match', title="Bob's article").execute(cast=False)


In contrast with ``elasticsearch_dsl``, ``django-el`` provides modified
``Search`` object which return django model instances instead of raw
elasticsearch results by default. You can control this feature using the
``cast`` argument.


Installation
------------

Install ``django-el`` as usual python package using pip::

    pip install django-el


Configuration
-------------

Django-el is build on top of ``elasticsearch_dsl`` library and provides
django-way connections configuration through ``settings.py``::

    ELASTICSEARCH_CONNECTIONS = {
        'default': {
            'hosts': ['127.0.0.1:9200'],
            'serializer': 'project.serializers.MySerializer',
        }
    }

You can define project connections using ``ELASTICSEARCH_CONNECTIONS``
setting. It is just a hight-level interface over low-level
``elasticsearch_dsl.connections.connections.create_connection`` function.

The keys are (default, in this example) are connection aliases, and it's values
are ``create_connection`` arguments.


.. |pypi| image:: https://img.shields.io/pypi/v/django-el.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-el
    :alt: pypi

.. |license| image:: https://img.shields.io/github/license/asyncee/django-el.svg?style=flat-square
    :target: https://github.com/asyncee/django-el/blob/master/LICENSE.txt
    :alt: MIT License

.. |python| image:: https://img.shields.io/badge/python-3.x-blue.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-el
    :alt: 3.x
