import re, os.path

def underscore_camel_case(s):
    """Adds spaces to a camel case string.  Failure to space out string returns the original string.
    >>> space_out_camel_case('DMLSServicesOtherBSTextLLC')
    'DMLS Services Other BS Text LLC'
    """

    return re.sub('((?=[A-Z][a-z])|(?<=[a-z])(?=[A-Z]))', '_', s)


def import_line_check(regex, text, module):
    '''
    Using the given regex see if the module is imported in the text
    '''
    imprt = regex.findall( text )

    if imprt:
        for line in imprt:
            check = [ x.strip() for x in line.split(",") ]
            #print check
            if module in check:
                return True

    return False


def class_name(str):
    return str[:1].upper() + str[1:]
