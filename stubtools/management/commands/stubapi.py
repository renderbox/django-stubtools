# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-12-05 14:50:04
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-10 17:52:17
# --------------------------------------------
from django.conf import settings
from django.core.management.base import CommandError

from stubtools.core import FileAppCommand, parse_app_input
from stubtools.core.prompt import horizontal_rule, selection_list, ask_question
from stubtools.core.file import PythonFileParser

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
            print("You need to install the Django-REST app first")
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

        api_view_path = model.lower()
        api_view_name = "%s-%s-api" % (app, model)

        ctx = {'app': app, 'model':model, 'api_view_class':api_view_class, 'api_view_class_type':api_view_class_type, 
                'serializer_class':serializer_class, 'api_view_description':api_view_description, 
                'model_fields':model_fields, 'api_view_path':api_view_path, 'api_view_name':api_view_name.lower()}
        
        return ctx

    def process(self, app, api, api_class, **kwargs):
        api_views_file = "%s/api/views.py" % app
        api_urls_file = "%s/api/urls.py" % app
        api_serializers_file = "%s/api/serializers.py" % app

        self.render_ctx = self.get_context(app, api, api_class, **kwargs)

        # Slice the files...

        # self.pp.pprint(self.render_ctx)
        self.write_files = False            # While Debugging

        api_serializers_template = self.get_template('stubtools/stubapi/serializers.py.j2')
        api_serializers_result = api_serializers_template.render(context=self.render_ctx)

        if self.write_files:
            self.write_file(api_serializers_file, api_serializers_result)
        else:
            self.echo_output(api_serializers_file, api_serializers_result)

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

