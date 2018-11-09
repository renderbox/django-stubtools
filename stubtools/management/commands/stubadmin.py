#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-11-09 13:47:54
#--------------------------------------------

import os.path
import re
import inspect

from jinja2 import Environment, PackageLoader, select_autoescape

from django.core.management.base import AppCommand, CommandError

from stubtools.core.search import get_first_index, get_last_index, get_first_and_last_index
from stubtools.core.file import write_file


class Command(AppCommand):
    args = '<app.model_name>'
    help = 'creates the admin setup for a model class'
    class_regex = re.compile(r"class (\w+)\(.+\):")
    import_line_regex = re.compile(r"^from django.contrib import (.+)", re.MULTILINE)
    model_import_line_regex = re.compile(r"^from .models import (.+)", re.MULTILINE)
    imports_regex = re.compile(r"(import|from)")
    func_regex = re.compile(r"(def|class)")
    admin_site_register_regex = re.compile(r"admin.site.register")


    def handle(self, *args, **options):

        app = None
        model = None

        for entry in args:

            try:
                app, model = entry.split(".")
                self.process(app, model)

            except ValueError:
                app = entry
                models = input("Which model(s) did you want to work on in the app \"%s\"? (Model Model ...) > " % app)  # todo: replace with selection prompt

                for model in models.split():
                    self.process(app, model)


    def process(self, app, model, *args, **kwargs):
        model_file = "%s/models.py" % app
        admin_file = "%s/admin.py" % app
        print("Admin File: %s" % admin_file)

        import_line = False
        import_entry = False
        first_class_line = 0
        last_import_line = 0
        model_admin = model + "Admin"

        # Load models.py to check it's contents
        # This will get a list of possible Admin entries that can be made
        if os.path.isfile( model_file ):
            try:
                FILE = open( model_file, "r")
                model_file_data = FILE.read()
                FILE.close()

                model_classes = self.class_regex.findall( model_file_data )

            except IOError as e:
                pass                    # May need to add something here to handle a file locking issue

        if model not in model_classes:
            if model_classes:
                print('"%s" Not Found in the app\'s models.py.  Possible Model Classes are:' % model)
                for m in model_classes:
                    print('\t%s' % m)
                return
            else:
                print("There are currently no models found in models.py.  You will need to add some.")
                return

        # LOAD FILE
        # Load admin.py to check it's contents
        if os.path.isfile( admin_file ):
            try:
                FILE = open( admin_file, "r")
                data = FILE.read()
                FILE.close()

            except IOError as e:
                pass                    # May need to add something here to handle a file locking issue

        classes = self.class_regex.findall( data )

        # LOOK FOR CLASS WITH NAME
        if model_admin in classes:
            print('%s Admin Interface Exists, Skipping.' % model_admin)
            return

        # 'pre_' naming convention: any line before that part of the template is added
        render_ctx = { 'pre_import':"", 'pre_admin':"", 'pre_registration':"", 'post_registration':"",'model':model, 'models':[model], 'model_admin':model_admin, 'admin_import':"" }

        # Slice and Dice the admin.py here
        data_lines = data.split("\n")
        line_count = len(data_lines)

        # Find the parts of the file to slice

        # Check that the admin module is loaded
        render_ctx['admin_import'] = self.import_line_regex.findall( data )
        
        # Set the insert lines to be the length of the doc.  This way if things are missing, they will just be appended to the end of the file.
        admin_import_line = line_count
        model_import_line = line_count
        model_admin_class_end = line_count
        admin_registry_start = line_count
        admin_registry_end = line_count
        footer_start = line_count

        # See if the Admin module is loaded
        admin_import_line = get_first_index(data_lines, self.import_line_regex)

        # Model Import Line
        for c, line in enumerate(data_lines):
            check = self.model_import_line_regex.findall( line )

            if check:
                model_import_line = c       # Make note of the line number
                render_ctx['models'].extend(check)  # Add the models to the list
                break

        render_ctx['models'] = list(set(render_ctx['models']))  # Remove any duplicates
        render_ctx['models'].sort()

        # Admin Registration
        admin_registry_start, admin_registry_end = get_first_and_last_index(data_lines, self.admin_site_register_regex)

        # Model Admin
        # Find the registries first to reduce the search range for the Model Admins
        model_admin_class_end = get_last_index(data_lines, self.func_regex)

        # Take the last model admin line and find the break between it and the registry line
        for c, line in enumerate(data_lines[model_admin_class_end:admin_registry_start]):
            if line:
                model_admin_class_end = c + model_admin_class_end
            else:
                break

        # Slice the existing admin.py into parts
        if 0 < model_import_line:
            render_ctx['pre_import'] = "\n".join(data_lines[0:model_import_line] )    # Everything up until the model import line

        if model_import_line < model_admin_class_end:
            render_ctx['pre_admin'] = "\n".join(data_lines[(model_import_line + 1):(model_admin_class_end + 1)] )    # Everything up until the model import line

        # pre_registration
        if model_admin_class_end < admin_registry_end:
            render_ctx['pre_registration'] = "\n".join(data_lines[(model_admin_class_end + 1):(admin_registry_end + 1)] )    # Everything up until the model import line

        # FOOTER
        if admin_registry_end < line_count:
            render_ctx['post_registration'] = "\n".join(data_lines[(admin_registry_end + 1):line_count] )    # Everything up until the model import line

        # Print out the results to the terminal, add as an option?
        admin_template = get_template('stubtools/stubadmin/admin.py.j2', using='jinja2')
        admin_result = admin_template.render(context=render_ctx)

        write_file(admin_file, admin_result)

