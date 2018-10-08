from os import path

from setuptools import setup
from setuptools import find_packages

PACKAGE_ROOT = path.abspath(path.dirname(__file__))

def load_description(file_path, file_name):
    description = ''
    with open(path.join(file_path, file_name), encoding='utf-8') as f:
        description = f.read()
    return description

data = {
    'name': 'django-stubtools',
    'version': '0.8.0',
    'description': "A set of tools for Django to help 'stub-out' an project quickly.",
    'long_description': load_description(PACKAGE_ROOT, 'README.md'),
    'license': 'BSD',
    'classifiers': [
          "Development Status :: 4 - Beta",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3"
    ],
    'keywords': ['django', 'app'],
    'url': 'http://github.com/renderbox/django-stubtools',
    'author': 'Grant Viklund',
    'author_email': 'renderbox@gmail.com',
    'maintainer': 'Grant Viklund',
    'maintainer_email': 'renderbox@gmail.com',
    'packages': ['stubtools', 'stubtools.core', 'stubtools.management', 'stubtools.management.commands', 'stubtools.tests', 'stubtools.templates'],
    'package_data': {'stubtools.templates': ['*.j2', '*.txt']},
    'python_requires': '>=2.7.0',
    'install_requires': ["Django>=2.0.0", "Jinja2==2.10"],
    'extras_require': {
        'dev': [],
        'docs': ["Sphinx==1.7.5", "coverage==4.5.1"],
        'test': ["pytest==3.6.1", "coverage==4.5.1"],
    },
    'entry_points': {
        'console_scripts': ['mayapm=mayapm.cmd:main'],
    }
}

setup(**data)