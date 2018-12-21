# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-12-05 14:50:04
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-21 15:13:05
# --------------------------------------------
import os
import os.path

from django.conf import settings
from django.core.management.base import CommandError

from stubtools.core import FileAppCommand, parse_app_input
from stubtools.core.prompt import horizontal_rule, selection_list, ask_question
from stubtools.core.file import PythonFileParser
from stubtools.core.filters import url_ctx_flter

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

    def process(self, app, api, api_class, **kwargs):
        api_dir = os.path.join(app, 'api')
        view_file = os.path.join(api_dir, 'views.py')
        url_file = os.path.join(api_dir, 'urls.py')
        serializers_file = os.path.join(api_dir, 'serializers.py')

        self.render_ctx = self.get_context(app, api, api_class, **kwargs)

        if not self.render_ctx:
            # IF an empty dict comes back, it falied the queries for some reason (maybe it already exists in the file)
            return


        ####
        # Serializers
        self.write(serializers_file, self.render_ctx['serializer_class'], 
                    template='stubtools/stubapi/serializers.py.j2',
                    extra_ctx=self.render_ctx, 
                    modules=[   ("rest_framework", "serializers"),
                                (self.render_ctx['model_class_module'], self.render_ctx['model']) ])

        ####
        # Views
        self.write(view_file, self.render_ctx['api_view_class'],
                    template='stubtools/stubapi/views.py.j2',
                    extra_ctx=self.render_ctx, 
                    modules=[   ("rest_framework", "generics"),
                                ( self.render_ctx['model_class_module'], self.render_ctx['model'] ),
                                ( ".serializers", self.render_ctx['serializer_class']) ])

        ####
        # URLs
        self.write(url_file, self.render_ctx['view_class'], 
                    template=url_template_file,
                    extra_ctx=self.render_ctx, 
                    modules=url_modules,
                    filters=[url_ctx_flter])

