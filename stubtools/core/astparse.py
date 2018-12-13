# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-14 15:34:48
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-12 15:29:43
# --------------------------------------------

import ast

##############
# AST Parsing
##############

def ast_parse_code(tree):
    '''
    This is a tool that will return information about the Python code handed to it.
    It can be used by tools to figure out where the last line of code is and where import
    lines exist.  This is working to replace the use of regex to parse files.
    '''
    result = {'imports':[], 'functions':[], 'classes':[], 'root':tree}

    result['first_line'] = ast_first_line_number(tree)
    result['last_line'] = ast_last_line_number(tree)

    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            result['imports'].append( ast_parse_import(node) )
        if isinstance(node, ast.FunctionDef):
            result['functions'].append( ast_parse_function(node) )
        if isinstance(node, ast.ClassDef):
            result['classes'].append( ast_parse_class(node) )

    # Determine the first and last import lines
    result['first_import_line'], result['last_import_line'] = ast_first_and_last_line(result['imports'])

    # Determine the first and last class/function lines
    result['first_function_line'], result['last_function_line'] = ast_first_and_last_line(result['functions'])
    result['first_class_line'], result['last_class_line'] = ast_first_and_last_line(result['classes'])

    code = []
    code.extend(result['functions'])
    code.extend(result['classes'])

    result['first_code_line'], result['last_code_line'] = ast_first_and_last_line(code)

    result['from_list'] = [ f['from'] for f in result['imports'] ]      # Used to see if a line is already imported
    result['function_list'] = [ f['name'] for f in result['functions'] ]      # Used to see if a line is already imported
    result['class_list'] = [ f['name'] for f in result['classes'] ]      # Used to see if a line is already imported

    return result

def ast_first_and_last_line(items):
    first = None
    last = None

    if items:
        for item in items:
            if first == None or item['first_line'] < first:
                first = item['first_line']

            if last == None or item['last_line'] > last:
                last = item['last_line']

    return first, last

def ast_parse_defaults(node):
    '''
    Things each node needs to have
    '''
    result = {}
    result['node'] = node
    result['first_line'] = ast_first_line_number(node)
    result['last_line'] = ast_last_line_number(node)

    return result


def ast_parse_import(node):
    result = ast_parse_defaults(node)
    result['from'] = node.module
    result['import'] = [x.name for x in node.names]
    return result


def ast_parse_class(node):
    '''
    todo: Append Meta info if present...
    '''
    result = ast_parse_defaults(node)
    result['name'] = node.name
    ichain = ast_class_inheritence_chain(node)

    if ichain:
        result['inheritence_chain'] = ichain

    if hasattr(node, "body"):
        for child in node.body:
            if isinstance(child, ast.ClassDef):
                cdata = ast_parse_class(child)

                if cdata['name'] == "Meta":
                    result['meta'] = cdata
                else:
                    if not 'nested_class' in result:
                        result['nested_class'] = []
                    result['nested_class'].append(cdata)
            # if isinstance(child, ast.Assign):
            #     if not 'attributes' in result:
            #         result['attributes'] = []

            #     if isinstance(child.value, ast.Name):
            #         result['attributes'].append({'target':", ".join([x.id for x in child.targets]), 'value': child.value.id})
            #     # if isinstance(child.value, ast.List):
            #     #     value = [x.elts for x in child.value]
            #     #     result['attributes'].append({'target':", ".join([x.id for x in child.targets]), 'value': value})

    return result


# def ast_value_tree(node):
#     '''Recursively Parse a Node Tree'''
#     result = {}
#     if isinstance(node, ast.ClassDef):


def ast_parse_function(node):
    result = ast_parse_defaults(node)
    result['name'] = node.name
    result['args'] = ast_parse_args(node)
    return result

def ast_parse_expression_name(node):
    '''
    Neet to rework this so the whole chain is figured out.

    exaple: admin.site.register(Category)
    
    like: 
        'value.func.value.value.id'='admin'
        'expn.value.func.value.attr'='site' 
        for registering an Admin to a Model.
    '''
    function_name = node.value.func.attr

    return function_name


    # result = []
    # for base in node.bases:
    #     if hasattr(base, 'id'):
    #         result.append(base.id)
    #     else:
    #         result.append(base.value.id + "." + base.attr)
    # return result
    

def ast_last_line_number(node, index= -1):
    '''
    returns the last line number for the node
    '''
    if hasattr(node, "body") and node.body:   # If it has the attr and it has a value...
        return ast_last_line_number(node.body[index], index=index)
    else:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
            # Need to check to handle Meta classes...
            if hasattr(node.value, 'elts') and len(node.value.elts) > 0:
                return ast_last_line_number(node.value.elts[-1])    # Get the last item in the list.  Trying to compensate for multiline assignments.
            elif hasattr(node.value, 'targets') and len(node.value.targets) > 0:
                return ast_last_line_number(node.value.targets[-1])

    return getattr(node, "lineno", None)    # Fall Through Result

    #     if hasattr(obj, "lineno"):
    #         return obj.lineno
    # return None     # Return None if there is no code present


def ast_first_line_number(node):
    '''
    returns the first line number for the node
    '''
    if isinstance(node, ast.Module):     # In the case of the top level tree, check the first item in the module's body to get the first line number.
        if node.body:
            node = node.body[0]
            return node.lineno
    else:
        return getattr(node, "lineno", None)


def ast_class_inheritence_chain(node):
    result = []
    for base in node.bases:
        if hasattr(base, 'id'):
            result.append(base.id)
        else:
            result.append(base.value.id + "." + base.attr)
    return result


def ast_parse_args(node):
    '''
    Parses the args passed into a function
    '''
    result = {'args':[], 'kwargs':[]}
    if isinstance(node, ast.Expr):
        args = node.value.args
    else:
        args = node.args.args
    defaults = node.args.defaults

    dlen = len(defaults)

    if dlen:
        result['args'] = [a.arg for a in args[:-1 * dlen]]
        result['kwargs'] = [{a.arg:ast_parse_arg_defaults(b)} for a, b in zip(args[-1 * dlen:], defaults)]
    else:
        result['args'] = [a.arg for a in args]

    return result

def ast_parse_expression_args(node):
    '''
    Parses the args passed into a function
    '''
    result = {'args':[], 'kwargs':[]}

    result['args'] = [arg.id for arg in node.value.args]
    result['kwargs'] = node.value.keywords

    return result


def ast_parse_arg_defaults(node):
    '''
    Going to have to update different value types as they are figured out.
    '''
    if hasattr(node, 's'):
        return node.s
    elif hasattr(node, 'n'):
        return node.n
    else:
        return None


'''
def parse_import(arg1, arg1, kwarg1="Foo", kwarg2=2):
    result = parse_defaults(tree)
    result['name'] = tree.module
    result['imports'] = [x.name for x in imp.names]
    return result
'''