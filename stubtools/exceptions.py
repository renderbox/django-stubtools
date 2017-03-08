# EXCEPTIONS

class NoProjectPathException(Exception):
    def __init__(self, message):

        project_name = message
        result = []

        result.append( "You need to have a BASE_DIR settings variable." )
        result.append( "Add the following to your settings.py:\n" )
        result.append( "import os.path\n" )
        result.append( "BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))" )
        result.append( "if '%s/%s' in BASE_DIR:" % (project_name, project_name) )
        result.append( "    BASE_DIR = BASE_DIR.replace('%s/%s', '%s')" % (project_name, project_name, project_name) )

        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, '\n'.join(result) )
