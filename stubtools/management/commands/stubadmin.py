#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-12-21 15:12:35
#--------------------------------------------

from django.template.loader import get_template

from stubtools.core import FileAppCommand, parse_app_input
from stubtools.core.prompt import selection_list
from stubtools.core.filters import admin_ctx_filter


class Command(FileAppCommand):
    args = '<app.model_name>'
    help = 'creates the admin setup for a model class'
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
            model = selection_list(app_models, "Pick a model to create an Admin interface for.", as_string=True)

        model_admin = model + "Admin"

        model_list = [model]

        result = {  'model':model, 'model_admin':model_admin, 'admin_import':"",
                    'create_model_admin':True, 'model_class_import_statement':"",
                    'model_class_module':".models", 'register_model_admin':True}

        # Update the import line to include any missing model classes
        model_list.extend(app_models)
        model_list = list(set(model_list))
        model_list.sort()

        return result


    def process(self, app, model, **kwargs):
        admin_file = "%s/admin.py" % app
        admin_template_file = 'stubtools/stubadmin/admin.py.j2'

        print("ADMIN FILE: %s" % admin_file)

        app_models = []

        if not model:
            app_models = self.get_app_models(app)

        self.render_ctx = self.get_context(app, model, app_models=app_models, **kwargs)

        self.load_file(admin_file)

        #######################
        # RENDER THE TEMPLATES
        #######################

        self.write(admin_file, self.render_ctx['model'], 
                    template=admin_template_file,
                    extra_ctx=self.render_ctx, 
                    modules=[ ('django.contrib', 'admin'),
                              (self.render_ctx['model_class_module'], self.render_ctx['model']) ],
                    filters=[ admin_ctx_filter ])


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
