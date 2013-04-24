from django.core.management.base import AppCommand, CommandError
import re, os.path
from stubtools.core import underscore_camel_case, import_line_check, class_name


class Command(AppCommand):
    args = '<app.model_name>'
    help = 'creates stub Templates, Forms and Admin entries for a given model name'
    import_line_regex = re.compile(r"^from django.db import (.+)", re.MULTILINE)
    import_uget_regex = re.compile(r"^from django.utils.translation import (.+)", re.MULTILINE)
    imports_regex = re.compile(r"(import|from)")
    class_regex = re.compile(r"class (\w+)\(.+\):")
    func_regex = re.compile(r"(def|class)")
    

    def handle(self, *args, **options):
        
        if not args:
            print "No Arguments Passed"
            return
        
        for entry in args:
            app, model = entry.split(".")
            print("CHECKING FOR MODEL: %s" % model)
            self.process(app, model)
        
        
    def process(self, app, model, *args, **kwargs):
        model_file = "%s/models.py" % app
        print("MODEL FILE: %s" % model_file)
        
        import_entry = False
        first_class_line = 0
        last_import_line = 0
        new_lines = []

        # MAKE SURE THE MODEL NAME'S FIRST LETTER IS CAPITALIZED
        model = class_name(model)
        
        # LOAD FILE
        if os.path.isfile( model_file ): 
            try:
                FILE = open( model_file, "r")
                data = FILE.read()

                if not import_line_check(self.import_line_regex, data, 'models'):
                    new_lines.append("from django.db import models")

                if not import_line_check(self.import_uget_regex, data, 'ugettext_lazy as _'):
                    new_lines.append("from django.utils.translation import ugettext_lazy as _")

                classes = self.class_regex.findall( data )
                FILE.close()

            except IOError as e:
                print "IO ERROR, CONTINUE"
                pass                    # May need to add something here
                                        # to handle a file locking issue
        else:
            print( "File Not Found: %s" % model_file )
            return

        # LOOK FOR CLASS WITH NAME
        if model in classes:
            print('Model Exists: %s' % model)
            return

        print('Creating Model: %s' % model)
        
        if not import_entry:
            # FIND WHERE TO ADD THE IMPORT LINES
            
            lines = []
            for m in re.finditer( self.func_regex, data ):
                lines.append( data.count("\n",0,m.start())+1 )
        
            if lines:
                lines.sort()
                first_class_line = lines[0]
        
            print "[%d]" % ( first_class_line )

            lines = []
            for m in re.finditer( self.imports_regex, data ):
                lineno = data.count("\n",0,m.start())+1
                if lineno < first_class_line:
                    lines.append(lineno)
                #print "[%d] %s" % (lineno, data[ m.start() : m.end() ] )
            if lines:
                lines.sort()
                last_import_line = lines[-1]
        
            print "[%d]" % ( last_import_line )
        
        # ADD THE MODEL TO THE LINES
        new_lines.append('\n\nclass %s(models.Model):\n    name = models.CharField(_("Name"), max_length=300)' % model)
        new_lines.append(" ")

        mf = open( model_file, "a" )
        # NEEDS TO LOAD AND REWRITE THE FILE RATHER THAN JUST APPEND
        mf.write( "\n".join(new_lines) )
        mf.close()
