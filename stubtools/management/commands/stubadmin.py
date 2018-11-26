#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-11-26 10:32:39
#--------------------------------------------

import os.path
import re
import inspect

from jinja2 import Environment, PackageLoader, select_autoescape

from django.core.management.base import CommandError
from django.template.loader import get_template

from stubtools.core import FileAppCommand, parse_app_input
from stubtools.core.search import get_first_index, get_last_index, get_first_and_last_index
from stubtools.core.file import write_file
from stubtools.core.prompt import horizontal_rule, selection_list


class Command(FileAppCommand):
    args = '<app.model_name>'
    help = 'creates the admin setup for a model class'
    # class_regex = re.compile(r"class (\w+)\(.+\):")
    # import_line_regex = re.compile(r"^from django.contrib import (.+)", re.MULTILINE)
    # model_import_line_regex = re.compile(r"^from .models import (.+)", re.MULTILINE)
    # imports_regex = re.compile(r"(import|from)")
    # func_regex = re.compile(r"(def|class)")
    # admin_site_register_regex = re.compile(r"admin.site.register")
    debug = True


    def handle(self, *args, **options):

        app = None
        model = None

        try:
            for app_view in args:
                app, view, trash = parse_app_input(app_view)
                self.process(app, view)
        except KeyboardInterrupt:
            print("\nExiting...")
            return

        # for entry in args:

        #     try:
        #         app, model = entry.split(".")
        #         self.process(app, model)

        #     except ValueError:
        #         app = entry
        #         models = input("Which model(s) did you want to work on in the app \"%s\"? (Model Model ...) > " % app)  # todo: replace with selection prompt

        #         for model in models.split():
        #             self.process(app, model)

    def get_context(self, app, model, app_models=None, **kwargs):

        if model == None:       # If not model is provided, ask which one to work with
            model = selection_list(app_models, "Pick a model to create a Admin interface for.", as_string=True)

        model_admin = model + "Admin"

        model_list = [model]

        result = { 'header':"", 'pre_admin':"", 'pre_registration':"", 'footer':"",'model':model, 
                    'model_admin':model_admin, 'admin_import':"",
                    'create_model_admin':True, 'model_class_import_statement':"",
                    'model_class_module':".models"}

        # Update the import line to include any missing model classes
        model_list.extend(app_models)
        model_list = list(set(model_list))
        model_list.sort()

        result['model_class_imports'] = ", ".join(model_list)

        return result


    def process(self, app, model, **kwargs):
        model_file = "%s/models.py" % app
        admin_file = "%s/admin.py" % app

        print("ADMIN FILE: %s" % admin_file)

        import_line = False
        import_entry = False
        first_class_line = 0
        last_import_line = 0
        app_models = []

        if not model:
            model_file_lines = self.load_file(model_file)
            model_file_structure = self.parse_code("".join(model_file_lines))
    
            # Pass in a list of available models from models.py
            app_models = [x['name'] for x in model_file_structure['classes'] if 'models.Model' in x['inheritence_chain'] ]

        self.render_ctx = self.get_context(app, model, app_models=app_models, **kwargs)

        admin_file_lines = self.load_file(admin_file)
        self.structure = self.parse_code("".join(admin_file_lines))


        #######################
        # PARSE admin.py
        #######################

        if self.debug:
            print( horizontal_rule() )
            print("FILE STRUCTURE:")
            self.pp.pprint(self.structure)

        modules = []
        comment = ""

        last_file_line = len(admin_file_lines)

        class_start_line = self.structure['first_class_line']
        class_end_line = self.structure['last_class_line']

        body_start_index = self.structure['last_import_line'] + 1
        header_end_index = self.structure['last_import_line']

        # if self.structure['first_import_line']:
        #     body_start_index = self.structure['last_import_line']
        #     header_end_index = body_start_index
        # else:
        #     body_start_index = 0
        #     header_end_index = body_start_index

        if self.structure['first_code_line']:
            body_end_index = self.structure['last_code_line']      # Get the last line of code as an index value
        else:
            body_end_index = body_start_index + 1

        if self.structure['last_line']:
            footer_start_index = self.structure['last_line'] + 1
        else:
            footer_start_index = self.structure['last_line']

        # Figure out the import line...
        import_line = self.get_import_line(".models")               # Check to see if this is imported
        admin_import_line = self.get_import_line("django.contrib")  # Does a check to see if the line is already included or not

        if import_line != None:     # Check to see if there is an import line or not
            import_info = self.get_module_import_info(self.render_ctx['model_class_module'])
            modules = import_info['import']     # Get the other modules already imported
            import_lineno = import_info['first_line']
            header_end_index = import_lineno    # Modify the slicing to adjust for the import line.
            body_start_index = import_lineno

        #######
        # SORTING SLICE POINTS

        if header_end_index:
            print("Header Line Index: 0-%d" % (header_end_index) )
        else:
            print("Header Line Index: No Header")

        # if self.structure['first_import_line'] == None:
        #     print("IMPORT LINES: None")
        # else:
        #     print("IMPORT LINES: %d-%d" % (self.structure['first_import_line'], self.structure['last_import_line']) )

        # Import line can be None
        if admin_import_line == None:
            print("ADMIN IMPORT INDEX: None")
        else:
            print("ADMIN IMPORT INDEX: %d" % (admin_import_line) )

        # # Import line can be None
        # if import_line == None:
        #     print("IMPORT LINE: None")
        # else:
        #     print("IMPORT LINE: %d" % (import_line) )

        # if class_start_line == class_end_line and class_start_line == None:
        #     print("CLASS RANGE: None")
        # else:
        #     print("CLASS RANGE: %d-%d" % (class_start_line, class_end_line) )

        # # Insert Registration at the end of the body
        # print("BODY INDEX RANGE: %d-%d" % (body_start_index, body_end_index) )

        # if footer_start_index:
        #     print("FOOTER INDEX START: %d" % (footer_start_index) )
        # else:
        #     print("FOOTER INDEX START: None")

        #########
        # SLICING
        self.render_ctx['admin_header'] = "".join(admin_file_lines[:header_end_index]).strip()

        if footer_start_index:
            self.render_ctx['admin_footer'] = "".join(admin_file_lines[footer_start_index:])
        else:
            self.render_ctx['admin_footer'] = ""

        # self.render_ctx['pre_admin'] = "".join(admin_file_lines[:header_end])
        # self.render_ctx['pre_register'] = "".join(admin_file_lines[:header_end])

        self.render_ctx['model_class_import_statement'] = self.create_import_line(self.render_ctx['model'], path=self.render_ctx['model_class_module'], modules=modules, comment=comment)

        if admin_import_line == None:
            # if it's not there, prepend the admin import
            self.render_ctx['model_class_import_statement'] = "from django.contrib import admin\n" + self.render_ctx['model_class_import_statement']

        if self.render_ctx['model_admin'] in self.structure['class_list']:
            print("** %s admin already in '%s', skipping creation..." % (self.render_ctx['model_admin'], admin_file))
            self.render_ctx['create_model_admin'] = False


        #######################
        # RENDER THE TEMPLATES
        #######################

        if self.debug:
            print( horizontal_rule() )
            print("RENDER CONTEXT:")
            self.pp.pprint(self.render_ctx)
            print( horizontal_rule() )

        admin_template = get_template('stubtools/stubadmin/admin.py.j2', using='jinja2')
        admin_result = admin_template.render(context=self.render_ctx)


        # if self.debug:
        #     print( horizontal_rule() )
        #     print("admin.py RESULT:")
        #     print( horizontal_rule() )
        #     print(admin_result)

        # if self.write_files:
        #     self.write_file(admin_file, admin_result)


    def get_module_import_info(self, module):
        i = self.structure['from_list'].index(module)
        result = self.structure['imports'][i]
        return result


    def get_header(self):
        pass


