import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


# Some initialization
here = os.path.abspath(os.path.dirname(__file__))
long_description = open(os.path.join(here, 'README.rst')).read()


data_files = []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)


# this code snippet is taken from django-registration setup.py script
for dirpath, dirnames, filenames in os.walk('el'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if filenames:
        prefix = dirpath[len('el')+1:] # Strip "el/" or "el\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)


setup(
    name="django-el",
    version="0.2",
    packages=find_packages(),
    author="asyncee",
    description="Django elasticsearch integration.",
    long_description=long_description,
    license="MIT",
    keywords="django elasticsearch",
    url='https://github.com/asyncee/django-el',
    download_url='https://pypi.python.org/pypi/django-el/',
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
    ],

    package_dir={'el': 'el'},
    package_data={'el': data_files},
    zip_safe=False,

    tests_require=['tox'],
    cmdclass={'test': Tox},
)
