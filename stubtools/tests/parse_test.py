#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2015-10-27 13:59:25
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-11-27 10:45:12
#--------------------------------------------
from django.test import TestCase
from stubtools.core import parse_app_input
from stubtools.core.parse import get_import_range

'''
> python -m unittest tests/parse_test.py
'''

class CoreParseGetImportRangeTestCase(TestCase):

    def test_parse_app_args(self):
        self.assertEqual( ['app', 'view', 'TemplateView'], parse_app_input("app.view.TemplateView") )
        self.assertEqual( ['app', 'view', None], parse_app_input("app.view") )
        self.assertEqual( ['app', None, None], parse_app_input("app") )