"""
SAMPLE:


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


###############
# ACTIONS
###############

def enable_selected(modeladmin, request, queryset):
    queryset.update(enabled=True)


def disable_selected(modeladmin, request, queryset):
    queryset.update(enabled=False)


def reset_slug(modeladmin, request, queryset):
    '''
    Given a query set of Students, reset their progress.
    '''

    print( "SLUG RESET CALLED BY: %s" % (request.user.email) )

    for item in queryset:
        item.slug = None
        item.save()


admin.site.register(User, UserAdmin)
"""



        # # LOOK FOR CLASS WITH NAME
        # if model_admin in classes:
        #     print('%s Admin Interface Exists, Skipping.' % model_admin)
        #     return

        # 'pre_' naming convention: any line before that part of the template is added

        # Slice and Dice the admin.py here
        # data_lines = data.split("\n")
        # line_count = len(data_lines)



        # Find the parts of the file to slice

        # Check that the admin module is loaded
        # render_ctx['admin_import'] = self.import_line_regex.findall( data )
        
        # Set the insert lines to be the length of the doc.  This way if things are missing, they will just be appended to the end of the file.
        # admin_import_line = line_count
        # model_import_line = line_count
        # model_admin_class_end = line_count
        # admin_registry_start = line_count
        # admin_registry_end = line_count
        # footer_start = line_count

        # # See if the Admin module is loaded
        # admin_import_line = get_first_index(data_lines, self.import_line_regex)

        # # Model Import Line
        # for c, line in enumerate(data_lines):
        #     check = self.model_import_line_regex.findall( line )

        #     if check:
        #         model_import_line = c       # Make note of the line number
        #         render_ctx['models'].extend(check)  # Add the models to the list
        #         break

        # render_ctx['models'] = list(set(render_ctx['models']))  # Remove any duplicates
        # render_ctx['models'].sort()

        # # Admin Registration
        # admin_registry_start, admin_registry_end = get_first_and_last_index(data_lines, self.admin_site_register_regex)

        # # Model Admin
        # # Find the registries first to reduce the search range for the Model Admins
        # model_admin_class_end = get_last_index(data_lines, self.func_regex)

        # # Take the last model admin line and find the break between it and the registry line
        # for c, line in enumerate(data_lines[model_admin_class_end:admin_registry_start]):
        #     if line:
        #         model_admin_class_end = c + model_admin_class_end
        #     else:
        #         break

        # # Slice the existing admin.py into parts
        # if 0 < model_import_line:
        #     render_ctx['pre_import'] = "\n".join(data_lines[0:model_import_line] )    # Everything up until the model import line

        # if model_import_line < model_admin_class_end:
        #     render_ctx['pre_admin'] = "\n".join(data_lines[(model_import_line + 1):(model_admin_class_end + 1)] )    # Everything up until the model import line

        # # pre_registration
        # if model_admin_class_end < admin_registry_end:
        #     render_ctx['pre_registration'] = "\n".join(data_lines[(model_admin_class_end + 1):(admin_registry_end + 1)] )    # Everything up until the model import line

        # # FOOTER
        # if admin_registry_end < line_count:
        #     render_ctx['post_registration'] = "\n".join(data_lines[(admin_registry_end + 1):line_count] )    # Everything up until the model import line

        # # Print out the results to the terminal, add as an option?
        # admin_template = get_template('stubtools/stubadmin/admin.py.j2', using='jinja2')
        # admin_result = admin_template.render(context=render_ctx)

        # write_file(admin_file, admin_result)

