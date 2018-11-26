# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-08 11:30:11
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-26 15:54:16
# --------------------------------------------

import os
import ast

from .astparse import ast_first_line_number, ast_last_line_number, ast_parse_defaults, ast_class_inheritence_chain

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

    def __init__(self, file_path):

        self.file_path = file_path

        self.load_file()

    def load_file(self):
        FILE = open( self.file_path, "r")
        self.data_lines = FILE.readlines()
        FILE.close()

        self.ast_parse_code()
        self.set_slice_indexes()

    def ast_parse_code(self):
        '''
        This is a tool that will return information about the Python code handed to it.
        It can be used by tools to figure out where the last line of code is and where import
        lines exist.  This is working to replace the use of regex to parse files.
        '''
        data = "".join(self.data_lines)
        tree = ast.parse(data)

        self.structure = {'imports':[], 'functions':[], 'classes':[], 'root':tree, 'linecount':len(self.data_lines)}

        self.structure['first_line'] = ast_first_line_number(tree)
        self.structure['last_line'] = ast_last_line_number(tree)

        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                self.structure['imports'].append( self.ast_parse_import(node) )
            if isinstance(node, ast.FunctionDef):
                self.structure['functions'].append( self.ast_parse_function(node) )
            if isinstance(node, ast.ClassDef):
                self.structure['classes'].append( self.ast_parse_class(node) )

        # Determine the first and last import lines
        self.structure['first_import_line'], self.structure['last_import_line'] = self.ast_first_and_last_line(self.structure['imports'])

        # Determine the first and last class/function lines
        self.structure['first_function_line'], self.structure['last_function_line'] = self.ast_first_and_last_line(self.structure['functions'])
        self.structure['first_class_line'], self.structure['last_class_line'] = self.ast_first_and_last_line(self.structure['classes'])

        code = []
        code.extend(self.structure['functions'])
        code.extend(self.structure['classes'])

        self.structure['first_code_line'], self.structure['last_code_line'] = self.ast_first_and_last_line(code)

        self.structure['from_list'] = [ f['from'] for f in self.structure['imports'] ]      # Used to see if a line is already imported
        self.structure['function_list'] = [ f['name'] for f in self.structure['functions'] ]      # Used to see if a line is already imported
        self.structure['class_list'] = [ f['name'] for f in self.structure['classes'] ]      # Used to see if a line is already imported


    def set_slice_indexes(self, module=None):
        '''
        Rules:
        - If a module is present in the file, the header ends the line before.  The assumption will be that this is the line your want to update.
        - If there is no module passed, return up to the last import line
        - If there are no import lines, return an empty string
        '''

        # Set Header End...
        header_end_index = None
        footer_start_index = None
        body_start_index = self.structure['first_code_line']
        body_end_index = self.structure['last_code_line']

        # HEADER
        if self.structure['last_import_line'] != None:
            if module and module in self.structure['from_list']:    # if the module passed in is in the Python File, use that
                i = self.structure['from_list'].index(module)
                header_end_index = self.structure['imports'][i]['node'].lineno - 1
                body_start_index = self.structure['imports'][i]['node'].lineno
            else:
                header_end_index = self.structure['last_import_line']

        # FOOTER
        if header_end_index == None:
            footer_start_index = self.structure['last_code_line']
        else:
            if self.structure['last_code_line'] != None and self.structure['last_code_line'] > header_end_index:
                footer_start_index = self.structure['last_code_line']
            else:
                footer_start_index = header_end_index

        self.structure['header_end_index'] = header_end_index
        self.structure['body_start_index'] = body_start_index
        self.structure['body_end_index'] = body_end_index
        self.structure['footer_start_index'] = footer_start_index


    def get_header(self, module=None):
        if self.structure['header_end_index'] != None:
            return "".join(self.data_lines[:self.structure['header_end_index']])
        return ""

    # def get_body_start_end_indexes(self, module=None):
    #     if module and module in self.structure['from_list']:    # if the module passed in is in the Python File, use that
    #         i = self.structure['from_list'].index(module)
    #         body_start_index = self.structure['imports'][i]['node'].lineno
    #     else:
    #         body_start_index = self.structure['last_import_line']   # If the module is not there, use this line to start

    #     return body_start_index, self.structure['last_code_line']   # Convert the line to an idex value


    def get_body(self, module=None):
        # body_start_index, body_end_index = self.get_body_start_end_indexes(module=module)
        if self.structure['body_start_index'] != None:
            return "".join(self.data_lines[self.structure['body_start_index']:self.structure['body_end_index']])
        return ""

    def get_footer(self):
        # return "".join(self.data_lines[self.structure['last_code_line']:])
        if self.structure['footer_start_index'] != None:
            return "".join(self.data_lines[self.structure['footer_start_index']:])
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

    def get_import_line(self, module):
        '''
        Returns where an module is imported.  'None' is returned if not already included.
        '''
        result = None

        for imp in self.structure['imports']:
            if  imp['from'] == module:
                result = imp['first_line']

        return result

