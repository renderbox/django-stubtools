#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-12-21 17:47:58
#--------------------------------------------

import os.path

from django.core.management.base import CommandError
from django.views.generic.base import View

from stubtools.core import FileAppCommand, version_check, split_camel_case, parse_app_input
from stubtools.core.prompt import ask_question, ask_yes_no_question, selection_list, horizontal_rule
from stubtools.core.view_classes import VIEW_CLASS_DEFAULT_SETTINGS, VIEW_CLASS_SETTINGS, STUBTOOLS_IGNORE_MODULES
from stubtools.core.filters import url_ctx_flter


class Command(FileAppCommand):
    args = '<app.view.view_class>'
    help = 'creates a template and matching view for the given view name'
    terminal_width = 80
    view_file = None
    url_file = None

    def handle(self, *args, **kwargs):
        if len(args) < 1:
            raise CommandError('Need to pass App.View names')

        # batch process app views
        try:
            for app_view in args:
                # SPLIT THE APP, VIEW AND VIEW_CLASS
                app, view, view_class = parse_app_input(app_view)
                self.process(app, view, view_class)
        except KeyboardInterrupt:
            print("\nExiting...")
            return


    def get_context(self, app, view, view_setting_key, **kwargs):

        view_class_settings = self.get_class_settings(View, ignore_modules=STUBTOOLS_IGNORE_MODULES, settings=VIEW_CLASS_SETTINGS)      # todo: move this over to a settings option
        self.pp.pprint(view_class_settings)
        view_class_shortname_map = dict([(v['class_name'], k) for k, v in view_class_settings.items()])

        # PICK THE VIEW CLASS TO USE BASED ON A LIST OF AVAILABLE CLASSES IF NOT SET IN THE COMMAND LINE
        if not view_setting_key:
            view_setting_key = selection_list(list( view_class_shortname_map.keys() ), as_string=True)
            
        if len(view_setting_key.split(".")) == 1:
            view_setting_key = view_class_shortname_map[view_setting_key]

        if view_setting_key:
            print("\nUsing Module Setting for '%s'" % view_setting_key)

        view_class = view_class_settings[view_setting_key]['class_name']

        print("View Class: %s" % view_class)

        if not view:
            default = "My%s" % view_class
            view = input("What is the name of the view? [%s] > " % default) or default

        # MAKE SURE AT LEAST THE FIRST LETTER OF THE VIEW NAME IS CAPITALIZED
        view = view[0].upper() + view[1:]

        view_name = "_".join(split_camel_case(view)).lower()

        render_ctx = {'app':app, 'view':view, 'view_name':view_name, 'views':[],
                        'view_class':view_class, 'attributes':{}, 
                        'view_class_module': view_class_settings[view_setting_key]['module'] }

        render_ctx.update(kwargs)  # Update with any context info passed in.

        attr_ctx = {'app_label': app, 'view_name':view_name}

        key_remove_attr_list = []   # This is so defaults are available while the questioning is going on so defaults can be applied to other attrs.

        if not 'template_in_app' in kwargs:
            render_ctx['template_in_app'] = ask_yes_no_question("Place templates at the app level?", default=True, required=True)

        render_ctx['constructor_template'] = view_class_settings[view_setting_key].get("template", VIEW_CLASS_DEFAULT_SETTINGS['template'])

        ################
        # QUERIES:
        # Query the user to build the attribute values

        self.logger.debug("Setting Key: %s" % view_setting_key)

        queries = []
        queries.extend(view_class_settings[view_setting_key].get("queries", []))

        default_queries = []
        default_queries.extend(VIEW_CLASS_DEFAULT_SETTINGS['queries'])

        default_values = view_class_settings[view_setting_key].get("default_values", {})

        for item in default_queries:
            if item['key'] in default_values:
                item['default'] = default_values[item['key']]

        queries.extend(default_queries)

        if 'model' in kwargs:       # If a model is explicitly passed in to the method, use that value.  It will be skipped in the queries.
            attr_ctx['model'] = kwargs['model']
            render_ctx['model'] = kwargs['model']
            print("** Working with Model -> %s" % kwargs['model'])

        for query in queries:
            key = query['key']

            self.logger.debug("KEY: %s" % key)

            if key in kwargs:   # Don't ask the question if an answer is already provided (usually from chaining).
                if self.debug:
                    print("\tValue provided in method call, skipping.")
                continue

            default = query.get("default", None)
            ignore_default = query.get("ignore_default", False)

            # Update the attribute context with the results of render_ctx['attributes'] before creating the default value
            attr_ctx.update(render_ctx['attributes'])

            if 'model' in attr_ctx:
                attr_ctx['model_name'] = "_".join(split_camel_case(attr_ctx['model'])).lower()

            # Create the default value so it can be used in the query prompt
            if default:
                default = default % attr_ctx    # Update the default value with the attr_ctx

            answer = ask_question(query["question"], default=default, required=query.get("required", False) )

            # If the result is seto to 'ignore_default' it will be poped out of the context when queries are done.
            # In other words, the value will be kept only if it's not the default after the queries are over.
            if ignore_default and answer == default:
                key_remove_attr_list.append(key)

            value_type = query.get('attr_type', None)

            if value_type == "str":
                answer = '\"%s\"' % answer

            # This way if an attribute value is updated, it's reapplied to the question context
            if query.get('as_atttr', True):
                render_ctx['attributes'][key] = answer
            else:
                render_ctx[key] = answer

        for key in key_remove_attr_list:
            del render_ctx['attributes'][key]

        view_suffix = view_class_settings[view_setting_key].get("view_suffix", "View")     # Given the view type, there is a common convention for appending to the name of the "page's" View's Class

        if not 'description' in render_ctx:
            render_ctx['description'] = ask_question("Did you want to add a quick description?")

        # POP VIEW OFF THE NAME PARTS IF IT IS THERE
        if view.endswith(view_suffix):
            render_ctx['resource_class'] = view
        else:
            render_ctx['resource_class'] = view + view_suffix

        # Break the Name up into parts
        name_parts = split_camel_case(view[:(-1 * len(view_suffix))])

        render_ctx['page'] = "_".join(name_parts).lower()   # Name used in the URL and template
        render_ctx['page_name'] = ' '.join(name_parts)      # Title Friendly Format

        if version_check("gte", "2.0.0"):
            render_ctx['resource_method'] = "path"
        else:
            render_ctx['resource_method'] = "url"

        render_ctx['class_based_view'] = True

        return render_ctx

    def process(self, app, view, view_class, **kwargs):

        self.render_ctx = self.get_context(app, view, view_class, **kwargs)

        view_file = os.path.join(app, "views.py")
        url_file = os.path.join(app, "urls.py")

        view_template_file = os.path.join('stubtools', 'stubview', "views.py.j2")
        url_template_file = os.path.join('stubtools', 'stubview', "urls.py.j2")

        if self.render_ctx['template_in_app']:
            template_file = os.path.join(app, "templates", *self.render_ctx['attributes']['template_name'][1:-1].split("/"))
        else:
            template_file = os.path.join("templates", *self.render_ctx['attributes']['template_name'][1:-1].split("/"))     # todo: get the template folder name from the settings

        if version_check("gte", "2.0.0"):
            url_modules = [ ("django.urls", "path", "re_path"), ("views",) ]
        else:
            url_modules = [ ("django.conf.urls", "url"), ("views",) ]

        # #######################
        # # RENDER THE TEMPLATES
        # #######################

        ####
        # Views
        self.write(view_file, self.render_ctx['view_class'], 
                    template=view_template_file,
                    extra_ctx=self.render_ctx, 
                    modules=[ (self.render_ctx['view_class_module'], self.render_ctx['view_class']) ])

        self.write(url_file, self.render_ctx['view_class'], 
                    template=url_template_file,
                    extra_ctx=self.render_ctx, 
                    modules=url_modules,
                    filters=[url_ctx_flter])

        if not os.path.exists(template_file):
            constructor_template = os.path.join('stubtools', 'stubview', self.render_ctx['constructor_template'])

            self.write(template_file, self.render_ctx['view_class'], 
                        template=constructor_template,
                        extra_ctx=self.render_ctx)

        #######################
        # Writing Output

        print( horizontal_rule() )
        print("FILES:")
        print("    VIEW FILE: %s" % view_file)
        print("    URL FILE: %s" % url_file)
        print("    TEMPLATE FILE: %s" % template_file)

