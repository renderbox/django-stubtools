from django.core.management.base import AppCommand, CommandError
import re, os.path

class Command(AppCommand):
    args = '<app page_name>'
    help = 'creates a template and matching method for a given page name'

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError('Need to pass App and Page names')

        # Using a Dictionary for clarity in strin replacements
        argDict = {'app':args[0], 'page':args[1]}

        # regex pattern to help find python methods
        # will need to be updated to handle Class Based Views
        view_method_regex = re.compile("def (\w+)\(.+\):")
        #class_method_regex = re.compile("class (\w+)\(.+\):")
        url_entry_regex = re.compile("url\(\S+ '(\S+)'" )
        
        view_file = "%(app)s/views.py" % argDict
        
        methods = []
        
        # Get a list of methods in the file
        if os.path.isfile(view_file): 
            try:
                FILE = open(view_file, "r")
                data = FILE.read()
                methods = view_method_regex.findall( data )
                FILE.close()

            except IOError as e:
                pass                    # May need to add something here
                                        # to handle a file locking issue
            
        # If the new page name is not in the views.py, add the stub
        if ("%(page)s_view" % argDict) not in methods:
        
            self.stdout.write( "ADDING METHOD: %s to %s\n" % (argDict['page'], view_file) )
            FILE = open(view_file, "a")
            lines = ["\ndef %(page)s_view(request):" % argDict, 
                     "\tctx = RequestContext(request)",
                     "\treturn render_to_response('%(app)s/%(page)s.html', ctx )\n" % argDict ]

            FILE.write( "\n".join(lines) )
            FILE.close()
        else:
            self.stdout.write( "EXISTING METHODS: %s\n" % ", ".join(methods) )

        # Create the template stub
        template_file = "templates/%(app)s/%(page)s.html" % argDict
        
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

        if os.path.isfile(url_file): 
            try:
                FILE = open(url_file, "r")
                data = FILE.read()
                urls = url_entry_regex.findall( data )
                FILE.close()

            except IOError as e:
                pass                    # May need to add something here

            if "%(app)s.views.%(page)s_view" % argDict not in urls:
                self.stdout.write( "Needs to be added\n" )

                # Just a print out line for the urls.py
                # need to update this to have the tool add to the app's urls.py
                self.print_break("Goes into url.py")
                self.stdout.write( "\n" )
                self.stdout.write( "url(r'^%(page)s/$', '%(app)s.views.%(page)s_view', name='%(app)s-%(page)s')," % argDict )
                self.stdout.write( "\n" * 2 )

        else:
            FILE = open(url_file, "w")

            url_py = ["from django.conf.urls.defaults import *\n",
            "urlpatterns = patterns('',",
            "\turl(r'^%(page)s/$', '%(app)s.views.%(page)s_view', name='%(app)s-%(page)s'),\n)" % argDict ]

            FILE.write( "\n".join(url_py) + "\n" )
            FILE.close()


    def print_break(self, lable):
        count = 20
        self.stdout.write( "\n" + "*" * count + "\n" )
        self.stdout.write( "%s\n" % lable )
        self.stdout.write( "*" * count + "\n" )
