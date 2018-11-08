# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-05 10:06:34
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-07 17:39:15
# --------------------------------------------

import re

# Common Regex Patterns

IMPORT_REGEX = re.compile(r"(import|from)")
FUNCTION_OR_CLASS_REGEX = re.compile(r"(def|class)")

def get_classes_and_functions_start(data_lines):
    return get_pattern_line(r"(def|class)", data_lines)

def get_pattern_line(pattern, data_lines, first=True, default=None):
    '''
    Find the first line this pattern occurs at
    '''
    module_regex = re.compile(pattern, re.MULTILINE)
    result = default

    for c, line in enumerate(data_lines):
        modules_check = module_regex.findall( line )

        if modules_check:
            if first:
                return c    # Record the line number and break at the first match
            else:
                result = c

    return result


def get_all_pattern_lines(pattern, data_lines, values=True):
    '''
    Find all the lines that match the patters.  
        values > True returns the line, False returns the index
    '''
    module_regex = re.compile(pattern, re.MULTILINE)

    result = []

    for c, line in enumerate(data_lines):
        modules_check = module_regex.findall( line )

        if modules_check:
            if values:
                result.append(line)    # Record the line number and break at the first match
            else:
                result.append(c)    # Record the line number and break at the first match

    return result


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
