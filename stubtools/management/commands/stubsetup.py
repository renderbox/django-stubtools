import sys
import inspect
import re
import os.path
from django.core.management.base import AppCommand, CommandError
from django.conf import settings
#import ast
from stubtools.core import StubRootCommand

class Command(StubRootCommand):
    help = 'sets-up folder structure for django files and directories if missing from a given project.'
    tab = "    "


    def handle(self, *args, **options):
        super(Command, self).handle()
        self.process()


    def process(self):
        self.splitConfigSetup()
        self.templatePathSetup()
        self.staticPathSetup()

    def splitConfigSetup(self):
        '''
        This sets up the split config that works really well for deployments.  It seperates
        the different deployment options and allows you to override different config settings
        depending on deployment.
        '''
        print "CHECKING FOR DIVIDED SETTINGS"

        project_name = settings.ROOT_URLCONF.split(".")[0]
        settings_file = os.path.join(settings.PROJECT_PATH, project_name, "settings.py")
        if not os.path.isfile( settings_file ):
            print "\tYOU ARE USING A SPLIT CONFIG!"
        else:
            print "\tYOU ARE USING A SINGLE CONFIG FILE, LETS BREAK THAT UP."

        settings_dir = os.path.join(settings.PROJECT_PATH, project_name, "settings")

        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)

        settings_init_file = os.path.join(settings_dir, "__init__.py")

        if not os.path.exists(settings_init_file):  # STUB OUT THE BLANK init FILE
            open(settings_init_file, 'w').close()

        settings_file_c = settings_file + "c"
        if os.path.exists(settings_file_c):
            os.remove(settings_file_c)

        # CHECK FOR THE settings.py AND MOVE IT INTO THE DIRECTORY IF NEEDED
        new_settings_file = os.path.join(settings_dir, "base.py")
        if os.path.exists(settings_file) and not os.path.exists(new_settings_file):
            os.rename(settings_file, new_settings_file)

        # CREATE THE DEV FILE
        dev_settings_file = os.path.join(settings_dir, "dev.py")
        if not os.path.exists(dev_settings_file):
            FILE = open(dev_settings_file, 'w')

            lines = ["from base import *"]

            lines.append("\n# DATABASES = {")
            lines.append("#     'default': {")
            lines.append("#         'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.")
            lines.append("#         'NAME': 'database.sqlite',                      # Or path to database file if using sqlite3.")
            lines.append("#         'USER': '',                      # Not used with sqlite3.")
            lines.append("#         'PASSWORD': '',                  # Not used with sqlite3.")
            lines.append("#         'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.")
            lines.append("#         'PORT': '',                      # Set to empty string for default. Not used with sqlite3.")
            lines.append("#     }")
            lines.append("# }")

            lines.append("\nDEV_ONLY_APPS = (")
            lines.append("#     'debug_toolbar',")
            lines.append(")")

            lines.append("\nINSTALLED_APPS = DEV_ONLY_APPS + INSTALLED_APPS")
            lines.append("\n# MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)")
            lines.append("\n# INTERNAL_IPS = ('127.0.0.1',)")

            lines.append("\nDEBUG_TOOLBAR_CONFIG = {")
            lines.append("    'INTERCEPT_REDIRECTS': False,")
            lines.append("    'SHOW_TEMPLATE_CONTEXT': True,")
            lines.append("}\n\n")

            FILE.writelines("\n".join(lines))
            FILE.close()

        # CREATE THE PRODUCTION SERVER FILE
        dev_settings_file = os.path.join(settings_dir, "production.py")
        if not os.path.exists(dev_settings_file):
            FILE = open(dev_settings_file, 'w')

            lines = ["from base import *"]

            lines.append("\n# DATABASES = {")
            lines.append("#     'default': {")
            lines.append("#         'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.")
            lines.append("#         'NAME': 'database.sqlite',                      # Or path to database file if using sqlite3.")
            lines.append("#         'USER': '',                      # Not used with sqlite3.")
            lines.append("#         'PASSWORD': '',                  # Not used with sqlite3.")
            lines.append("#         'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.")
            lines.append("#         'PORT': '',                      # Set to empty string for default. Not used with sqlite3.")
            lines.append("#     }")
            lines.append("# }")

            lines.append("\nPRODUCTION_ONLY_APPS = (")
            lines.append(")")

            lines.append("\nINSTALLED_APPS = PRODUCTION_ONLY_APPS + INSTALLED_APPS")

            lines.append("\n########## STORAGE CONFIGURATION")
            lines.append("# INSTALLED_APPS += ('storages', )")
            lines.append("\n# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'")
            lines.append("# STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'")
            lines.append("\n# AWS_QUERYSTRING_AUTH = False")
            lines.append("\n# AWS_HEADERS = {")
            lines.append("#     'Expires': 'Thu, 15 Apr 2020 20:00:00 GMT',")
            lines.append("#     'Cache-Control': 'max-age=86400',")
            lines.append("# }")
            lines.append("\n# #Boto requires subdomain formatting.")
            lines.append("# from S3 import CallingFormat")
            lines.append("# AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN")
            lines.append("\n# Amazon S3 configuration.")
            lines.append("# if 'AWS_ACCESS_KEY_ID' in os.environ:")
            lines.append("#     AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']")
            lines.append("# else:")
            lines.append("#     raise Exception('Missing AWS_ACCESS_KEY_ID')")
            lines.append("\n# if 'AWS_SECRET_ACCESS_KEY' in os.environ:")
            lines.append("#     AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']")
            lines.append("# else:")
            lines.append("#     raise Exception('Missing AWS_SECRET_ACCESS_KEY')")
            lines.append("\n# AWS_STORAGE_BUCKET_NAME = 'bevlog'")
            lines.append("\n# STATIC_URL = 'https://s3.amazonaws.com/bevlog/'")
            lines.append("# MEDIA_URL = STATIC_URL")
            lines.append("########## END STORAGE CONFIGURATION\n\n")

            FILE.writelines("\n".join(lines))
            FILE.close()


    def templatePathSetup(self):
        print "\nCHECKING FOR TEMPLATE PATH"

        if not len(settings.TEMPLATE_DIRS):
            print "\tERROR: NO TEMPLATE FILE DIRECOTRIES FOUND!\n\tAdd something like this to your config:\n"
            print "TEMPLATE_DIRS = ("
            print "\tos.path.join(PROJECT_PATH, 'templates'),"
            print ")\n"
            return

        for directory in settings.TEMPLATE_DIRS:
            if not os.path.exists(directory):
                print "\t\tMAKING %s" % directory
                os.makedirs(directory)
            else:
                print "\tDirectory Exists: %s" % directory


    def staticPathSetup(self):
        print "\nCHECKING FOR STATIC PATHS"

        if not len(settings.STATICFILES_DIRS):
            print "\tERROR: NO STATIC FILE DIRECOTRIES FOUND!\n\tAdd something like this to your config:\n"
            print "STATICFILES_DIRS = ("
            print "\tos.path.join(PROJECT_PATH, 'static'),"
            print ")\n"
            return

        if len(settings.STATICFILES_DIRS) == 1:
            for sub in ['css','js','img']:
                directory = os.path.join(settings.STATICFILES_DIRS[0], sub)  
                if not os.path.exists(directory):
                    print "\t\tMAKING %s" % directory
                    os.makedirs(directory)
                else:
                    print "\tDirectory Exists: %s" % directory






