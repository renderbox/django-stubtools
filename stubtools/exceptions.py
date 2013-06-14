# EXCEPTIONS

class NoProjectPathException(Exception):
    def __init__(self, message):

    	project_name = message
    	result = []

        result.append( "You need to have a PROJECT_PATH settings variable." )
        result.append( "Add the following to your settings.py:\n" )
        result.append( "import os.path\n" )
        result.append( "PROJECT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))" )
        result.append( "if '%s/%s' in PROJECT_PATH:" % (project_name, project_name) )
        result.append( "    PROJECT_PATH = PROJECT_PATH.replace('%s/%s', '%s')" % (project_name, project_name, project_name) )

        #result.append( message )

        # Call the base class constructor with the parameters it needs
        Exception.__init__(self, '\n'.join(result) )

        # Now for your custom code...
        #self.Errors = Errors

        # print "You need to have either a PROJECT_PATH or PROJECT_ROOT settings variable."
        # print "Add the following to your settings.py:\n"
        # print "import os.path\n"
        # print "PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))"
        # print "if '%s/%s' in PROJECT_ROOT:" % (project_name, project_name)

        # print "    PROJECT_ROOT = PROJECT_ROOT.replace('%s/%s', '%s')" % (project_name, project_name, project_name)
        # raise Exception("Missing ")
