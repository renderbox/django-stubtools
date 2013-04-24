# EXCEPTIONS

class NoProjectPathException(Exception):
    def __init__(self, message, name):

    	project_name = message
    	result = []

        result.append( "You need to have either a PROJECT_PATH settings variable." )
        result.append(  "Add the following to your settings.py:\n" )
        result.append(  "import os.path\n" )
        result.append(  "PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))" )
        result.append(  "if '%s/%s' in PROJECT_PATH:" % (project_name, project_name) )
        result.append(  "    PROJECT_PATH = PROJECT_PATH.replace('%s/%s', '%s')" % (project_name, project_name, project_name) )

        result.append( message )

        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, '\n'.join(result) )

        # Now for your custom code...
        #self.Errors = Errors
