from django.core.management.base import AppCommand, CommandError
import re, os.path
from stubcore import underscore_camel_case

class Command(AppCommand):
    args = '<app.model_name>'
    help = 'creates stub Templates, Forms and Admin entries for a given model name'
    class_regex = re.compile(r"class (\w+)\(.+\):")
    import_line_regex = re.compile(r"^from django.db import (.+)", re.MULTILINE)
    imports_regex = re.compile(r"(import|from)")
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
        
        import_line = False
        import_entry = False
        first_class_line = 0
        last_import_line = 0
        
        # LOAD FILE
        if os.path.isfile( model_file ): 
            try:
                FILE = open( model_file, "r")
                data = FILE.read()
                
                model_import = self.import_line_regex.findall( data )
                
                if model_import:
                    import_line = True
                    
                    for line in model_import:
                        if 'models' in [x.strip() for x in line.split(",") ]:
                            import_entry = True
                            
                classes = self.class_regex.findall( data )
                FILE.close()

            except IOError as e:
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
            # FIND WHERE TO ADD THE IMPORT LINE
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
        
            # CREATE IMPORT LINE
            
            # ADD TO IMPORT LINE
        
        mf = open( model_file, "a" )
        mf.write("\n\n\nclass %s(models.Model):\n    name = models.CharField(max_length=300)" % model )
        mf.close()
