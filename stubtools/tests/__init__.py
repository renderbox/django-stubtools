# #--------------------------------------------
# # Copyright 2013-2018, Grant Viklund
# # @Author: Grant Viklund
# # @Date:   2015-10-27 13:59:25
# # @Last Modified by:   Grant Viklund
# # @Last Modified time: 2018-11-20 11:58:26
# #--------------------------------------------
# from unittest import TestCase

from stubtools.tests.parse_test import *
from stubtools.tests.stubview import *

'''
> python -m unittest tests
'''

# # from django.test import TestCase
# from stubtools.core.parse import get_import_line

# class CoreParseGetImportRangeTestCase(TestCase):

#     def setUp(self):

#         self.data_lines = [
#             "from django.db import models",
#             "from django.utils.translation import ugettext_lazy as _",
#             "#2",
#             "#3",
#             "class User(models.Model):",
#             "    name = models.CharField(_('Name'), max_length=300 )",
#             "#6",
#             "#7",
#         ]

#         self.data_lines_missing_import = [
#             "# COMMENT"
#             "from django.utils.translation import ugettext_lazy as _",
#             "#2",
#             "#3",
#             "class User(models.Model):",
#             "    name = models.CharField(_('Name'), max_length=300 )",
#             "#6",
#             "#7",
#         ]

#     def test_empty_data_results_in_zero(self):
#         self.assertEqual( get_import_line("^from django.db import models", []), (0,0) )


#     # def test_empty_data_results_in_zero(self):
#     #     self.assertEqual( get_import_line("^from django.db import models", self.data_lines), (0,0) )

#         # self.assertEqual(lion.speak(), 'The lion says "roar"')
#         # self.assertEqual(cat.speak(), 'The cat says "meow"')
