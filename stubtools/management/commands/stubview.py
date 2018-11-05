#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-11-05 12:32:37
#--------------------------------------------

import re, os.path
import ast
import django

from django.core.management.base import AppCommand, CommandError
from django.views.generic.base import View

from jinja2 import Environment, PackageLoader, select_autoescape

from stubtools.core import class_name, version_check, get_all_subclasses, split_camel_case, underscore_camel_case
from stubtools.core.prompt import ask_question, selection_list, horizontal_rule
from stubtools.core.regex import FUNCTION_OR_CLASS_REGEX, IMPORT_REGEX


VIEW_CLASS_SETTINGS = {
    "TemplateView": {
        "queries": [
            {
                "question": "Any comment you want to add to the view?",
                "key": "comment",
                'required': False
            }
        ],
        "append": "View"
    },
    "ListView": {
        "queries": [
            {
                "question": "Which Model is this for?",
                "key": "model",
                'required': True
            },
            {
                "question": "Which template to use?",
                "key": "template_name",
                "default": "%(app)s/%(model)s_list.html",
                'attr_type':"str",
                'required': True
            }
        ],
        "append": "ListView"
    },
    "DetailView": {
        "queries": [
            {
                "question": "Which Model is this for?",
                "key": "model",
                'required': True
            },
            {
                "question": "Slug Keyword?",
                "key": "model",
                'required': False,
                "default": "%(model)s",
            },
            {
                "question": "What variable should be used for the model instance in the template?",
                "key": "model",
                'required': False,
                "default": "%(model)s",
            },
            {
                "question": "",
                "key": "form_class",
                'required': True
            },
            {
                "question": "Which template to use?",
                "key": "template_name",
                "default": "%(app)s/%(model)s_form.html",
                'attr_type':"str",
                'required': True
            }
        ],
        "append": "DetailView"
    },
    "FormView": {
        "queries": [
            {
                "question": "Which Model is this for?",
                "key": "model",
                'required': True
            },
            {
                "question": "",
                "key": "form_class",
                'required': True
            },
            {
                "question": "Which template to use?",
                "key": "template_name",
                "default": "%(app)s/%(model)s_form.html",
                'attr_type':"str",
                'required': True
            }
        ]},
    "RedirectView": {}
}


IGNORE_MODULES = ["django.views.i18n", "django.contrib.admin.views"]


def parse_app_view(app_view):
    parts = app_view.split(".")  # split the app and views

    if len(parts) == 3:
        return parts[0], parts[1], parts[2]

    if len(parts) == 2:
        return parts[0], parts[1], None

    return parts[0], None, None


