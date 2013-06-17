import sys
import inspect
import re
import os.path
import urllib
import zipfile
import shutil

from django.core.management.base import AppCommand, CommandError
from django.conf import settings
#import ast
from stubtools.core import StubRootCommand
import stubtools

class Command(StubRootCommand):
    help = 'sets-up folder structure for django files and directories if missing from a given project.'
    tab = "    "

    def handle(self, *args, **options):
        super(Command, self).handle()
        self.process()

    def checkInput(self, question, default="n", choices=["y","n"]):

        tags = []

        for x in choices:
            if x == default:
                tags.append(x.upper())
            else:
                tags.append(x)

        tag = "[" + "/".join(tags) + "]"

        result = raw_input(question + " " + tag)
        result = result.lower()

        if result == "":
            result = default

        if result in choices:
            return result

        return self.checkInput(question, default=default, choices=choices)  # Ask the question again if the choice is incorrect

    def process(self):

        result = self.checkInput("Do you want to set-up a split config?")
        if result == "y":
            self.splitConfigSetup()

        result = self.checkInput("Do you want to set-up tempalte paths?")
        if result == "y":
            self.templatePathSetup()

        result = self.checkInput("Do you want to set-up static paths?")
        if result == "y":
            self.staticPathSetup()

        result = self.checkInput("Do you want to get Twitter Bootstrap?")
        if result == "y":
            self.getTwitterBootstrap()

        result = self.checkInput("Do you want to create a Base html template file?")
        if result == "y":
            self.addBaseHtmlFile()

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
            print "\tConfig File already Split Up!"
            return
        else:
            print "\tSingle Config File detected, let's break that up."

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
            lines = self.loadTemplateLines( os.path.join(stubtools.__path__[0], "templates", "dev_py.txt") )
            FILE.writelines("\n".join(lines))
            FILE.close()

        # CREATE THE PRODUCTION SERVER FILE
        dev_settings_file = os.path.join(settings_dir, "production.py")
        if not os.path.exists(dev_settings_file):
            FILE = open(dev_settings_file, 'w')
            lines = self.loadTemplateLines( os.path.join(stubtools.__path__[0], "templates", "production_py.txt") )
            FILE.writelines("\n".join(lines))
            FILE.close()

    def loadTemplateLines(self, path):
            SRC = open(path, 'r')
            lines = SRC.readlines()
            SRC.close()
            return lines

    def templatePathSetup(self):
        print "\nCHECKING FOR TEMPLATE PATH"

        if not len(settings.TEMPLATE_DIRS):
            print "\tERROR: NO TEMPLATE FILE DIRECOTRIES FOUND!\n\tAdd something like this to your config:\n"
            print "TEMPLATE_DIRS = (\n    os.path.join(PROJECT_PATH, 'templates'),\n)\n"
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
            print "STATICFILES_DIRS = (\n    os.path.join(PROJECT_PATH, 'static'),\n)\n"
            return

        if len(settings.STATICFILES_DIRS) == 1:
            for sub in ['css','js','img']:
                directory = os.path.join(settings.STATICFILES_DIRS[0], sub)  
                if not os.path.exists(directory):
                    print "\t\tMAKING %s" % directory
                    os.makedirs(directory)
                else:
                    print "\tDirectory Exists: %s" % directory


    def getTwitterBootstrap(self):
        url = "http://twitter.github.io/bootstrap/assets/bootstrap.zip"

        # SETUP THE DESTINATION PATH
        tmpdir = os.path.join(settings.PROJECT_PATH, "_tmp")
        tmpfile = os.path.join(settings.PROJECT_PATH, "_tmp", url.split("/")[-1])

        # DOWNLOAD
        print "Downloading '%s' \n\tto '%s'" % (url, tmpfile)
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)
        urllib.urlretrieve(url, tmpfile)
        print "Download Complete"

        # DECOMPRESS
        try:
            z = zipfile.ZipFile(tmpfile)
        except zipfile.error, e:
            print "Bad zipfile (from %r): %s" % (theurl, e)
            return

        z.extractall(tmpdir)
        z.close()
        os.remove(tmpfile)

        # MOVE TO THE RIGHT LOCATIONS
        bsdir = os.path.join(tmpdir, 'bootstrap')
        bsdirlen = len(bsdir) + 1
        staticdir = settings.STATICFILES_DIRS[0]

        # PREPARE THE LIST
        dir_list = []
        cleanup_list = []

        for (path, dirs, files) in os.walk(bsdir):
            cleanup_list.append(path)
            reldir = path[bsdirlen:]
            for f in files:
                dir_list.append(os.path.join(reldir, f))
        
        # print dir_list

        for item in dir_list:
            os.rename(os.path.join(bsdir, item), os.path.join(staticdir, item))

        # NEED TO ADD CLEANUP OF tmp DIRECTORIES
        shutil.rmtree(tmpdir)

    def addBaseHtmlFile(self):
        pass
        # SETUP THE base.html FILE

        base_html_file = os.path.join(settings.TEMPLATE_DIRS[0], "base.html")
        if not os.path.exists(base_html_file):
            FILE = open(base_html_file, 'w')
            lines = self.loadTemplateLines( os.path.join(stubtools.__path__[0], "templates", "base_html.txt") )
            FILE.writelines("\n".join(lines))
            FILE.close()



