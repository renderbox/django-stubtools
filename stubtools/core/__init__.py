import re, os.path
from django.core.management.base import AppCommand
from django.conf import settings
from stubtools.exceptions import NoProjectPathException

def underscore_camel_case(s):
    """Adds spaces to a camel case string.  Failure to space out string returns the original string.
    >>> space_out_camel_case('DMLSServicesOtherBSTextLLC')
    'DMLS Services Other BS Text LLC'
    """

    return re.sub('((?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z]))', '_', s)


def import_line_check(regex, text, module):
    '''
    Using the given regex see if the module is imported in the text
    '''
    imprt = regex.findall( text )

    if imprt:
        for line in imprt:
            check = [ x.strip() for x in line.split(",") ]
            #print check
            if module in check:
                return True

    return False


def class_name(str):
    return str[:1].upper() + str[1:]


class StubRootCommand(AppCommand):
    """This checks to make sure there is a Project Root path in the Config file"""

    def handle(self, *args, **options):
        try:
            root_path = settings.PROJECT_PATH
        except:
            try:
                root_path = settings.PROJECT_ROOT
            except:
                project_name = settings.ROOT_URLCONF.split(".")[0]

                raise NoProjectPathException(project_name)

