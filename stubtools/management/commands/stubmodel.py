#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-12-21 15:40:00
#--------------------------------------------

import os.path

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
    debug = False

    def handle(self, *args, **kwargs):

        try:
            for app_model in args:
                app, model, model_class = parse_app_input(app_model)    # Broken out so process's can be chained
                self.process(app, model, model_class)
        except KeyboardInterrupt:
            print("\nExiting...")
            return


    def get_context(self, app, model, model_class, **kwargs):

        field_classes = [ "%s.%s" % (x.__module__, x.__name__) for x in get_all_subclasses(Field, ignore_modules=["django.contrib.contenttypes"]) ]

        model_classes = ['django.db.models.Model']
        model_classes.extend([ "%s.%s" % (x.__module__, x.__name__) for x in get_all_subclasses(Model, ignore_modules=['django.contrib.contenttypes.models', 'django.contrib.admin.models', 'django.contrib.sessions', 'django.contrib.auth.base_user', 'django.contrib.auth.models', 'allauth']) ])
        model_classes = list(set(model_classes))
        model_classes.sort()
        model_class_settings = {}

        # Make a selection only if there is more than one option
        if len(model_classes) > 1:
            model_key = selection_list(model_classes, as_string=True, title="Select a Model Class")
        else:
            model_key = model_classes[0]

        if not model:   # todo: Move to settings file
            default = "MyModel"
            model = input("What is the name of the model? [%s] > " % default) or default

        # MAKE SURE AT LEAST THE FIRST LETTER OF THE VIEW NAME IS CAPITALIZED
        model = model[0].upper() + model[1:]

        model_name = "_".join(split_camel_case(model)).lower()

        render_ctx = {'app':app, 'model_key':model_key, 'model':model, 'model_name':model_name, 'attributes':[],
                        'header':"", 'import_statement':"", 'body':"", 'footer':"", 'create_model':True }

        if kwargs:
            render_ctx.update(kwargs)

        # Creating a model can create a cascade of views that are needed
        render_ctx['create_model_admin'] = ask_yes_no_question("Create an Admin Entry?", default=True, required=True)
        render_ctx['create_model_form'] = ask_yes_no_question("Create a matching Model Form?", default=True, required=True)
        render_ctx['create_model_views'] = ask_yes_no_question("Create matching Model Views?", default=True, required=True)
        # render_ctx['create_model_api'] = ask_yes_no_question("Create matching Model API?", default=True, required=True)

        if render_ctx['create_model_views']:
            render_ctx['create_model_detail'] = ask_yes_no_question("Create a Model Detail View?", default=True, required=True)
            render_ctx['create_model_list'] = ask_yes_no_question("Create a Model List View?", default=True, required=True)

            # render_ctx['create_model_create'] = ask_yes_no_question("Create a Model Create View?", default=True, required=True)
            # render_ctx['create_model_edit'] = ask_yes_no_question("Create a Model Edit View?", default=True, required=True)
            # render_ctx['create_model_delete'] = ask_yes_no_question("Create a Model Delete View?", default=True, required=True)

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
            render_ctx['attributes'] = [{'field_name':'name', 'field_type':"models.CharField", 'field_kwargs':{ 'max_length':100, 'blank':False }}]

        return render_ctx

    def process(self, app, model, model_class, **kwargs):

        model_file = os.path.join(app, "models.py")
        model_file_template = os.path.join('stubtools', 'stubmodel', "model.py.j2")

        print("MODEL FILE: %s" % model_file)

        if self.debug:
            print("CONTEXT")
            print(kwargs)

        self.render_ctx = self.get_context(app, model, model_class, **kwargs)

        self.load_file(model_file)

        # #######################
        # # PARSE models.py
        # #######################

        if self.debug:
            print( horizontal_rule() )
            print("FILE STRUCTURE:")
            self.pp.pprint(self.parser.structure)

        # # Slice and Dice!
        # data_lines = get_file_lines(model_file)
        # line_count = len(data_lines)
        # self.structure = self.parse_code("".join(data_lines))

        # if self.debug:
        #     print( horizontal_rule() )
        #     print("FILE STRUCTURE (%s):" % model_file)
        #     self.pp.pprint(self.structure)

        # check to see if the model is already in models.py
        if self.render_ctx['model'] in self.parser.structure['class_list']:
            print("** \"%s\" model already in '%s', skipping creation..." % (self.render_ctx['model'], model_file))
            self.render_ctx['create_model'] = False

        # # Establish the Segments
        # if self.structure['first_import_line']:
        #     body_start_index = self.structure['last_import_line']
        #     header_end_index = body_start_index
        # else:
        #     body_start_index = 0
        #     header_end_index = body_start_index

        # if self.structure['first_code_line']:
        #     body_end_index = self.structure['last_code_line']      # Get the last line of code as an index value
        # else:
        #     body_end_index = body_start_index + 1

        # footer_start_index = body_end_index

        # modules = []        # List of other modules being loaded
        # comment = None

        # # Check to see if the needed 'from' module is already being loaded.  If so, adjust where the header ends and the body starts
        # if self.get_import_line(self.render_ctx['model_class_module']):
        #     i = self.structure['from_list'].index(self.render_ctx['model_class_module'])
        #     import_info = self.structure['imports'][i]
        #     modules = import_info['import']
        #     import_lineno = import_info['first_line']
        #     header_end_index = import_lineno - 1
        #     body_start_index = import_lineno

        # Segment Values
        # self.render_ctx['model_import_statement'] = self.create_import_line(self.render_ctx['model_class_import'], path=self.render_ctx['model_class_module'], modules=modules, comment=comment)
        # self.render_ctx['model_header'] = "".join(data_lines[:header_end_index])         # In between the first line and the module import
        # self.render_ctx['model_body'] = "".join(data_lines[body_start_index:body_end_index])      # between the import line and where the model needs to be added
        # self.render_ctx['model_footer'] = "".join(data_lines[footer_start_index:])         # after the model code

        # self.render_ctx['import_statement'] = self.create_import_line(self.render_ctx['model_class_import'], path=self.render_ctx['model_class_module'])
        # self.render_ctx['header'] = self.parser.get_header()
        # self.render_ctx['footer'] = self.parser.get_footer()
        # self.render_ctx['body'] = self.parser.get_body()

        #######################
        # RENDER THE TEMPLATES
        #######################

        if self.debug:
            print( horizontal_rule() )
            print("RENDER CONTEXT:")
            self.pp.pprint(self.render_ctx)

        ####
        # Model
        if self.render_ctx['create_model']:
            self.write(model_file, self.render_ctx['model'], 
                        template=model_file_template,
                        extra_ctx=self.render_ctx, 
                        modules=[ ('django.utils.translation', 'ugettext_lazy'),
                                  ('django.db', 'models') ])

        ####
        # Views
        if self.render_ctx['create_model_views']:
            from stubtools.management.commands.stubview import Command as ViewCommand
            vc = ViewCommand()
            vc.debug = self.debug
            view_kwargs = {}

            if self.render_ctx['create_model_detail']:
                vc.process(app, self.render_ctx['model_name'], "django.views.generic.detail.DetailView", model=self.render_ctx['model'])
                view_kwargs['template_in_app'] = vc.render_ctx['template_in_app']

            if self.render_ctx['create_model_list']:
                vc.process(app, self.render_ctx['model_name'], "django.views.generic.list.ListView", model=self.render_ctx['model'], **view_kwargs)

        if self.render_ctx['create_model_admin']:

            from stubtools.management.commands.stubadmin import Command as AdminCommand
            ac = AdminCommand()
            ac.debug = self.debug
            admin_kwargs = {}

            ac.process(app, self.render_ctx['model'])
