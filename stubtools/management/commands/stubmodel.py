#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-12-21 17:07:30
#--------------------------------------------

import os.path

# from django.template.loader import get_template
from django.conf import settings

# from django.core.management.base import CommandError
# from django.db import models
from django.db.models import Model, Field

from stubtools.core import FileAppCommand, get_all_subclasses, parse_app_input, split_camel_case
from stubtools.core.prompt import ask_yes_no_question, selection_list, horizontal_rule

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
        render_ctx['create_model_api'] = False

        if render_ctx['create_model_api'] and 'rest_framework' not in settings.INSTALLED_APPS:
            render_ctx['create_model_api'] = False
            print("Please make sure you have the Django Rest Framework installed and 'rest_framework' added to your INSTALLED_APPS in settings.py")

        if render_ctx['create_model_views']:
            render_ctx['create_model_detail'] = ask_yes_no_question("Create a Model Detail View?", default=True, required=True)
            render_ctx['create_model_list'] = ask_yes_no_question("Create a Model List View?", default=True, required=True)
            render_ctx['create_model_create'] = ask_yes_no_question("Create a Model Create View?", default=True, required=True)
            render_ctx['create_model_update'] = ask_yes_no_question("Create a Model Edit View?", default=True, required=True)
            render_ctx['create_model_delete'] = ask_yes_no_question("Create a Model Delete View?", default=True, required=True)

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

        self.render_ctx = self.get_context(app, model, model_class, **kwargs)

        self.load_file(model_file)

        # #######################
        # # PARSE models.py
        # #######################

        # check to see if the model is already in models.py
        if self.render_ctx['model'] in self.parser.structure['class_list']:
            print("** \"%s\" model already in '%s', skipping creation..." % (self.render_ctx['model'], model_file))
            self.render_ctx['create_model'] = False

        #######################
        # RENDER THE TEMPLATES
        #######################

        ####
        # Model
        if self.render_ctx['create_model']:
            self.write(model_file, self.render_ctx['model'], 
                        template=model_file_template,
                        extra_ctx=self.render_ctx, 
                        modules=[ ('django.utils.translation', 'ugettext_lazy'),
                                  ('django.db', 'models') ])

        ####
        # Forms


        ####
        # Views
        print("VIEWS")
        if self.render_ctx['create_model_views']:
            from stubtools.management.commands.stubview import Command as ViewCommand
            vc = ViewCommand()
            vc.debug = self.debug
            view_kwargs = {}

            if self.render_ctx['create_model_detail']:
                vc.process(app, self.render_ctx['model_name'], "django.views.generic.detail.DetailView", model=self.render_ctx['model'], **view_kwargs)
                view_kwargs['template_in_app'] = vc.render_ctx['template_in_app']   # Append the anser to the view kwargs so it is not asked again

            if self.render_ctx['create_model_list']:
                vc.process(app, self.render_ctx['model_name'], "django.views.generic.list.ListView", model=self.render_ctx['model'], **view_kwargs)

            if self.render_ctx['create_model_create']:
                vc.process(app, self.render_ctx['model_name'], "django.views.generic.edit.CreateView", model=self.render_ctx['model'], **view_kwargs)

            if self.render_ctx['create_model_update']:
                vc.process(app, self.render_ctx['model_name'], "django.views.generic.edit.UpdateView", model=self.render_ctx['model'], **view_kwargs)

            if self.render_ctx['create_model_delete']:
                vc.process(app, self.render_ctx['model_name'], "django.views.generic.edit.DeleteView", model=self.render_ctx['model'], **view_kwargs)

        ####
        # Admin

        if self.render_ctx['create_model_admin']:

            from stubtools.management.commands.stubadmin import Command as AdminCommand
            ac = AdminCommand()
            ac.debug = self.debug
            admin_kwargs = {}

            ac.process(app, self.render_ctx['model'])

        ####
        # APIs

        # if self.render_ctx['create_model_api']:
        #     from stubtools.management.commands.stubapi import Command as ApiCommand
        #     ap = ApiCommand()
        #     ap.debug = self.debug
        #     admin_kwargs = {}

        #     ap.process(app, self.render_ctx['model'])
