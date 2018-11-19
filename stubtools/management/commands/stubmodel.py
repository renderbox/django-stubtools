#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-11-19 11:01:50
#--------------------------------------------

import os.path
# import re
# import inspect
import pprint

# from jinja2 import Environment, PackageLoader, select_autoescape
from django.template.loader import get_template

from django.core.management.base import CommandError
from django.db import models
from django.db.models import Model, Field

from stubtools.core import FileAppCommand, underscore_camel_case, import_line_check, class_name, get_all_subclasses, parse_app_input, get_file_lines, split_camel_case
from stubtools.core.prompt import ask_question, ask_yes_no_question, selection_list, horizontal_rule
from stubtools.core.parse import get_import_range, get_classes_and_functions_start, get_classes_and_functions

# Fields that are not really meant to be included in the list of useable Model Fields
EXCLUDED_FIELDS = ['BLANK_CHOICE_DASH', 'Empty', 'Field', 'FieldDoesNotExist', 'NOT_PROVIDED']



class Command(FileAppCommand):
    args = '<app.model_name>'
    help = 'creates stub Templates, Forms and Admin entries for a given model name'
    pp = pprint.PrettyPrinter(indent=4)

    def handle(self, *args, **kwargs):

        # batch process app models
        try:
            for app_model in args:
                app, model, model_class = parse_app_input(app_model)    # Broken out so process's can be chained
                self.process(app, model, model_class)
        except KeyboardInterrupt:
            print("\nExiting...")
            return


    def get_context(self, app, model, model_class, context={}):

        # model_classes = get_all_subclasses(Model, ignore_modules=['django.contrib.contenttypes.models', 'django.contrib.admin.models', 'django.contrib.sessions'])
        model_classes = ['django.db.models.Model', 'django.contrib.auth.models.AbstractUser']
        model_classes.extend([ "%s.%s" % (x.__module__, x.__name__) for x in get_all_subclasses(Model, ignore_modules=['django.contrib.contenttypes.models', 'django.contrib.admin.models', 'django.contrib.sessions', 'django.contrib.auth.base_user', 'django.contrib.auth.models']) ])
        field_classes = [ "%s.%s" % (x.__module__, x.__name__) for x in get_all_subclasses(Field, ignore_modules=["django.contrib.contenttypes"]) ]

        model_class_settings = {}
        # modelclass_settings.update(MODELCLASS_SETTINGS)     # Update the setting dict with defaults
        model_key = selection_list(model_classes, as_string=True, title="Select a Model Class")

        if not model:
            default = "MyModel"
            model = input("What is the name of the model? [%s] > " % default) or default

        # MAKE SURE AT LEAST THE FIRST LETTER OF THE VIEW NAME IS CAPITALIZED
        model = model[0].upper() + model[1:]

        model_name = "_".join(split_camel_case(model)).lower()

        render_ctx = {'app':app, 'model_key':model_key, 'model':model, 'model_name':model_name, 'attributes':[],
                        'model_header':"", 'model_import_statement':"", 'model_body':"", 'model_footer':"", 'create_model':True }

        if context:
            print(context)
            render_ctx.update(context)

        # Creating a model can create a cascade of views that are needed
        render_ctx['create_model_admin'] = ask_yes_no_question("Create an Admin Entry?", default=True, required=True)
        render_ctx['create_model_form'] = ask_yes_no_question("Create a matching Model Form?", default=True, required=True)
        render_ctx['create_model_views'] = ask_yes_no_question("Create a Matching Model Views?", default=True, required=True)

        if render_ctx['create_model_views']:
            render_ctx['create_model_detail'] = ask_yes_no_question("Create a Model Detail View?", default=True, required=True)
        #     render_ctx['create_model_list'] = ask_yes_no_question("Create a Model List View?", default=True, required=True)
        #     render_ctx['create_model_create'] = ask_yes_no_question("Create a Model Create View?", default=render_ctx['create_model_form'], required=True)
        #     render_ctx['create_model_edit'] = ask_yes_no_question("Create a Model Edit View?", default=render_ctx['create_model_form'], required=True)
        #     render_ctx['create_model_delete'] = ask_yes_no_question("Create a Model Delete View?", default=True, required=True)

        # In this case, load the other commands and give them settings

        # REST APIs?

        # Need to replace this with a settings file
        if render_ctx['model_key'] == "django.db.models.Model":
            render_ctx['model_class_module'] = "django.db"
            render_ctx['model_class'] = "models.Model"
            render_ctx['model_class_import'] = "models"
        else:
            render_ctx['model_class_module'] = ".".join( render_ctx['model_key'].split(".")[:-1] )
            render_ctx['model_class'] = render_ctx['model_key'].split(".")[-1]
            render_ctx['model_class_import'] = render_ctx['model_class']

        if not render_ctx['attributes']:
            render_ctx['attributes'] = [{'field_name':'name', 'field_type':"models.CharField", 'field_kwargs':{ 'blank':False }}]

        return render_ctx

    def process(self, app, model, model_class, context={}):

        model_file = os.path.join(app, "models.py")

        print("MODEL FILE: %s" % model_file)
        print("CONTEXT")
        print(context)

        render_ctx = self.get_context(app, model, model_class, context=context)

        # #######################
        # # PARSE models.py
        # #######################

        # Slice and Dice!
        data_lines = get_file_lines(model_file)
        line_count = len(data_lines)
        structure = self.parse_code("".join(data_lines))

        # print( horizontal_rule() )
        # print("FILE STRUCTURE (%s):" % model_file)
        # self.pp.pprint(structure)

        # check to see if the model is already in models.py
        if render_ctx['model'] in structure['class_list']:
            print("%s model already in '%s', skipping creation" % (render_ctx['model'], model_file))
            render_ctx['create_model'] = False
        else:
            print(model)
            print(structure['class_list'])

        # Establish the Segments
        if structure['first_import_line']:
            # import_start_index = structure['first_import_line'] - 1
            body_start_index = structure['last_import_line']
            header_end_index = body_start_index
        else:
            # import_start_index = 0
            body_start_index = 0
            header_end_index = body_start_index

        if structure['first_code_line']:
            body_end_index = structure['last_code_line']      # Get the last line of code as an index value
        else:
            body_end_index = body_start_index + 1

        footer_start_index = body_end_index

        modules = []        # List of other modules being loaded
        comment = None

        # Check to see if the needed 'from' module is already being loaded.  If so, adjust where the header ends and the body starts
        if render_ctx['model_class_module'] in structure['from_list']:
            i = structure['from_list'].index(render_ctx['model_class_module'])
            import_info = structure['imports'][i]
            modules = import_info['import']
            import_lineno = import_info['first_line']
            header_end_index = import_lineno - 1
            body_start_index = import_lineno

        # Segment Values
        render_ctx['model_import_statement'] = self.create_import_line(render_ctx['model_class_import'], path=render_ctx['model_class_module'], modules=modules, comment=comment)
        render_ctx['model_header'] = "".join(data_lines[:header_end_index])         # In between the first line and the module import
        render_ctx['model_body'] = "".join(data_lines[body_start_index:body_end_index])      # between the import line and where the model needs to be added
        render_ctx['model_footer'] = "".join(data_lines[footer_start_index:])         # after the model code

        #######################
        # RENDER THE TEMPLATES
        #######################

        # print( horizontal_rule() )
        # print("RENDER CONTEXT:")
        # self.pp.pprint(render_ctx)

        model_template = get_template('stubtools/stubmodel/model.py.j2', using='jinja2')
        model_result = model_template.render(context=render_ctx)

        if render_ctx['create_model']:
            self.write_file(model_file, model_result)
        # else:
        #     print( horizontal_rule() )
        #     print("models.py RESULT:")
        #     print(model_result)

        # This lets the uer create new views to match

        if render_ctx['create_model_views']:
            from stubtools.management.commands.stubview import Command as ViewCommand

            if render_ctx['create_model_detail']:
                vc = ViewCommand()
                # app_args = '.'.join([app, render_ctx['model_name'], "DetailView"])
                print("APP ARGS: creating a '%s' for model '%s' in app '%s'" % ("DetailView", app, render_ctx['model_name']) )
                vc.process(app, render_ctx['model_name'], "DetailView")

