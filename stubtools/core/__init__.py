import re, os.path
from django.core.management.base import AppCommand
from django.conf import settings
from stubtools.exceptions import NoProjectPathException
import django

# Compiled REGEX Patterns
name_split_regex = re.compile("([A-Z][a-z]+)")


def parse_app_input(app_view, expected_parts=3):
    parts = app_view.split(".")  # split the app and views
    part_len = len(parts)

    for i in range(part_len, expected_parts):
        parts.append(None)

    return parts[:expected_parts]


def underscore_camel_case(string):
    """Adds spaces to a camel case string.  Failure to space out string returns the original string.
    >>> space_out_camel_case('DMLSServicesOtherBSTextLLC')
    'DMLS Services Other BS Text LLC'
    """

    return re.sub('((?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z]))', '_', string)


def split_camel_case(string):
    return name_split_regex.findall(string)


def import_line_check(regex, text, module):
    '''
    Using the given regex see if the module is imported in the text
    '''
    imprt = regex.findall( text )

    if imprt:
        for line in imprt:
            check = [ x.strip() for x in line.split(",") ]
            if module in check:
                return True

    return False


def class_name(str):
    return str[:1].upper() + str[1:]


class StubRootCommand(AppCommand):
    """This checks to make sure there is a Project Root path in the Config file"""

    def handle(self, *args, **options):
        try:
            root_path = settings.BASE_DIR
        except:
            project_name = settings.ROOT_URLCONF.split(".")[0]

            raise NoProjectPathException(project_name)


def version_check(mode="gte", vcheck="0.0.0"):
    '''
    Checks the production version against the one passed in.  Assumes a
    version number that looks like this: 1.0.0

    5 modes:
        gt -> Greater Than
        gte -> Greater Than or Equal
        lt ->  Less Than
        lte -> Less Than or Equal
        eq -> Equal
    '''

    django_version = [int(x) for x in django.get_version().split(".")]
    check_version = [int(x) for x in vcheck.split(".")]

    # MAKE SURE THE PASSED IN VERSION HAS 3 VALUES
    if len(check_version) < 3:
        check_version.append(0)

    if len(check_version) < 3:
        check_version.append(0)

    # DETERMINE THE CHECK MODES
    if mode == "gt" and django_version > check_version:
        return True

    if mode == "gte" and django_version >= check_version:
        return True

    if mode == "lte" and django_version <= check_version:
        return True

    if mode == "lt" and django_version < check_version:
        return True

    if mode == "eq" and django_version == check_version:
        return True

    return False


def get_all_subclasses(cls, ignore_modules=[]):
    all_subclasses = []
    ignore_list = tuple([ "<class '" + v for v in ignore_modules ])

    for subclass in cls.__subclasses__():
        if ignore_list:
            if not str(subclass).startswith(ignore_list):
                all_subclasses.append(subclass)
        else:
            all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass, ignore_modules=ignore_modules))

    return all_subclasses


def class_path_as_string(cl):
    return  str(cl)[8:-2]



