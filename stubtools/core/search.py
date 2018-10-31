# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-10-30 18:31:15
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-10-30 18:52:58
# --------------------------------------------

def get_first_index(lines, regex):
    '''
    Get the index value of the first item to match the regex pattern.
    '''
    for c, line in enumerate(lines):
        check = regex.findall( line )

        if check:
            return c       # Return the line index value when found

    return None     # Returns None if not found

def get_last_index(lines, regex, start=0):
    '''
    Get the index value of the last item to match the regex pattern.
    '''
    result = None

    for c, line in enumerate(lines[start:]):
        check = regex.findall( line )

        if check:
            result = c + start       # Return the line index value when found

    return result

def get_first_and_last_index(lines, regex):
    '''
    Done this way to support some optimizations, like starting searches from an index point.
    '''

    first = get_first_index(lines, regex)
    last = get_last_index(lines, regex, start=first)

    return (first, last)