class Command(AppCommand):
    args = '<app.view.view_class>'
    help = 'creates a template and matching view for the given view name'
    terminal_width = 80


    def handle(self, *args, **kwargs):
        if len(args) < 1:
            raise CommandError('Need to pass App.View names')

        # batch process app views
        for app_view in args:
            self.process(app_view, *args, **kwargs)


    def process(self, app_view, *args, **kwargs):

        class_based_views_available = version_check("gte", "1.3.0")        # SHOULD DEFAULT FOR 1.3+ TO True.  NEED ATTR IN settings.py TO CONFIG SET TO FALSE.

        # SPLIT THE APP, VIEW AND VIEW_CLASS
        app, view, view_class = parse_app_view(app_view)

        view_file = "%s/views.py" % app

        if not view:
            view = input("What is the name of the view? > ")

        # MAKE SURE AT LEAST THE FIRST LETTER OF THE VIEW NAME IS CAPITALIZED
        view = view[0].upper() + view[1:]

        # Load the classes each time so they can be made to include views that were previously created
        view_classes = get_all_subclasses(View, ignore_modules=IGNORE_MODULES)

        # Update the VIEW_CLASS_SETTINGS module value
        for cl in view_classes:
            class_name = cl.__name__    # Get the short name for the class


            if class_name not in VIEW_CLASS_SETTINGS: 
                VIEW_CLASS_SETTINGS[class_name] = {} 

            VIEW_CLASS_SETTINGS[class_name]['module'] = cl.__module__   # Set the module to the full import path

        classes = list(VIEW_CLASS_SETTINGS.keys())

        # PICK THE VIEW CLASS TO USE BASED ON A LIST OF AVAILABLE CLASSES IF NOT SET IN THE COMMAND LINE
        if not view_class:
            view_class = selection_list(classes, as_string=True)

        view_name = "_".join(split_camel_case(view)).lower()

        render_ctx = {'app':app, 'view':view, 'view_name':view_name, 'views':[],'view_class':view_class, 'attributes':{} }

        view_class_module = VIEW_CLASS_SETTINGS[view_class]['module']

        # Ask the Queries to build the attribute values
        for query in VIEW_CLASS_SETTINGS[view_class].get("queries", []):
            default = query.get("default", None)

            if default:
                attr_ctx = {'app': app, 'view_name':view_name}
                attr_ctx.update(render_ctx['attributes'])
                print(attr_ctx)
                attr_ctx['model'] = "_".join(split_camel_case(attr_ctx['model'])).lower()
                default = default % attr_ctx

            answer = ask_question(query["question"], default=default, required=query.get("required", False) )

            value_type = query.get('attr_type', None)

            if value_type == "str":
                answer = '\"%s\"' % answer

            render_ctx['attributes'][query['key']] = answer 

        page_append = VIEW_CLASS_SETTINGS[view_class].get("append", "View")     # Given the view type, there is a common convention for appending to the name of the "page's" View's Class

        render_ctx['description'] = ask_question("Did you want to add a quick description?")

        # POP VIEW OFF THE NAME PARTS IF IT IS THERE
        if view.endswith(page_append):
            render_ctx['page_class'] = view
        else:
            render_ctx['page_class'] = view + page_append

        # Break the Name up into parts
        name_parts = split_camel_case(view[:(-1 * len(page_append))])

        render_ctx['page'] = "_".join(name_parts).lower()   # Name used in the URL and template
        render_ctx['page_name'] = ' '.join(name_parts)      # Human Friendly Format

        # Setting up for attributes to use different types
        render_ctx['resource'] = {'method':"path"}  # resource is used mainly in the URL template

        #######################
        # PARSE view.py
        #######################

        # view_import_line_regex = re.compile(r"^from " + VIEW_CLASS_SETTINGS[view_class]['module'] + " import (.+)", re.MULTILINE)

        if os.path.isfile( view_file ):
            FILE = open( view_file, "r")
            data = FILE.read()
            FILE.close()

        # Slice and Dice!
        data_lines = data.split("\n")
        line_count = len(data_lines)

        # Establish the Segments
        import_start_index = 0
        import_end_index = 0
        import_line = None
        view_start_index = line_count
        view_end_index = line_count

        # Segment Values
        pre_import = None
        pre_view = None
        post_view = None

        # 1) Find where Classes and Functions start

        for c, line in enumerate(data_lines):
            if FUNCTION_OR_CLASS_REGEX.findall( line ):
                view_start_index = c       # Make note of the line number
                break

        pattern = "^from %s import (.+)" % view_class_module
        module_regex = re.compile(pattern, re.MULTILINE)

        import_zone = data_lines[:view_start_index]
        modules = []

        for c, line in enumerate(import_zone):
            modules_check = module_regex.findall( line )

            if modules_check:
                import_line = c             # Record the line number and break at the first match
                modules.extend(modules_check)
                break

        if view_class not in modules:
            modules.append(view_class)
        modules.sort()

        # PULL OUT THE IMPORTED ITEMS AND REBUILD THE LINE
        render_ctx['import_statement'] = "from %s import %s" % (view_class_module, ", ".join(modules))

        if not import_line:

            if view_start_index > 0:
                import_end_index = view_start_index - 1
            else:
                import_end_index = view_start_index

            for c, line in enumerate(import_zone):
                if IMPORT_REGEX.findall( line ):
                    import_end_index = c       # Make note of the line number

            import_line = import_end_index + 1
            view_start_index = import_end_index + 1
        else:
            view_start_index = import_line + 1

        # 3) Find where the post_view starts

        # Search backwards until there is line that is not blank or a starting with a '#'.
        # This is here to provide recognition for footers on files that may be there
        # todo: Add support for """/''' blocks?

        for c, line in reversed(list(enumerate(data_lines))):
            cleaned_line = line.strip()

            if cleaned_line:
                if not cleaned_line.startswith("#"):
                    view_end_index = c + 1
                    break

        # 4) Build the sections

        render_ctx['pre_import'] = "\n".join(data_lines[:import_line])
        render_ctx['pre_view'] = "\n".join(data_lines[view_start_index:view_end_index])
        render_ctx['post_view'] = "\n".join(data_lines[view_end_index:])

        # PRE-IMPORT RESULTS
        print( horizontal_rule() )
        print("PRE-IMPORT:")
        print(render_ctx['pre_import'])
        print( horizontal_rule() )
        print("PRE-VIEW:")
        print(render_ctx['pre_view'])
        print( horizontal_rule() )
        print("POST-VIEW:")
        print(render_ctx['post_view'])
        print( horizontal_rule() )

        # 5) Assemble the file

        #######################
        # RENDER THE TEMPLATES
        #######################

        # Start Rendering a writing files
        env = Environment( loader=PackageLoader('stubtools', 'templates/commands/stubview'), autoescape=select_autoescape(['html']) )
        template = env.get_template('view.py.j2')

        result = template.render(**render_ctx)
        print( horizontal_rule() )
        print("RESULT:")
        print(result)




        # # module_regex = re.compile("%s import (.+)" % view_class_module)

        # # if class_based_views_available:
        # #     url_entry_regex = re.compile("url\(\S+ (\S+)" )
        # # else:
        # #     url_entry_regex = re.compile("url\(\S+ '(\S+)'" )

        # # TEMPLATE
        # # App templates or Project Templates?

        # # Get contents of views.py file
        # if os.path.isfile(view_file):
        #     try:
        #         FILE = open(view_file, "r")
        #         data = FILE.read()
        #         FILE.close()
        #     except IOError as e:
        #         print( "IO Error reading %s\n\t%s" % (view_file, tab, e) )
        #         return

        # insert_line = None
        # replace_line = None

        # if class_based_views_available:
        #     views = [ x.name for x in ast.parse(data).body if isinstance(x, ast.ClassDef) ]   # BEST PYTHON WAY TO DO THIS
        #     view_name = render_ctx['page_class']
        #     view_import_path = "views.%s.as_view()" % (view_name)
        #     render_ctx['view_import_path'] = view_import_path

        #     # CHECK IMPORT LINES
        #     importers = { v.module : v for v in ast.parse(data).body if isinstance(v, ast.ImportFrom) }

        #     if not importers:
        #         insert_line = (0, "from django.views.generic import %s\n\n" % (view_class))
        #     else:
        #         if "django.views.generic" in importers:
        #             name_list = [ x.name for x in importers["django.views.generic"].names ]

        #             if view_class not in name_list:
        #                 print("Adde Module into line: %d -> %s" % (importers["django.views.generic"].lineno, view_class ) )     # NEED AUTOMATIC WAY TO INSERT THIS
        #         else:
        #             # GET THE LAST IMPORT LINE
        #             import_number = 0
        #             insert_line = (import_number, "from django.views.generic import %s\n" % (view_class) )

        # else:
        #     views = [ x.name for x in ast.parse(data).body if isinstance(x, ast.FunctionDef) ]   # BEST PYTHON WAY TO DO THIS
        #     view_name = ("%(page)s_view" % render_ctx)
        #     view_import_path = "%(app)s.views.%(page)s_view" % render_ctx
        #     render_ctx['view_import_path'] = view_import_path

        # url_name = "%(app)s-%(page)s" % render_ctx
        # render_ctx['url_name'] = url_name
        # template = "%(app)s/%(page)s.html" % render_ctx

        # FILE = open(view_file, "r")
        # lines = FILE.readlines()
        # FILE.close()
        # #lines = [ x.strip() for x in FILE.readlines() ]    # WILL STRIP OFF TABS
        # dirty = False

        # if insert_line:
        #     lines.insert( insert_line[0], insert_line[1] )
        #     dirty = True

        # # If the new page name is not in the views.py, add the stub
        # if view_name not in views:
        #     self.stdout.write( "ADDING: %s to %s\n" % (render_ctx['page'], view_file) )
        #     dirty = True

        #     if class_based_views_available:
        #         # CHECK FOR IMPORT LINE IN FILE

        #         lines.extend( [ "##-" + "-" * len(render_ctx["page_name"]) + "\n",
        #                         "## %(page_name)s\n\n" % render_ctx,
        #                         "class %s(%s):\n" % (view_name, view_class),
        #                         render_ctx['tab'] + "template_name = '%s'\n\n\n" % template ] )
        #     else:
        #         lines.extend( [ "def %s(request):\n" % view_name,
        #                         render_ctx['tab'] + "ctx = Requestrender_ctx(request)\n",
        #                         render_ctx['tab'] + "return render_to_response('%s', ctx )\n" % template ] )

        # else:
        #     self.stdout.write( "EXISTING VIEWS: %s\n" % ", ".join(views) )

        # if dirty:
        #     FILE = open(view_file, "w")
        #     FILE.writelines( lines )
        #     FILE.close()

        # # Create the template stub
        # # todo: check to see if the template should be written in the project root or app directory
        # template_file = "templates/%s" % template

        # # Need to check for directory and add it if it is missing from the template directory
        # if not os.path.isfile(template_file):

        #     dest_path = "templates/%(app)s" % render_ctx
        #     if not os.path.exists(dest_path):
        #         os.makedirs(dest_path)

        #     self.stdout.write( "ADDING HTML TEMPLATE FILE: %s\n" % template_file )
        #     FILE = open( template_file, "w" )
        #     template = env.get_template('page.html.j2')
        #     FILE.write( template.render(**render_ctx) )
        #     FILE.close()

        # url_file = "%(app)s/urls.py" % render_ctx

        # #################
        # # UPDATE THE urls.py FILE

        # render_ctx['page_link'] = "%(page)s/" % render_ctx

        # if render_ctx['page'] == "index":
        #     render_ctx['page_link'] = ""

        # if os.path.isfile(url_file):
        #     '''
        #     If there is a urls.py file do this
        #     '''
        #     try:
        #         FILE = open(url_file, "r")
        #         data = FILE.read()
        #         urls = url_entry_regex.findall( data )
        #         FILE.close()

        #     except IOError as e:
        #         print( "IO Error reading %s, Step Skipped.\n\t%s" % (view_file, e) )

        #     if render_ctx['view_import_path'] + "," not in urls:   # Make sure to add the comma, which is caught by the regex pattern
        #         FILE = open(url_file, "a")

        #         # TODO: REBUILD THE WHOLE FILE WITH THE URLs INSERTED INTO THE LIST RATHER THAN APPEND

        #         if class_based_views_available:
        #             if version_check("gte", "1.10.0"):
        #                 url_py = "urlpatterns += [\n%(tab)surl(r'^%(page_link)s$', %(view_import_path)s, name='%(url_name)s')\n]" % (render_ctx)
        #             else:
        #                 url_py = "urlpatterns += patterns('',\n%(tab)surl(r'^%(page_link)s$', %(view_import_path)s, name='%(url_name)s'),\n)" % (render_ctx)
        #         else:
        #             url_py = "urlpatterns += patterns('',\n%(tab)surl(r'^%(page_link)s$', '%(view_import_path)s', name='%(url_name)s'),\n)" % (render_ctx)

        #         FILE.write( url_py + "\n" )
        #         FILE.close()

        # else:
        #     '''
        #     If there is no urls.py file do this
        #     '''
        #     FILE = open(url_file, "w")

        #     if version_check("gte", "1.10.0"):
        #         url_py = ["from django.conf.urls import url", "from . import views\n" % render_ctx, "urlpatterns = [" ]
        #         post_append = "]"
        #     elif version_check("gte", "1.5.0"):
        #         url_py = ["from django.conf.urls import *", "from %(app)s import views\n" % render_ctx, "urlpatterns = patterns(''," ]
        #         post_append = ")"
        #     else:
        #         url_py = ["from django.conf.urls import *\n", "urlpatterns = patterns(''," ]
        #         post_append = ")"

        #     if class_based_views_available:
        #         url_py.append(   "%(tab)surl(r'^%(page_link)s$', %(view_import_path)s, name='%(url_name)s'),\n)" % ( render_ctx ) )
        #     else:
        #         url_py.append(   "%(tab)surl(r'^%(page_link)s$', '%(view_import_path)s', name='%(url_name)s'),\n)" % ( render_ctx ) )

        #     url_py.append(post_append)

        #     FILE.write( "\n".join(url_py) + "\n" )
        #     FILE.close()


    def print_break(self, lable):
        count = 20
        self.stdout.write( "\n" + "*" * count + "\n" )
        self.stdout.write( "%s\n" % lable )
        self.stdout.write( "*" * count + "\n" )


