#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-12-12 14:37:38
#--------------------------------------------

# from django.core.management.base import CommandError
# import re, os.path
# from stubtools.core import FileAppCommand, underscore_camel_case


from jinja2 import Environment, PackageLoader, select_autoescape

from django.core.management.base import CommandError
from django.template.loader import get_template

from stubtools.core import FileAppCommand, parse_app_input
from stubtools.core.search import get_first_index, get_last_index, get_first_and_last_index
from stubtools.core.file import write_file, PythonFileParser
from stubtools.core.prompt import horizontal_rule, selection_list


class Command(FileAppCommand):
    args = '<app.model_name>'
    help = 'creates a form for a model class'
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

    def get_context(self, app, model, app_models=None, **kwargs):

        if model == None:       # If not model is provided, ask which one to work with
            model = selection_list(app_models, "Pick a model to create an Form for.", as_string=True)

        model_form = model + "Form"

        model_list = [model]

        model_fields = [ x for x in self.get_model_fields(app, model) if x not in ['id', 'pk'] ]  # Remove fields that should be ignored by default
        # Pop the ID field if persent

        result = { 'header':"", 'body':"", 'footer':"",'model':model, 
                    'model_form':model_form, 'form_import':"",
                    'create_model_form':True, 'import_statement':"",
                    'model_class_module':".models", 'model_fields':model_fields}

        # Update the import line to include any missing model classes
        model_list.extend(app_models)
        model_list = list(set(model_list))
        model_list.sort()

        return result

    def process(self, app, model, **kwargs):
        form_file = "%s/forms.py" % app

        print("FORM FILE: %s" % form_file)

        app_models = []

        if not model:
            app_models = self.get_app_models(app)

        self.render_ctx = self.get_context(app, model, app_models=app_models, **kwargs)

        self.load_file(form_file)


        #######################
        # PARSE forms.py
        #######################

        if self.debug:
            print( horizontal_rule() )
            print("FILE STRUCTURE:")
            self.pp.pprint(self.parser.structure)

        # Checkt to see if the form is already in the file and skip if it is...
        if self.render_ctx['model_form'] in self.parser.structure['class_list']:
            print("** %s form already in '%s', skipping creation..." % (self.render_ctx['model_form'], form_file))
            return

        modules = []
        comment = ""

        form_import_line = self.parser.get_import_line("django.forms")  # Does a check to see if the line is already included or not

        #########
        # FILE PARTS

        self.parser.set_import_slice(".models")

        self.render_ctx['header'] = self.parser.get_header()
        self.render_ctx['body'] = self.parser.get_body()
        self.render_ctx['footer'] = self.parser.get_footer()

        self.render_ctx['import_statement'] = self.parser.create_import_statement(self.render_ctx['model'], path=self.render_ctx['model_class_module'])

        if form_import_line == None:       # if it's not there, prepend the form import line
            # self.render_ctx['add_django_import_statement'] = True
            self.render_ctx['import_statement'] = "from django.forms import ModelForm\n" + self.render_ctx['import_statement']

        #######################
        # RENDER THE TEMPLATES
        #######################

        if self.debug:
            print( horizontal_rule() )
            print("RENDER CONTEXT:")
            self.pp.pprint(self.render_ctx)
            print( horizontal_rule() )

        form_template = get_template('stubtools/stubform/forms.py.j2', using='jinja2')
        form_result = form_template.render(context=self.render_ctx)

        if self.debug:
            print( horizontal_rule() )
            print("forms.py RESULT:")
            print( horizontal_rule() )
            print(form_result)

        if self.write_files:
            self.write_file(form_file, form_result)
            print( horizontal_rule() )
            print("Wrote File: %s" % form_file)

    def get_module_import_info(self, module):
        i = self.parser.structure['from_list'].index(module)
        result = self.parser.structure['imports'][i]
        return result

    def get_header(self):
        pass

# class Command(FileAppCommand):
#     args = '<app.model_name>'
#     help = 'creates stub model form entries'
#     class_regex = re.compile(r"class (\w+)\(.+\):")
#     import_line_regex = re.compile(r"^from django import (.+)", re.MULTILINE)
#     imports_regex = re.compile(r"(import|from)")
#     func_regex = re.compile(r"(def|class)")


#     def handle(self, *args, **options):

#         if not args:
#             print("No Arguments Passed")
#             return

#         for entry in args:
#             app, model = entry.split(".")
#             print("CHECKING FOR MODEL FORM FOR: %s" % model)
#             self.process(app, model)


#     def process(self, app, model, *args, **kwargs):
#         form_file = "%s/forms.py" % app
#         print("FORM FILE: %s" % form_file)

#         import_line = False
#         import_entry = False
#         first_class_line = 0
#         last_import_line = 0
#         modelform = model + "Form"

#         # LOAD FILE
#         if os.path.isfile( form_file ):
#             try:
#                 FILE = open( form_file, "r")
#                 data = FILE.read()

#                 form_import = self.import_line_regex.findall( data )

#                 if form_import:
#                     import_line = True

#                     for line in form_import:
#                         if 'forms' in [x.strip() for x in line.split(",") ]:
#                             import_entry = True

#                 classes = self.class_regex.findall( data )
#                 FILE.close()

#             except IOError as e:
#                 pass                    # May need to add something here
#                                         # to handle a file locking issue
#         # LOOK FOR CLASS WITH NAME
#         if modelform in classes:
#             print('Form Exists: %s' % modelform)
#             return

#         print('Creating Form: %s' % modelform)

#         import_model_regex = re.compile(r"^from %s.models import (.+)" % (app), re.MULTILINE)
#         imported_models = import_model_regex.findall( data )

#         if not import_entry or imported_models:
#             # FIND WHERE TO ADD THE IMPORT LINE
#             lines = []
#             for m in re.finditer( self.func_regex, data ):
#                 lines.append( data.count("\n",0,m.start())+1 )

#             if lines:
#                 lines.sort()
#                 first_class_line = lines[0]

#             print("[%d]" % ( first_class_line ) )

#             lines = []
#             for m in re.finditer( self.imports_regex, data ):
#                 lineno = data.count("\n",0,m.start())+1
#                 if lineno < first_class_line:
#                     lines.append(lineno)
#                 #print("[%d] %s" % (lineno, data[ m.start() : m.end() ] ) )
#             if lines:
#                 lines.sort()
#                 last_import_line = lines[-1]

#             print("[%d]" % ( last_import_line ) )

#         if not import_entry:
#             pass

#         if imported_models:
#             imported_models = [x.strip() for x in imported_models[0].split(',')]
#         else:
#             print("Adding Model with Import Line")

#         if model not in imported_models:
#             print("Adding Model to Import Line")

#             # CREATE IMPORT LINE

#             # ADD TO IMPORT LINE

#         # model_ctx = { 'modelform':modelform, 'model':model }


#         mf = open( form_file, "a" )
#         mf.write("\n\nclass %s(forms.ModelForm):\n\n    class Meta:\n        model = %s" % (modelform, model) )
#         mf.close()
