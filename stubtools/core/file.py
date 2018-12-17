# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-08 11:30:11
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-16 21:35:47
# --------------------------------------------

import os
import ast

from .astparse import ast_first_line_number, ast_last_line_number, ast_parse_defaults, \
                        ast_class_inheritence_chain, ast_parse_expression_name, ast_parse_args, \
                        ast_parse_expression_args

def write_file(file_path, data, create_path=True):
    full_path = os.path.abspath(file_path)          # Make it a full path to reduce issues in parsing direcotry from file
    file_directory = os.path.dirname(full_path)

    # Check the directory exists
    if not os.path.exists(file_directory):
        # Create the full path if needed
        os.makedirs(file_directory)

    FILE = open(full_path, "w")
    FILE.write(data)
    FILE.close()


class PythonFileParser():

    structure = {}
    data_lines = []
    write_files = True

    def __init__(self, file_path=None):

        self.file_path = file_path

        if file_path:
            self.load_file()

    def load_file(self):
        if os.path.isfile(self.file_path):
            FILE = open( self.file_path, "r")
            data = FILE.read()
            FILE.close()
        else:
            self.data_lines = []

        self.prepare_data(data)
        self.ast_parse_code()
        self.set_import_slice()

    def load_string(self, data):
        '''
        Similar to load_file but allows you to pass in a string of code.
        '''
        self.prepare_data(data)
        self.ast_parse_code()
        self.set_import_slice()

    def prepare_data(self, data):
        self.data = data
        self.data_lines = self.data.splitlines()

        self.data_by_line = ['']      # Replace data_lines eventually with this.  It matches the index number with the line number to more easily be managed.
        self.data_by_line.extend(self.data_lines)

    def ast_parse_code(self):
        '''
        This is a tool that will return information about the Python code handed to it.
        It can be used by tools to figure out where the last line of code is and where import
        lines exist.  This is working to replace the use of regex to parse files.
        '''
        # data = "".join(self.data_lines)
        tree = ast.parse(self.data)

        self.structure = {'imports':[], 'functions':[], 'classes':[], 'expressions':[], 'assignments':[], 'root':tree, 'linecount':len(self.data_lines)}

        self.structure['first_line'] = ast_first_line_number(tree)
        self.structure['last_line'] = ast_last_line_number(tree)

        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                self.structure['imports'].append( self.ast_parse_import(node) )
            if isinstance(node, ast.FunctionDef):
                self.structure['functions'].append( self.ast_parse_function(node) )
            if isinstance(node, ast.ClassDef):
                self.structure['classes'].append( self.ast_parse_class(node) )
            if isinstance(node, ast.Expr):
                self.structure['expressions'].append( self.ast_parse_expression(node) )
            if isinstance(node, ast.Assign):
                self.structure['assignments'].append( self.ast_parse_assignments(node) )

        # Determine the first and last import lines
        self.structure['first_import_line'], self.structure['last_import_line'] = self.ast_first_and_last_line(self.structure['imports'])

        # Determine the first and last class/function lines
        self.structure['first_function_line'], self.structure['last_function_line'] = self.ast_first_and_last_line(self.structure['functions'])
        self.structure['first_class_line'], self.structure['last_class_line'] = self.ast_first_and_last_line(self.structure['classes'])
        self.structure['first_expression_line'], self.structure['last_expression_line'] = self.ast_first_and_last_line(self.structure['expressions'])
        self.structure['first_assignment_line'], self.structure['last_assignment_line'] = self.ast_first_and_last_line(self.structure['assignments'])

        code = []
        code.extend(self.structure['functions'])
        code.extend(self.structure['classes'])
        code.extend(self.structure['expressions'])
        code.extend(self.structure['assignments'])

        self.structure['first_code_line'], self.structure['last_code_line'] = self.ast_first_and_last_line(code)

        self.structure['from_list'] = [ f['from'] for f in self.structure['imports'] ]      # Used to see if a line is already imported
        self.structure['function_list'] = [ f['name'] for f in self.structure['functions'] ]      # Used to see if a line is already imported
        self.structure['class_list'] = [ f['name'] for f in self.structure['classes'] ]      # Used to see if a line is already imported


    def get_import_block(self, modules=[]):
        '''
        modules format is a List of Tuples of items to import
        The first entry is the 'from' and the remaining are the 'imports'
        If there is only one entry in the Tuple, that should be imported as is.

        # Examples:
        [   ("from", "import_1", "import_2", "import_3",),
            ("import",),
            ("from", "import_1",) ]
        '''
        if self.structure['first_import_line'] == None:     # If there is no import block, return None
            return None

        result = self.data_by_line[self.structure['first_import_line']:self.structure['last_import_line'] + 1]

        # print("MODULES:")
        # print(modules)

        print(self.structure)

        for module in modules:

            if len(module) > 1:
                from_check = module[0]

                if from_check.startswith("."):
                    from_check = from_check[1:]   # Strip off the first "." since AST ignores it and it does not make it into the structure
                
                from_path = module[0]
                import_mods = module[1:]
            else:   # assume it's just the import

                print("Single Entry")
                print(module)
                print(type(module))

                mod = module[0]

                if mod.startswith("."):
                    mod = mod[1:]   # Strip off the first "." since AST ignores it and it does not make it into the structure

                from_check = None
                from_path = None
                import_mods = [ module[0] ]

            # print("from_check: %s" % from_check)
            # print("from_path: %s" % from_path)

            for mod in import_mods:
                # Go through each mod to see if it's already in the list of mods
                append = True

                for imp in self.structure['imports']:

                    if from_check == imp['from']:
                        append = False      # No longer try to append the line, look to update it

                        # Check the imports to see if it's already included
                        extend_list = list([x for x in import_mods if x not in imp['import']])

                        # print("EXTEND LIST: %s" % imp['from'])
                        # print(extend_list)

                        if extend_list:
                            # If there is anything to append...
                            new_import_list = []
                            new_import_list.extend(imp['import'])
                            new_import_list.extend(extend_list)

                            # Modify the import line
                            mod_line_index_number = imp['first_line'] - self.structure['first_import_line']
                            # print("MODE LINE INDEX: %d" % mod_line_index_number)
                            comment = "#".join(result[mod_line_index_number].split("#")[1:] )     # Try to capture any comments on the line and preserve them

                            if from_path != None:
                                result[mod_line_index_number] = "from %s import %s" % (from_path, ", ".join(new_import_list) )
                            else:
                                result[mod_line_index_number] = "import %s" % ( ", ".join(new_import_list) )

                            if comment: # Append the comment
                                result[mod_line_index_number] = result[mod_line_index_number] + "    #" + comment

                # If it's not present, append it to the list of imports
                if append:
                    # print("APPENDING")
                    if from_path != None:
                        result.append("from %s import %s" % (from_path, ", ".join(import_mods) ) )
                    else:
                        result.append("import %s" % ( ", ".join(import_mods) ) )

        # print(result)

        return "\n".join(result)

    def set_import_slice(self, module=None):
        '''
        Rules:
        - If a module is present in the file, the header ends the line before.  The assumption will be that this is the line your want to update.
        - If there is no module passed, return up to the last import line
        - If there are no import lines, return an empty string
        '''

        # Set Header End...
        header_end_index = None
        footer_start_index = None

        if self.structure['first_code_line'] == None:
            body_start_index = self.structure['first_code_line']
        else:
            body_start_index = self.structure['first_code_line'] - 1

        if self.structure['first_code_line'] == None:               # If there is no code in the file...
            body_end_index = self.structure['last_code_line']
        else:
            body_end_index = self.structure['last_code_line'] - 1   # 'line' values start at 1, 'index' values start at 0

        # HEADER
        if self.structure['last_import_line'] != None:
            # print("LOOKING FOR %s" % module)

            from_check = module

            if module:
                if module.startswith("."):      # AST does not provide the '.' as part of the name when loading a local path module
                    from_check = module[1:]

            if from_check and from_check in self.structure['from_list']:    # if the module passed in is in the Python File, use that
                i = self.structure['from_list'].index(from_check)
                # print("MODULE FOUND AT: %d" % self.structure['imports'][i]['node'].lineno)
                header_end_index = self.structure['imports'][i]['node'].lineno - 2
                body_start_index = self.structure['imports'][i]['node'].lineno
            else:
                header_end_index = self.structure['last_import_line']           # WORKS CORRECTLY

        # FOOTER
        if self.structure['last_code_line'] != None and self.structure['last_code_line'] > header_end_index:
            footer_start_index = self.structure['last_code_line']

        if body_start_index and footer_start_index == None:     # If there is no footer, but there is a body, body should go to the end of the lines
            body_end_index = self.structure['last_line'] - 1

        self.structure['header_end_index'] = header_end_index
        self.structure['body_start_index'] = body_start_index
        self.structure['body_end_index'] = body_end_index
        self.structure['footer_start_index'] = footer_start_index

    def get_text_slice(self, start_index, end_index):
        '''
        Returns the string, from start, up to and including the end_index
        '''
        return "".join(self.data_lines[start_index:end_index + 1])

    def get_text_slice_by_line(self, start_line, end_line):
        '''
        Returns the string, from start, up to and including the end_index
        '''
        return "\n".join(self.data_by_line[start_line:end_line + 1])

    def get_header(self, module=None):  # DEPRECATED
        if self.structure['header_end_index'] != None:
            return self.get_text_slice(0, self.structure['header_end_index'])
        return ""

    def new_get_header(self):
        # This will capture everything up until the first import line
        if self.structure['first_import_line'] != None:
            return "\n".join(self.data_by_line[1:self.structure['first_import_line']])
        return ""

    def get_body(self, module=None):  # DEPRECATED
        # body_start_index, body_end_index = self.get_body_start_end_indexes(module=module)
        if self.structure['body_start_index'] != None:
            return self.get_text_slice(self.structure['body_start_index'], self.structure['body_end_index'])
        return ""

    def new_get_body(self):
        # This will capture everything up until the first import line
        if self.structure['last_import_line'] != None:
            return self.get_text_slice_by_line(self.structure['last_import_line'] + 1, self.structure['last_line'] + 1)
        return ""

    def get_footer(self):
        if self.structure['footer_start_index'] != None:
            return self.get_text_slice(self.structure['footer_start_index'], -1)
        return ""

    def ast_first_and_last_line(self, items):
        '''
        Given a bunch of AST nodes, figure out which is the first and last line
        '''
        first = None
        last = None

        if items:
            for item in items:
                if first == None or item['first_line'] < first:
                    first = item['first_line']

                if last == None or item['last_line'] > last:
                    last = item['last_line']

        return first, last

    def ast_parse_import(self, node):
        result = ast_parse_defaults(node)
        result['from'] = node.module
        result['import'] = [x.name for x in node.names]
        return result

    def ast_parse_class(self, node):
        result = ast_parse_defaults(node)
        result['name'] = node.name
        result['inheritence_chain'] = ast_class_inheritence_chain(node)
        return result

    def ast_parse_function(self, node):
        result = ast_parse_defaults(node)
        result['name'] = node.name
        result['args'] = ast_parse_args(node)
        return result

    def ast_parse_expression(self, node):
        result = ast_parse_defaults(node)
        result['name'] = ast_parse_expression_name(node)
        result['args'] = ast_parse_expression_args(node)   #list([arg.id for arg in node.value.args])
        # result['args'] = ast_parse_args(node.value)
        return result

    def ast_parse_assignments(self, node):
        result = ast_parse_defaults(node)
        result['name'] = node.targets[0].id

        # if isinstance(node.value, ast.List):
        # Parse the list

        return result

    def get_import_line(self, module):
        '''
        Returns where an module is imported.  'None' is returned if not already included.
        '''
        result = None

        for imp in self.structure['imports']:
            if  imp['from'] == module:
                result = imp['first_line']

        return result

    def create_import_statement(self, module, path=None, sort=False):
        '''
        example:
        path = django.db
        module = MyModel
        '''
        mod_list = []                   # Start with just the required
        comment = ""

        from_check = path

        if from_check.startswith("."):
            from_check = from_check[1:]

        if from_check in self.structure['from_list']:             # if the module passed in is in the Python File, use that
            i = self.structure['from_list'].index(from_check)
            mod_list.extend( self.structure['imports'][i]['import'] )
            print("EXTENDING THE MODULE LIST")

            # Look for comment and append if needed
            parts = self.data_lines[ self.structure['imports'][i]['node'].lineno - 1 ].split("#")    # Split off any comments
            if len(parts) > 1:
                comment = "#".join(parts[1:])

        if module not in mod_list:
            mod_list.append(module)

        print("MOD LIST")
        print(mod_list)

        if sort:
            mod_list.sort()             # Sort the modules

        if path:
            result = "from %s import %s" % ( path, ", ".join(mod_list) )
        else:
            result = "import %s" % ( ", ".join(mod_list) )

        if comment:
            result += "    # %s" % comment

        return result
