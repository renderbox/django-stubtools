#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2015-10-27 13:59:25
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-11-26 17:51:00
#--------------------------------------------
from django.test import TestCase
from stubtools.core.parse import get_import_range
from stubtools.core import parse_app_input

'''
> python -m unittest tests/parse_test.py
'''

class CoreParseGetImportRangeTestCase(TestCase):

    def test_parse_app_args(self):
        self.assertEqual( ['app', 'view', 'TemplateView'], parse_app_input("app.view.TemplateView") )
        self.assertEqual( ['app', 'view', None], parse_app_input("app.view") )
        self.assertEqual( ['app', None, None], parse_app_input("app") )

