# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-05 10:06:34
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-06 12:04:49
# --------------------------------------------

import re

# Common Regex Patterns

IMPORT_REGEX = re.compile(r"(import|from)")
FUNCTION_OR_CLASS_REGEX = re.compile(r"(def|class)")

def get_classes_and_functions_start(data_lines):

    # result = len(data_lines)

    # for c, line in enumerate(data_lines):
    #     if FUNCTION_OR_CLASS_REGEX.findall( line ):
    #         result = c       # Make note of the line number
    #         break

    # return result
    return get_pattern_line(r"(def|class)", data_lines)


def get_pattern_line(pattern, data_lines):
    '''
    Find the first line this pattern occurs at
    '''
    module_regex = re.compile(pattern, re.MULTILINE)

    for c, line in enumerate(data_lines):
        modules_check = module_regex.findall( line )

        if modules_check:
            return c    # Record the line number and break at the first match

    return None

def get_classes_and_functions(line):
    parts = line.split()
    module_start = 1
    comments = None

    # Find the import point
    for c, part in enumerate(parts):
        if part == "import":
            module_start = c + 1
            break

    reassembly = str(" ".join(parts[module_start:])).split("#")

    if len(reassembly) > 1:
        comments = "#" + "#".join(reassembly[1:])

    modules = [x.strip() for x in reassembly[0].split(",")]

    return modules, comments
