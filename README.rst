This is Django application that helps intergrate Django with elasticsearch.
It is built on top of ``elasticsearch-dsl``.

---------------

|python| |pypi| |license|

---------------


Project aims to support Python 3 and Django 1.8 (at least).


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


Update search indexes::

    ./manage.py update_index


Use ``elasticsearch_dsl`` to query::

    # articles is a list of an Article instances
    articles = Article.search().query('match', title="Bob's article").execute()



Documentation
-------------
The library is in development, use it carefully, because until stable an API
is a subject to change.


.. |pypi| image:: https://img.shields.io/pypi/v/django-el.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-el
    :alt: pypi

.. |license| image:: https://img.shields.io/github/license/asyncee/django-el.svg?style=flat-square
    :target: https://github.com/asyncee/django-el/blob/master/LICENSE.txt
    :alt: MIT License

.. |python| image:: https://img.shields.io/badge/python-3.x-blue.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-el
    :alt: 3.x
