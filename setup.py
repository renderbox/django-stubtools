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
    'version': '0.9.0',
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
    'packages': ['stubtools', 'stubtools.core', 'stubtools.management', 'stubtools.management.commands', 'stubtools.tests'],
    'package_data': {'stubtools': ['templates/*.j2', 'templates/*.txt']},
    'python_requires': '>=2.7.0',
    'install_requires': ["Django>=2.0.0", "Jinja2>=2.11.3"],
    'extras_require': {
        'dev': [],
        'docs': ["Sphinx", "coverage"],
        'test': ["pytest", "coverage"],
    },
    'entry_points': {
        'console_scripts': ['mayapm=mayapm.cmd:main'],
    }
}

setup(**data)