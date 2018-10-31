# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-10-30 18:31:15
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-10-30 18:34:42
# --------------------------------------------

def get_first_index(lines, regex):
    '''
    Get the index value of the first item to match the regex pattern.
    '''
    for c, line in enumerate(lines):
        check = regex.findall( line )

        if check:
            return c       # Return the line index value when found

def get_last_index(lines, regex):
    result = None

    for c, line in enumerate(lines):
        check = regex.findall( line )

        if check:
            result = c       # Return the line index value when found

    return result

def get_first_and_last_index(lines, regex):

    first = None
    last = first

    for c, line in enumerate(lines):
        check = regex.findall( line )

        if check:
            if first == None:
                first = c

            last = c       # Make note of the line number

    return (first, last)
