from distutils.core import setup

setup(name='django-stubtools',
      version='0.7.0',
      author = "Grant Viklund",
      author_email = "gviklund@backcode.com",
      description = "A set of tools for Django to help 'stub-out' an app quickly.",
      license = "BSD",
      keywords = "django app",
      home_page = "http://github.com/backcode/django-stubtools",
      packages=['stubtools', 'stubtools.core', 'stubtools.management', 'stubtools.management.commands', 'stubtools.tests', 'stubtools.templates'],
      package_data={'stubtools.templates': ['*.txt']},
      classifiers=[
          "Development Status :: 4 - Beta",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3"
      ],
      install_requires=[
          "Django>=1.9.0",
      ],
)
