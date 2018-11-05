# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-05 10:06:34
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-11-05 10:14:09
# --------------------------------------------

import re

# Common Regex Patterns

IMPORT_REGEX = re.compile(r"(import|from)")
FUNCTION_OR_CLASS_REGEX = re.compile(r"(def|class)")
