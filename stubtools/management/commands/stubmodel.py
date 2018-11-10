#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-11-09 17:58:33
#--------------------------------------------

import re, os.path
# import inspect
import pprint

from jinja2 import Environment, PackageLoader, select_autoescape

from django.core.management.base import AppCommand, CommandError
from django.db import models
from django.db.models import Model, Field

from stubtools.core import underscore_camel_case, import_line_check, class_name, get_all_subclasses, parse_app_input
from stubtools.core.prompt import ask_question, ask_yes_no_question, selection_list, horizontal_rule
from stubtools.core.parse import get_import_range

# Fields that are not really meant to be included in the list of useable Model Fields
EXCLUDED_FIELDS = ['BLANK_CHOICE_DASH', 'Empty', 'Field', 'FieldDoesNotExist', 'NOT_PROVIDED']



class Command(AppCommand):
    args = '<app.model_name>'
    help = 'creates stub Templates, Forms and Admin entries for a given model name'
    import_line_regex = re.compile(r"^from django.db import (.+)", re.MULTILINE)
    import_uget_regex = re.compile(r"^from django.utils.translation import (.+)", re.MULTILINE)
    imports_regex = re.compile(r"(import|from)")
    class_regex = re.compile(r"class (\w+)\(.+\):")
    func_regex = re.compile(r"(def|class)")


    def handle(self, *args, **kwargs):

        # batch process app models
        try:
            for app_model in args:
                self.process(app_model, *args, **kwargs)
        except KeyboardInterrupt:
            print("\nExiting...")
            return


    def get_context(self, app, model, model_class):

        # model_classes = get_all_subclasses(Model, ignore_modules=['django.contrib.contenttypes.models', 'django.contrib.admin.models', 'django.contrib.sessions'])
        model_classes = ['django.db.models.Model', 'django.contrib.auth.models.AbstractUser']
        model_classes.extend([ "%s.%s" % (x.__module__, x.__name__) for x in get_all_subclasses(Model, ignore_modules=['django.contrib.contenttypes.models', 'django.contrib.admin.models', 'django.contrib.sessions', 'django.contrib.auth.base_user', 'django.contrib.auth.models']) ])
        field_classes = [ "%s.%s" % (x.__module__, x.__name__) for x in get_all_subclasses(Field, ignore_modules=["django.contrib.contenttypes"]) ]

        model_class_settings = {}
        # modelclass_settings.update(MODELCLASS_SETTINGS)     # Update the setting dict with defaults
        model_key = selection_list(model_classes, as_string=True, title="Select a Model Class")



        render_ctx = {'model_key':model_key}

        return render_ctx

    def process(self, app_model, *args, **kwargs):

        pp = pprint.PrettyPrinter(indent=4)

        app, model, model_class = parse_app_input(app_model)

        model_file = os.path.join(app, "models.py")
        # form_file = os.path.join(app, "forms.py")

        print("MODEL FILE: %s" % model_file)

        render_ctx = self.get_context(app, model, model_class)

        if render_ctx['model_key'] == "django.db.models.Model"
            render_ctx['model_class_module'] = "django.db"
            render_ctx['model_class'] = "models.Model"
        else:
            render_ctx['model_class_module'] = ".".join( render_ctx['model_key'].split(".")[:-1] )
            render_ctx['model_class'] = render_ctx['model_key'].split(".")[-1]

        # #######################
        # # PARSE models.py
        # #######################

        # Slice and Dice!
        data_lines = get_file_lines(model_file)
        line_count = len(data_lines)

        # Establish the Segments
        import_start_index = 0
        import_end_index = 0
        class_func_start = get_classes_and_functions_start(data_lines)
        class_func_end = line_count

        # Segment Values
        model_header = None         # In between the first line and the module import
        model_pre_model = None      # between the import line and where the model needs to be added
        model_footer = None         # after the model code

        modules = []
        comments = ""

        import_start_index, import_end_index = get_import_range("^from %(model_class_module)s import (.+)" % render_ctx, data_lines[:class_func_start])

        if import_start_index > import_end_index:
            modules, comments = get_classes_and_functions(data_lines[import_start_index])

        #######################
        # RENDER THE TEMPLATES
        #######################

        print( horizontal_rule() )
        print("RENDER CONTEXT:")
        pp.pprint(render_ctx)
        print( horizontal_rule() )


        # # LOAD FILE
        # if os.path.isfile( model_file ):
        #     try:
        #         FILE = open( model_file, "r")
        #         data = FILE.read()

        #         if not import_line_check(self.import_line_regex, data, 'models'):
        #             new_lines.append("from django.db import models")

        #         if not import_line_check(self.import_uget_regex, data, 'ugettext_lazy as _'):
        #             new_lines.append("from django.utils.translation import ugettext_lazy as _")

        #         classes = self.class_regex.findall( data )
        #         FILE.close()

        #     except IOError as e:
        #         print("IO ERROR, CONTINUE")
        #         pass                    # May need to add something here
        #                                 # to handle a file locking issue
        # else:
        #     print( "File Not Found: %s" % model_file )
        #     return

        # # LOOK FOR CLASS WITH NAME
        # if model in classes:
        #     print('Model Exists: %s' % model)
        #     return

        # if not import_entry:
        #     lines = []
        #     for m in re.finditer( self.func_regex, data ):
        #         lines.append( data.count("\n",0,m.start())+1 )

        #     if lines:
        #         lines.sort()
        #         first_class_line = lines[0]

        #     lines = []
        #     for m in re.finditer( self.imports_regex, data ):
        #         lineno = data.count("\n",0,m.start())+1
        #         if lineno < first_class_line:
        #             lines.append(lineno)
        #     if lines:
        #         lines.sort()
        #         last_import_line = lines[-1]

        # # Process the templates
        # print('Creating Model: %s' % model)

        # model_template = get_template('stubtools/stubmodel/models.py.j2', using='jinja2')

        # # ADD THE MODEL TO THE LINES
        # render_ctx['model_name'] = model
        # render_ctx['fields'] = [{'field_name':"name", 'field_type':"CharField", 'field_kwargs':{'max_length':300}}]

        # new_lines.append( model_template.render(context=render_ctx) )

        # mf = open( model_file, "a" )
        # # NEEDS TO LOAD AND REWRITE THE FILE RATHER THAN JUST APPEND
        # mf.write( "\n".join(new_lines) )
        # mf.close()

        # model_results = "\n".join(new_lines)
        # write_file(model_file, model_results)

