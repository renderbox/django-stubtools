from django.core.management.base import AppCommand, CommandError
from stubtools.core import class_name
import re, os.path
import ast

class Command(AppCommand):
    args = '<app page_name>'
    help = 'creates a template and matching method for a given page name'

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Need to pass App.Page names')
            
        parts = args[0].split(".")
        tab = "\t"

        # Using a Dictionary for clarity in strin replacements
        argDict = {'app':parts[0], 'page':parts[1].lower()}
        
        use_class_based_views = True        # SHOULD DEFAULT FOR 1.3+ TO True.  NEED ATTR IN settings.py TO CONFIG SET TO FALSE.
        
        #from django.views.generic import TemplateView
        view_file = "%(app)s/views.py" % argDict
        
        views = []
        url_entry_regex = re.compile("url\(\S+ '(\S+)'" )
        
        # Get contents of views.py file
        if os.path.isfile(view_file): 
            try:
                FILE = open(view_file, "r")
                data = FILE.read()
                FILE.close()
            except IOError as e:
                print( "IO Error reading %s\n\t%s" % (view_file, e) )
                return
        
        insert_line = None
        replace_line = None
        
        if use_class_based_views:
            views = [ x.name for x in ast.parse(data).body if isinstance(x, ast.ClassDef) ]   # BEST PYTHON WAY TO DO THIS
            view_name = ( "%sView" % ( class_name( argDict['page'] ) ) )
            view_import_path = "%s.views.%s.as_view()" % (argDict['app'], view_name)
            
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
            
        url_name = "%(app)s-%(page)s" % argDict
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

                lines.extend( [ "class %s(TemplateView):\n" % view_name, 
                                tab + "template_name = '%s'\n\n\n" % template ] )
            else:
                lines.extend( [ "def %s(request):\n" % view_name, 
                                tab + "ctx = RequestContext(request)\n",
                                tab + "return render_to_response('%s', ctx )\n" % template ] )
            
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
            html = ['<!DOCTYPE html>',
                    '<html>',
                    '<head>',
                    '<meta charset="utf-8">',
                    '\t<title>%(app)s - %(page)s</title>' % argDict,
                    '</head>',
                    '<body>',
                    '\t<h1>%(app)s - %(page)s, Stub Page</h1>' % argDict,
                    '\t<a href="{% url ' + '%(app)s-%(page)s' % argDict + ' %}">link</a>',
                    '</body>\n</html>']

            FILE.write( "\n".join(html) )

        url_file = "%(app)s/urls.py" % argDict

        #################
        # UPDATE THE urls.py FILE

        if os.path.isfile(url_file): 
            try:
                FILE = open(url_file, "r")
                data = FILE.read()
                urls = url_entry_regex.findall( data )
                FILE.close()

            except IOError as e:
                print( "IO Error reading %s, Step Skipped.\n\t%s" % (view_file, e) )
            
            if view_import_path not in urls:
                FILE = open(url_file, "a")

                if argDict['page'] == "index":
                    url_py = "urlpatterns += patterns('',\n\turl(r'^/$', '%s', name='%s'),\n)" % (view_import_path, url_name)
                else:
                    url_py = "urlpatterns += patterns('',\n\turl(r'^%s/$', '%s', name='%s'),\n)" % (argDict['page'], view_import_path, url_name)

                FILE.write( url_py + "\n" )
                FILE.close()
                

        else:
            FILE = open(url_file, "w")

            url_py = ["from django.conf.urls.defaults import *\n", "urlpatterns = patterns(''," ]
            
            if argDict['page'] == "index":
                url_py.append( "\turl(r'^/$', '%s', name='%s'), )" % ( view_import_path, url_name ) )
            else:
                url_py.append( "\turl(r'^%s/$', '%s', name='%s'), )" % ( argDict['page'], view_import_path, url_name ) )

            FILE.write( "\n".join(url_py) + "\n" )
            FILE.close()


    def print_break(self, lable):
        count = 20
        self.stdout.write( "\n" + "*" * count + "\n" )
        self.stdout.write( "%s\n" % lable )
        self.stdout.write( "*" * count + "\n" )
