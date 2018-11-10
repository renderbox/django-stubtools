# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-05 10:06:34
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-09 18:07:07
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


# def get_last_import_index(data_lines):



def get_import_range(pattern, data_lines):
    '''
    Looks where the import line should be inserted into the file.  Returns the start and end lines (where to slice the segements from).
    '''
    length = len(data_lines)

    if length == 0:     # If there is nothing passeed in, return (0,0)
        return (0, 0)

    import_start_index = get_pattern_line(pattern, data_lines)  # Returns the index value of where the

    if import_start_index == None:                     # If no import...

        for c, line in enumerate(data_lines):
            if IMPORT_REGEX.findall( line ):
                import_end_index = c       # Make note of the last import's line number

        import_start_index = import_end_index + 1
        import_end_index = import_end_index + 1
    else:
        import_end_index = import_start_index + 1

    return import_start_index, import_end_index


def create_import_line(data, module, base_class):
    classes, comments = get_classes_and_functions(data)

    classes.append(base_class)
    classes = list(set(modules))
    classes.sort()      # Cleans up the import to be alphabetical

    result = "from %s import %s" % (module, ", ".join(classes))

    if comments:
        result += " #%s" % comments

    return result

