import sys
import inspect
import re
import os.path
from django.core.management.base import CommandError
from django.conf import settings
#import ast
from stubtools.core import StubRootCommand

class Command(StubRootCommand):
    #args = '<app>'
    help = 'sets-up boilerplate django files and directories if missing from a given project.'
    tab = "    "

    def handle(self, *args, **options):
        super(Command, self).handle()

        if len(args) < 1:
            raise CommandError('Need to pass App names')

        app_name = args[0]
        app_path = os.path.join(root_path, app_name)


    def get_models(self, app_name, app_path):

        models = []
        comment = ""

        try:
            classes = inspect.getmembers(sys.modules["%s.models" % app_name], inspect.isclass)  # COULD ALSO ADD CHECK TO SEE IF IT IS A DJANO MODEL CLASS
        except KeyError:
            print "\'%s\'' app is not included in your installed apps, please include it and run again." % app_name
            return comment, models

        for cl in classes:
            if cl[1].__module__ == "%s.models" % app_name:
                models.append(cl[0])

        if not models:
            models = ['ExampleModel']
            comment = "#"

        return comment, models


