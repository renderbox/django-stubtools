#--------------------------------------------
# Copyright 2017, Grant Viklund
# @Author: Grant Viklund
# @Date:   2017-02-20 13:50:51
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2017-04-06 12:53:17
#--------------------------------------------

from django.core.management.base import AppCommand, CommandError
from stubtools.core import class_name, version_check
import re, os.path
import ast
import django

class Command(AppCommand):
    args = '<app page_name>'
    help = 'creates a template and matching view for a given page name'

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Need to pass App.Page names')

        parts = args[0].split(".")

        if not parts[1][0].isupper():    # Make sure the first letter is uppercase
            parts[1] = parts[1][0].upper() + parts[1][1:]

        name_split_regex = re.compile("([A-Z][a-z]+)")    # Splits the CammelCase naming
        name_parts = name_split_regex.findall(parts[1])

        if name_parts[-1] == "View":
            page_class = parts[1]
            name_parts.pop(-1)
        else:
            page_class = parts[1]+"View"

        # Using a Dictionary for clarity in strin replacements
        argDict = {'app':parts[0], 'page':"_".join(name_parts).lower(), 'pageClass':page_class, 'pageName':' '.join(name_parts) }
        tab = "\t"
        argDict['tab'] = " " * 4

        use_class_based_views = version_check("gte", "1.3.0")        # SHOULD DEFAULT FOR 1.3+ TO True.  NEED ATTR IN settings.py TO CONFIG SET TO FALSE.

        view_file = "%(app)s/views.py" % argDict
        argDict['view_file'] = view_file

        views = []

        if use_class_based_views:
            url_entry_regex = re.compile("url\(\S+ (\S+)" )
        else:
            url_entry_regex = re.compile("url\(\S+ '(\S+)'" )

        # Get contents of views.py file
        if os.path.isfile(view_file):
            try:
                FILE = open(view_file, "r")
                data = FILE.read()
                FILE.close()
            except IOError as e:
                print( "IO Error reading %s\n\t%s" % (view_file, tab, e) )
                return

        insert_line = None
        replace_line = None

        if use_class_based_views:
            views = [ x.name for x in ast.parse(data).body if isinstance(x, ast.ClassDef) ]   # BEST PYTHON WAY TO DO THIS
            view_name = argDict['pageClass']
            view_import_path = "views.%s.as_view()" % (view_name)
            argDict['view_import_path'] = view_import_path

            # CHECK IMPORT LINES
            importers = { v.module : v for v in ast.parse(data).body if isinstance(v, ast.ImportFrom) }

            if not importers:
                insert_line = (0, "from django.views.generic import TemplateView\n\n")
            else:
                if "django.views.generic" in importers:
                    name_list = [ x.name for x in importers["django.views.generic"].names ]

                    if "TemplateView" not in name_list:
                        print("Adde Module into line: %d -> %s" % (importers["django.views.generic"].lineno, "TemplateView" ) )     # NEED AUTOMATIC WAY TO INSERT THIS
                else:
                    # GET THE LAST IMPORT LINE
                    import_number = 0
                    insert_line = (import_number, "from django.views.generic import TemplateView\n")

        else:
            views = [ x.name for x in ast.parse(data).body if isinstance(x, ast.FunctionDef) ]   # BEST PYTHON WAY TO DO THIS
            view_name = ("%(page)s_view" % argDict)
            view_import_path = "%(app)s.views.%(page)s_view" % argDict
            argDict['view_import_path'] = view_import_path

        url_name = "%(app)s-%(page)s" % argDict
        argDict['url_name'] = url_name
        template = "%(app)s/%(page)s.html" % argDict

        FILE = open(view_file, "r")
        lines = FILE.readlines()
        FILE.close()
        #lines = [ x.strip() for x in FILE.readlines() ]    # WILL STRIP OFF TABS
        dirty = False

        if insert_line:
            lines.insert( insert_line[0], insert_line[1] )
            dirty = True

        # If the new page name is not in the views.py, add the stub
        if view_name not in views:
            self.stdout.write( "ADDING: %s to %s\n" % (argDict['page'], view_file) )
            dirty = True

            if use_class_based_views:
                # CHECK FOR IMPORT LINE IN FILE

                lines.extend( [ "##-" + "-" * len(argDict["pageName"]) + "\n",
                                "## %(pageName)s\n\n" % argDict,
                                "class %s(TemplateView):\n" % view_name,
                                argDict['tab'] + "template_name = '%s'\n\n\n" % template ] )
            else:
                lines.extend( [ "def %s(request):\n" % view_name,
                                argDict['tab'] + "ctx = RequestContext(request)\n",
                                argDict['tab'] + "return render_to_response('%s', ctx )\n" % template ] )

        else:
            self.stdout.write( "EXISTING VIEWS: %s\n" % ", ".join(views) )

        if dirty:
            FILE = open(view_file, "w")
            FILE.writelines( lines )
            FILE.close()

        # Create the template stub
        template_file = "templates/%s" % template

        # Need to check for directory and add it if it is missing from the template directory
        if not os.path.isfile(template_file):

            dest_path = "templates/%(app)s" % argDict
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            self.stdout.write( "ADDING TEMPLATE FILE: %s\n" % template_file )
            FILE = open( template_file, "w" )
            html = ['{% extends "base.html" %}\n',
                    '{% block head_title %}' + ' - %(pageName)s'  % argDict + '{% endblock %}\n',
                    '{% block content %}',
                    '\t\t<div class="row">',
                    '\t\t\t<div class="col-md-12">',
                    '\t\t\t\t<h2>%(app)s - %(pageName)s, Stub Page</h2>' % argDict,
                    '\t\t\t\t<a href="{% url ' + "'%(url_name)s'" % argDict + ' %}">link</a>',
                    '\t\t\t</div>',
                    '\t\t</div>',
                    '{% endblock content %}']

            FILE.write( "\n".join(html) )

        url_file = "%(app)s/urls.py" % argDict

        #################
        # UPDATE THE urls.py FILE

        argDict['page_link'] = "%(page)s/" % argDict

        if argDict['page'] == "index":
            argDict['page_link'] = ""

        if os.path.isfile(url_file):
            '''
            If there is a urls.py file do this
            '''
            try:
                FILE = open(url_file, "r")
                data = FILE.read()
                urls = url_entry_regex.findall( data )
                FILE.close()

            except IOError as e:
                print( "IO Error reading %s, Step Skipped.\n\t%s" % (view_file, e) )

            if argDict['view_import_path'] + "," not in urls:   # Make sure to add the comma, which is caught by the regex pattern
                FILE = open(url_file, "a")

                # TODO: REBUILD THE WHOLE FILE WITH THE URLs INSERTED INTO THE LIST RATHER THAN APPEND

                if use_class_based_views:
                    if version_check("gte", "1.10.0"):
                        url_py = "urlpatterns += [\n%(tab)surl(r'^%(page_link)s$', %(view_import_path)s, name='%(url_name)s')\n]" % (argDict)
                    else:
                        url_py = "urlpatterns += patterns('',\n%(tab)surl(r'^%(page_link)s$', %(view_import_path)s, name='%(url_name)s'),\n)" % (argDict)
                else:
                    url_py = "urlpatterns += patterns('',\n%(tab)surl(r'^%(page_link)s$', '%(view_import_path)s', name='%(url_name)s'),\n)" % (argDict)

                FILE.write( url_py + "\n" )
                FILE.close()

        else:
            '''
            If there is no urls.py file do this
            '''
            FILE = open(url_file, "w")

            if version_check("gte", "1.10.0"):
                url_py = ["from django.conf.urls import url", "from . import views\n" % argDict, "urlpatterns = [" ]
                post_append = "]"
            elif version_check("gte", "1.5.0"):
                url_py = ["from django.conf.urls import *", "from %(app)s import views\n" % argDict, "urlpatterns = patterns(''," ]
                post_append = ")"
            else:
                url_py = ["from django.conf.urls import *\n", "urlpatterns = patterns(''," ]
                post_append = ")"

            if use_class_based_views:
                url_py.append(   "%(tab)surl(r'^%(page_link)s$', %(view_import_path)s, name='%(url_name)s'),\n)" % ( argDict ) )
            else:
                url_py.append(   "%(tab)surl(r'^%(page_link)s$', '%(view_import_path)s', name='%(url_name)s'),\n)" % ( argDict ) )

            url_py.append(post_append)

            FILE.write( "\n".join(url_py) + "\n" )
            FILE.close()


    def print_break(self, lable):
        count = 20
        self.stdout.write( "\n" + "*" * count + "\n" )
        self.stdout.write( "%s\n" % lable )
        self.stdout.write( "*" * count + "\n" )


