from distutils.core import setup

setup(name='django-stubtools',
      version='0.4.5',
      author = "Grant Viklund",
      author_email = "gviklund@backcode.com",
      description = "A set of tools for Django to help 'stub-out' an app quickly.",
      license = "BSD",
      keywords = "django app",
      home_page = "http://github.com/backcode/django-stubtools",
      packages=['stubtools', 'stubtools.core', 'stubtools.management', 'stubtools.management.commands', 'stubtools.tests'],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
      ],
      install_requires=[
          "Django >= 1.4.0",
      ],
)
