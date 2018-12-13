# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-12-05 14:50:04
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-12 16:49:55
# --------------------------------------------
import os
import os.path

from django.conf import settings
from django.core.management.base import CommandError

from stubtools.core import FileAppCommand, parse_app_input
from stubtools.core.prompt import horizontal_rule, selection_list, ask_question
from stubtools.core.file import PythonFileParser

INSTALL_INSTRUCTIONS = """
stubapi is meant to work with the Django REST Framework.  
You will need to install the Django-REST app to work with APIs.

In your python environment run (via command line):

    pip install djangorestframework

Then add it to your list of INSTALLED APPS in settings.py:

INSTALLED_APPS = (
    ...
    'rest_framework',
)

Check out the docs if you have more questions:
    https://www.django-rest-framework.org
"""

class Command(FileAppCommand):

    args = '<app.api>'
    help = 'creates a boilerplate for Django-REST based APIs'

    def handle(self, *args, **kwargs):
        if len(args) < 1:
            raise CommandError('Need to pass App.API names')

        try:
            for api_view in args:
                # SPLIT THE APP, VIEW AND VIEW_CLASS
                app, api, api_class = parse_app_input(api_view)
                self.process(app, api, api_class)

        except KeyboardInterrupt:
            print("\nExiting...")
            return

    def get_context(self, app, api, api_class, **kwargs):

        # Check to see if Django-REST Framework is installed...
        if not "rest_framework" in settings.INSTALLED_APPS:
            print(INSTALL_INSTRUCTIONS)
            return {}

        if api_class == None:
            pass

        app_models = self.get_app_models(app)
        api_view_class_types = ['ListAPIView', 'RetrieveAPIView']

        # Queries

        # Which Model?
        model = selection_list(app_models, "Pick a model to create a REST API for.", as_string=True)

        serializer_class = ask_question("What do you want to call the serializer?", default="%sSerializer" % model)

        # Which REST API ViewSet Type?
        api_view_class_type = selection_list(api_view_class_types, "Pick a model to create a REST API for.", as_string=True)

        api_view_class = ask_question("What do you want to call the API View?", default="%s%s" % (model, api_view_class_type) )

        api_view_description = ask_question("Do you want to add a quick description to the API View?" )

        model_fields = self.get_model_fields(app, model)
        # model_fields = [ x for x in self.get_model_fields(app, model) if x not in ['id', 'pk'] ]  # Remove fields that should be ignored by default

        api_view_path = model.lower()
        api_view_name = "%s-%s-api" % (app, model)

        model_class_module = "%s.models" % app

        ctx = {'app': app, 'model':model, 'api_view_class':api_view_class, 'api_view_class_type':api_view_class_type, 
                'serializer_class':serializer_class, 'api_view_description':api_view_description, 
                'model_fields':model_fields, 'api_view_path':api_view_path, 'api_view_name':api_view_name.lower(),
                'model_class_module':model_class_module}
        
        return ctx

    def sliced_ctx(self, file_path, new_class, module, module_path=None, extra_ctx={}, required_modules=[]):
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

        if module_path:
            parser.set_import_slice(module_path)

        ctx['header'] = parser.get_header()
        ctx['body'] = parser.get_body()
        ctx['footer'] = parser.get_footer()
        ctx['import_statement'] = parser.create_import_statement(module, path=module_path)

        for mod in required_modules:
            included = parser.get_import_line(mod[0])  # Does a check to see if the line is already included or not

            if included == None:
                if len(mod) == 1:
                    ctx['import_statement'] = "import %s\n" % (mod[0]) + api_ctx['import_statement']
                else:
                    ctx['import_statement'] = "from %s import %s\n" % (mod[0], ", ".join(mod[1:])) + ctx['import_statement']

        return ctx

    def process(self, app, api, api_class, **kwargs):
        api_dir = os.path.join(app, 'api')
        api_views_file = os.path.join(api_dir, 'views.py')
        api_urls_file = os.path.join(api_dir, 'urls.py')
        api_serializers_file = os.path.join(api_dir, 'serializers.py')

        self.render_ctx = self.get_context(app, api, api_class, **kwargs)

        if not self.render_ctx:
            return

        # Slice the files...

        # self.pp.pprint(self.render_ctx)
        # self.write_files = False            # While Debugging

        # ####
        # # Serializers
        # if not os.path.isfile(api_serializers_file):

        #     os.makedirs(api_dir, exist_ok=True)

        #     FILE = open(api_serializers_file, "w")
        #     FILE.write("")
        #     FILE.close()

        # api_parser = PythonFileParser(api_serializers_file)

        # api_ctx = {}
        # api_ctx.update(self.render_ctx)
        # api_ctx['add_serializer'] = True

        # api_parser.set_import_slice(api_ctx['model_class_module'])

        # if api_ctx['serializer_class'] in api_parser.structure['class_list']:
        #     print("** %s form already in '%s', skipping creation..." % (api_ctx['serializer_class'], api_serializers_file))
        #     api_ctx['add_serializer'] = False
            
        # api_ctx['header'] = api_parser.get_header()
        # api_ctx['body'] = api_parser.get_body()
        # api_ctx['footer'] = api_parser.get_footer()
        # api_ctx['import_statement'] = api_parser.create_import_statement(api_ctx['model'], path=api_ctx['model_class_module'])

        # rest_import_line = api_parser.get_import_line("rest_framework")  # Does a check to see if the line is already included or not

        # if rest_import_line == None:
        #     api_ctx['import_statement'] = "from rest_framework import serializers\n" + api_ctx['import_statement']

        api_ctx = self.sliced_ctx(api_serializers_file, self.render_ctx['serializer_class'], self.render_ctx['model'], 
                                    module_path=self.render_ctx['model_class_module'], 
                                    extra_ctx=self.render_ctx, 
                                    required_modules=[ ("rest_framework", "serializers") ])

        self.pp.pprint(api_ctx)

        api_serializers_template = self.get_template('stubtools/stubapi/serializers.py.j2')
        api_serializers_result = api_serializers_template.render(context=api_ctx)

        if self.write_files:
            self.write_file(api_serializers_file, api_serializers_result)
        else:
            self.echo_output(api_serializers_file, api_serializers_result)

        self.write_files = False            # While Debugging

        ####
        # Views

        api_views_template = self.get_template('stubtools/stubapi/views.py.j2')
        api_views_result = api_views_template.render(context=self.render_ctx)

        if self.write_files:
            self.write_file(api_views_file, api_views_result)
        else:
            self.echo_output(api_views_file, api_views_result)

        api_urls_template = self.get_template('stubtools/stubapi/urls.py.j2')
        api_urls_result = api_urls_template.render(context=self.render_ctx)

        if self.write_files:
            self.write_file(api_urls_file, api_urls_result)
        else:
            self.echo_output(api_urls_file, api_urls_result)

