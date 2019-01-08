# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-12-18 10:27:42
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-21 15:15:15
# --------------------------------------------
import pprint

from stubtools.core.prompt import horizontal_rule

###
# Context Filters
# Applied as a post process in the context generation

def url_ctx_flter(ctx, parser):
    '''
    Take a context and further process it for Dajngo App URL files...
    '''

    pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(parser.structure)
    last_line = None

    for assignment in parser.structure.get('assignments', []):
        if assignment['name'] == "urlpatterns":
            last_line = assignment['last_line']

    if last_line:
        if parser.structure['header_end_index'] == None:     # i.e. If there is no header, start the body from the beginning of the file
            first_body_line = 1
        else:
            first_body_line = parser.structure['header_end_index'] + 2      # +2 because it's converting index to line value and starting at the next line

        ctx['body'] = parser.get_text_slice_by_line(first_body_line, last_line)    # First line of Body until where to add the URLs.
        ctx['footer'] = parser.get_text_slice_by_line(last_line + 1, parser.structure['linecount'] + 1)

    else:
        # If there is no "urlpatterns", move everything from the body to the header and set the body to a value None (So the template knows there is no body string)
        ctx['header'] += ctx['body']
        ctx['body'] = None

    pp.pprint(ctx)
    return ctx


def admin_ctx_filter(ctx, parser):

    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(parser.structure)

    #########
    # FILE PARTS

    # if ctx['model_admin'] in parser.structure['class_list']:
    #     ctx['model_admin_exists'] = True
    ctx['model_admin_exists'] = ctx['model_admin'] in parser.structure['class_list']

    if parser.structure['expressions']:
        print("BODY RANGE: %d-%d" % (parser.structure['last_import_line'] + 1, parser.structure['last_class_line']) )
        print("REGISTRATION RANGE: %d-%d" % (parser.structure['last_class_line'] + 1, parser.structure['body_end_index'] + 1) )
        ctx['body'] = parser.get_text_slice_by_line(parser.structure['last_import_line'] + 1, parser.structure['last_class_line'])
        ctx['registration_block'] = parser.get_text_slice_by_line(parser.structure['last_class_line'] + 1, parser.structure['body_end_index'] + 1)
    else:
        ctx['body'] = parser.new_get_body()
        ctx['registration_block'] = ''

    # if self.render_ctx['model_admin'] in self.parser.structure['class_list']:
    #     print("** %s admin already in '%s', skipping creation..." % (self.render_ctx['model_admin'], admin_file))
    #     self.render_ctx['create_model_admin'] = False
    #     self.render_ctx['register_model_admin'] = False

    return ctx

def body_as_empty(ctx, parser):
    '''simple filter to change the body to an empty string if it's None'''
    if ctx['body'] == None:
        ctx['body'] = ''
    return ctx
