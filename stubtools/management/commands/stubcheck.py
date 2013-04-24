import sys
import inspect
import re
import os.path
from django.core.management.base import AppCommand, CommandError
from django.conf import settings
#import ast
#app_path = os.path.join(root_path, app_name)

class Command(AppCommand):
    #args = '<app>'
    help = 'Does a simple check pass to see if the project has a few key things set-up.'
    tab = "    "

    def handle(self, *args, **options):

        checklist = []

        checklist.append( self.path_check() )        # Check for the PROJECT_PATH in settings.py

        # SETTING UP THE SPLIT SETTINGS FILES

        # PRINT REPORT
        for check in checklist:
            print "*" * 30
            check.print_result()


    def path_check(self):

        result = Check("PROJECT_PATH Check")

        try:
            root_path = settings.PROJECT_PATH
            result.success = True
        except:
            project_name = settings.ROOT_URLCONF.split(".")[0]
            result.message.append( "You need to have either a PROJECT_PATH settings variable." )
            result.message.append(  "Add the following to your settings.py:\n" )
            result.message.append(  "import os.path\n" )
            result.message.append(  "PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))" )
            result.message.append(  "if '%s/%s' in PROJECT_PATH:" % (project_name, project_name) )
            result.message.append(  "    PROJECT_PATH = PROJECT_PATH.replace('%s/%s', '%s')" % (project_name, project_name, project_name) )
        
        return result


class Check(object):

    def __init__(self, name, message=[], success=False):
        self.name = name
        self.success = success
        self.message = message

    def print_result(self):
        if self.success:
            print "PASS: %s" % self.name
        else:
            print "FAIL: %s" % self.name

        if self.message:
            print '\n'.join(self.message)


