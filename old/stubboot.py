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

        result = self.checkInput("Do you want to get Twitter Bootstrap?")
        if result == "y":
            if not len(settings.STATICFILES_DIRS):
                print "\tERROR: NO STATIC FILE DIRECOTRIES FOUND!\n\tAdd this to your config:\n"
                print "STATICFILES_DIRS = (\n    os.path.join(BASE_DIR, 'static'),\n)\n"
                return

            self.getTwitterBootstrap()


    def loadTemplateLines(self, path):
        SRC = open(path, 'r')
        lines = SRC.readlines()
        SRC.close()
        return lines


    def getTwitterBootstrap(self):
        url = "http://twitter.github.io/bootstrap/assets/bootstrap.zip"

        # SETUP THE DESTINATION PATH
        tmpdir = os.path.join(settings.BASE_DIR, "_tmp")
        tmpfile = os.path.join(settings.BASE_DIR, "_tmp", url.split("/")[-1])

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

