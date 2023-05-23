#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-12-21 15:47:12
#--------------------------------------------
import re, os.path
import ast
import pprint
import logging
import importlib

from django.core.management.base import AppCommand
from django.conf import settings

from stubtools.core.astparse import ast_parse_code
from stubtools.core.file import PythonFileParser
from stubtools.core.prompt import horizontal_rule

import django

from django.template.loader import get_template

# Compiled REGEX Patterns
name_split_regex = re.compile("([A-Z][a-z]+)")


def get_file_lines(file_name):
    if os.path.isfile( file_name ):
        FILE = open( file_name, "r")
        data_lines = FILE.readlines()
        FILE.close()
        return data_lines
    return []

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

# todo: Fix an issue where Models that are joined through a ManyToMany, ForeignKey fields are returned as well.
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


#############
# Base Class
#############

class FileAppCommand(AppCommand):

    pp = pprint.PrettyPrinter(indent=4)
    debug = False       # Should move this to the logger
    write_files = True
    logger = logging.getLogger(__name__)
    structure = {}

    def add_arguments(self, parser):
        parser.add_argument(
            '--toscreen',
            action='store_true',
            dest='toscreen',
            help='Prints results to screen instead of writing to files',
        )

    def write_file(self, file_path, data, create_path=True):
        full_path = os.path.abspath(file_path)          # Make it a full path to reduce issues in parsing direcotry from file
        file_directory = os.path.dirname(full_path)

        # Check the directory exists
        if not os.path.exists(file_directory):
            # Create the full path if needed
            os.makedirs(file_directory)

        FILE = open(full_path, "w")
        FILE.write(data)
        FILE.close()

    def load_file(self, file_path):
        self.parser = PythonFileParser(file_path)

    def sliced_ctx(self, file_path, new_class, template=None, extra_ctx={}, modules=[], filters=[]):
        if not os.path.isfile(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            FILE = open(file_path, "w")
            FILE.write("")
            FILE.close()

        parser = PythonFileParser(file_path)

        ctx = {}
        ctx.update(extra_ctx)
        ctx['add_class'] = True

        if new_class in parser.structure['class_list']:
            print("** %s form already in '%s', skipping creation..." % (new_class, file_path))
            ctx['add_class'] = False

        ctx['header'] = parser.new_get_header()     # Everything before the first import line
        ctx['body'] = parser.new_get_body()         # Everything between the last import line and the last code line
        ctx['footer'] = parser.get_footer()         # Everything after the last code line
        ctx['import_statements'] = parser.get_import_block(modules=modules)

        for ctx_filter in filters:
            ctx = ctx_filter(ctx, parser)

        return ctx

    def write_template(self, ctx, path, template, toscreen=False):
        renderer = self.get_template(template)
        result = renderer.render(context=ctx)

        if toscreen:
            print("\n")
            print( horizontal_rule() )
            print("%s RESULT:" % path)
            print( horizontal_rule() )
            print(result)
        else:
            self.write_file(path, result)


    def write(self, file_path, new_class, template=None, extra_ctx={}, modules=[], filters=[], toscreen=False):
        ctx = self.sliced_ctx(file_path, new_class, template=template, extra_ctx=extra_ctx, modules=modules, filters=filters)
        self.write_template(ctx, file_path, template)
        print("Wrote File: \"%s\"" % file_path)


    def create_import_line(self, module, path=None, modules=[], comment=None, sort=False):
        mod_list = []                   # Start with just the required
        mod_list.extend(modules)        # Add the other modules to the list

        if module not in mod_list:
            mod_list.append(module)

        if sort:
            mod_list.sort()             # Sort the modules

        if path:
            result = "from %s import %s" % ( path, ", ".join(mod_list) )
        else:
            result = "import %s" % ( ", ".join(mod_list) )

        if comment:
            result += "    # %s" % comment

        return result


    def get_class_settings(self, root_class, ignore_modules=[], settings={}):

        classes = get_all_subclasses(root_class, ignore_modules=ignore_modules)

        result = {}
        result.update(settings)

        for cl in classes:
            class_name = cl.__name__    # Get the short name for the class
            view_key = cl.__module__ + "." + class_name

            if view_key not in result:
                result[view_key] = {}

            if not 'module' in result[view_key]:                 # Only if not specified already in the settings
                result[view_key]['module'] = cl.__module__       # Set the module to the full import path

            if not 'class_name' in result[view_key]:             # Only if not specified already in the settings
                result[view_key]['class_name'] = class_name      # Set the module to the full import path

        return result


    def get_app_models(self, app):
        model_file = "%s/models.py" % app

        model_file_parser = PythonFileParser(model_file)

        result = [x['name'] for x in model_file_parser.structure['classes'] if 'models.Model' in x['inheritence_chain'] ]

        return result


    def get_model_fields(self, app, model):

        model_mod = importlib.import_module('%s.models' % app)
        Model = getattr(model_mod, model) 

        return [f.name for f in Model._meta.get_fields()]


    def get_template(self, path, using='jinja2'):
        return get_template(path, using=using)

