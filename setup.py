from distutils.core import setup

setup(name='django-stubtools',
      version='0.2',
      author = "Grant Viklund",
      author_email = "gviklund@backcode.com",
      description = ("A set of tools for Django to help 'stub-out' an app quickly."),
      license = "BSD",
      keywords = "django app",
      #homepage = "https://github.com/renderbox/django-stubtools",
      packages=['stubtools'],
      #long_description=read('README'),
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
      ],
)
