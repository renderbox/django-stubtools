#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-12-21 15:46:46
#--------------------------------------------
from stubtools.core import FileAppCommand, parse_app_input
from stubtools.core.file import PythonFileParser
from stubtools.core.prompt import selection_list


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
        form_file_template = 'stubtools/stubform/forms.py.j2'

        app_models = []

        if not model:   # If no model is passed in, select from a list of already installed models.
            app_models = self.get_app_models(app)

        self.render_ctx = self.get_context(app, model, app_models=app_models, **kwargs)

        # Check to see if the form is already in the file and skip if it is...
        if self.render_ctx['model_form'] in self.parser.structure['class_list']:
            print("** \"%s\" form already in '%s', skipping creation..." % (self.render_ctx['model_form'], form_file))
            return

        #######################
        # RENDER THE TEMPLATES
        #######################

        self.write(form_file, self.render_ctx['model_form'], 
                    template=form_file_template,
                    extra_ctx=self.render_ctx, 
                    modules=[ ('django.forms', 'ModelForm'),
                              ('.models', self.render_ctx['model']) ])

