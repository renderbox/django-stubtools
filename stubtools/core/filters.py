# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-12-18 10:27:42
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-18 10:40:31
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
    # first_line = None
    last_line = None

    for assignment in parser.structure.get('assignments', []):
        if assignment['name'] == "urlpatterns":
            # first_line = assignment['first_line']
            last_line = assignment['last_line']

    if last_line:
        print("MODIFY BODY")
        print("Append After Line: %d" % last_line)
        # Check to see where the close list character is... "]"
        ctx['body'] = parser.get_text_slice_by_line(parser.structure['last_import_line'] + 1, last_line)
        ctx['footer'] = parser.get_text_slice_by_line(last_line + 1, parser.structure['linecount'] + 1)

    else:
        # If there is no "urlpatterns", move everything from the body to the header and set the body to a value None (So the template knows there is no body string)
        ctx['header'] += ctx['body']
        ctx['body'] = None

    # print( horizontal_rule() )
    # print("URL CTX:")
    # pp.pprint(ctx)
    # print( horizontal_rule() )
    # print("URL STRUCTURE:")
    # pp.pprint(parser.structure)
    # print( horizontal_rule() )

    return ctx
