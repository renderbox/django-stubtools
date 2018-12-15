# --------------------------------------------
# Copyright 2018 Grant Viklund
# @Author: Grant Viklund
# @Date:   2018-11-20 11:24:44
# @Last modified by:   Grant Viklund
# @Last Modified time: 2018-12-14 18:21:29
# --------------------------------------------
# import unittest
# import os

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.test import TestCase
# from django.core import management
# from django.core.management.base import CommandError

from stubtools.management.commands.stubview import Command as ViewCommand

# class TestStubTemplateView(TestCase):

#     def setUp(self):
#         self.cmd = Command()
#         self.cmd.debug = False
#         self.cmd.write_files = False

#     def test_template_view(self):
#         app_name = 'test'
#         view_name = 'foo'
#         self.cmd.process(app_name, view_name, 'TemplateView')

#         self.assertEqual( self.cmd.render_ctx['resource_class'], 'FooView')
#         self.assertEqual( self.cmd.render_ctx['view_header'][:4], '# 0 ')   # Make sure the first line works as expected
#         self.assertEqual( self.cmd.render_ctx['constructor_template'], 'views/TemplateView.html.j2')   # Make sure the first line works as expected
#         self.assertEqual( self.cmd.render_ctx['resource_name'], 'test-foo')   # Make sure the first line works as expected
#         self.assertEqual( self.cmd.render_ctx['resource_pattern'], 'foo/')   # Make sure the first line works as expected
#         self.assertEqual( self.cmd.render_ctx['attributes']['template_name'], '"test/foo.html"')   # Make sure the first line works as expected


class TestStubListView(TestCase):

    def setUp(self):
        self.cmd = ViewCommand()
        self.cmd.debug = False
        self.cmd.write_files = False

    def test_template_view(self):
        app_name = 'test'
        view_name = 'foo'
        model_name = 'boo'

        query_args = {  'queryset':"Boo.objects.all()",
                        'template_name': "test/boo_list.html",
                        'template_in_app': True,
                        'resource_name': "foo-boo-list",
                        'resource_pattern': "boo/list/",
                        'description': "Some Description",
        }

        self.cmd.process(app_name, view_name, 'ListView', model="Boo", **query_args)
    #     self.assertEqual( self.cmd.render_ctx['resource_class'], 'BooListView')
    #     self.assertEqual( self.cmd.render_ctx['view_header'][:4], '# 0 ')   # Make sure the first line works as expected
    #     self.assertEqual( self.cmd.render_ctx['constructor_template'], 'views/ListView.html.j2')   # Make sure the first line works as expected
    #     self.assertEqual( self.cmd.render_ctx['resource_name'], 'test-foo-boo-list')   # Make sure the first line works as expected
    #     self.assertEqual( self.cmd.render_ctx['resource_pattern'], 'foo/list/')   # Make sure the first line works as expected
    #     self.assertEqual( self.cmd.render_ctx['attributes']['template_name'], '"test/foo_boo_list.html"')   # Make sure the first line works as expected


if __name__ == '__main__':
    unittest.main()