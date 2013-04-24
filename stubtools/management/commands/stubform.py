from django.core.management.base import AppCommand, CommandError
import re, os.path
from stubtools.core import underscore_camel_case

class Command(AppCommand):
    args = '<app.model_name>'
    help = 'creates stub model form entries'
    class_regex = re.compile(r"class (\w+)\(.+\):")
    import_line_regex = re.compile(r"^from django import (.+)", re.MULTILINE)
    imports_regex = re.compile(r"(import|from)")
    func_regex = re.compile(r"(def|class)")
    

    def handle(self, *args, **options):
        
        if not args:
            print "No Arguments Passed"
            return
        
        for entry in args:
            app, model = entry.split(".")
            print("CHECKING FOR MODEL FORM FOR: %s" % model)
            self.process(app, model)
        
        
    def process(self, app, model, *args, **kwargs):
        form_file = "%s/forms.py" % app
        print("FORM FILE: %s" % form_file)
        
        import_line = False
        import_entry = False
        first_class_line = 0
        last_import_line = 0
        modelform = model + "Form"
        
        # LOAD FILE
        if os.path.isfile( form_file ): 
            try:
                FILE = open( form_file, "r")
                data = FILE.read()
                
                form_import = self.import_line_regex.findall( data )
                
                if form_import:
                    import_line = True
                    
                    for line in form_import:
                        if 'forms' in [x.strip() for x in line.split(",") ]:
                            import_entry = True
                            
                classes = self.class_regex.findall( data )
                FILE.close()

            except IOError as e:
                pass                    # May need to add something here
                                        # to handle a file locking issue
        # LOOK FOR CLASS WITH NAME
        if modelform in classes:
            print('Form Exists: %s' % modelform)
            return

        print('Creating Form: %s' % modelform)

        import_model_regex = re.compile(r"^from %s.models import (.+)" % (app), re.MULTILINE)
        imported_models = import_model_regex.findall( data )
        
        if not import_entry or imported_models:
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
            
        if not import_entry:
            pass
        
        if imported_models:
            imported_models = [x.strip() for x in imported_models[0].split(',')]
        else:
            print "Adding Model with Import Line"
            
        
        #print imported_models
        
        if model not in imported_models:
            print "Adding Model to Import Line"
        
            # CREATE IMPORT LINE
            
            # ADD TO IMPORT LINE
        
        mf = open( form_file, "a" )
        mf.write("\n\nclass %s(forms.ModelForm):\n\n    class Meta:\n        model = %s" % (modelform, model) )
        mf.close()
