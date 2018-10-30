#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-10-30 09:39:14
#--------------------------------------------

import os.path
import re
import inspect

from jinja2 import Environment, PackageLoader, select_autoescape

from django.core.management.base import AppCommand, CommandError
# from django.db import models

# from stubtools.core import underscore_camel_case, import_line_check, class_name

class Command(AppCommand):
    args = '<app.model_name>'
    help = 'creates the admin setup for a model class'
    class_regex = re.compile(r"class (\w+)\(.+\):")
    import_line_regex = re.compile(r"^from django import (.+)", re.MULTILINE)
    imports_regex = re.compile(r"(import|from)")
    func_regex = re.compile(r"(def|class)")


    def handle(self, *args, **options):

        app = None
        model = None

        for entry in args:

            try:
                app, model = entry.split(".")
                # print("CHECKING FOR MODEL ADMIN FOR: %s.%s" % (app, model))
                self.process(app, model)

            except ValueError:
                app = entry
                models = input("Which model(s) did you want to work on in the app \"%s\"? (Model Model ...) > " % app)

                for model in models.split():
                    # print("CHECKING FOR MODEL FORM FOR: %s.%s" % (app, model))
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
                data = FILE.read()

                model_classes = self.class_regex.findall( data )
                FILE.close()

            except IOError as e:
                pass                    # May need to add something here to handle a file locking issue

        if model not in model_classes:
            if model_classes:
                print('"%s" Not Found in models.py.  Possible Model Classes are:' % model)
                for m in model_classes:
                    print('\t%s' % m)
                return
            else:
                print("There are currently no models found in models.py.  You will need to add some.")
                return

        # Load admin.py to check it's contents
        if os.path.isfile( admin_file ):
            try:
                FILE = open( admin_file, "r")
                data = FILE.read()

                admin_import = self.import_line_regex.findall( data )

                if admin_import:
                    import_line = True

                    for line in admin_import:
                        if 'forms' in [x.strip() for x in line.split(",") ]:
                            import_entry = True

                classes = self.class_regex.findall( data )
                FILE.close()

            except IOError as e:
                pass                    # May need to add something here to handle a file locking issue

        # LOOK FOR CLASS WITH NAME
        if model_admin in classes:
            print('%s Admin Interface Exists, Skipping.' % model_admin)
            return

        # Temporary until file editing is added in
        print("Add the following to your code if they are not already there:\n")
        print("from .models import %s\n" % model)
        print("class %s(admin.ModelAdmin):\n\tpass\n" % model_admin)
        print("admin.site.register(%s, %s)\n\n" % (model, model_admin))

        # import_model_regex = re.compile(r"^from %s.models import (.+)" % (app), re.MULTILINE)
        # imported_models = import_model_regex.findall( data )

        # if not import_entry or imported_models:
        #     # FIND WHERE TO ADD THE IMPORT LINE
        #     lines = []
        #     for m in re.finditer( self.func_regex, data ):
        #         lines.append( data.count("\n",0,m.start())+1 )

        #     if lines:
        #         lines.sort()
        #         first_class_line = lines[0]

        #     print("[%d]" % ( first_class_line ) )

        #     lines = []
        #     for m in re.finditer( self.imports_regex, data ):
        #         lineno = data.count("\n",0,m.start())+1
        #         if lineno < first_class_line:
        #             lines.append(lineno)
        #         #print("[%d] %s" % (lineno, data[ m.start() : m.end() ] ) )
        #     if lines:
        #         lines.sort()
        #         last_import_line = lines[-1]

        #     print("[%d]" % ( last_import_line ) )

        # if not import_entry:
        #     pass

        # if imported_models:
        #     imported_models = [x.strip() for x in imported_models[0].split(',')]
        # else:
        #     print("Adding Model with Import Line")

        # if model not in imported_models:
        #     print("Adding Model to Import Line")

        #     # CREATE IMPORT LINE

        #     # ADD TO IMPORT LINE

        # print('Creating Admin Interface: %s' % model_admin)

        # mf = open( admin_file, "a" )
        # mf.write("\n\nclass %s(forms.ModelForm):\n\n    class Meta:\n        model = %s" % (model_admin, model) )
        # mf.close()
