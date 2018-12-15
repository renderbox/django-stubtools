#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2015-10-27 13:59:25
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-12-14 18:08:45
#--------------------------------------------
import os
import pprint

from django.test import TestCase

from stubtools.core.file import PythonFileParser
# from stubtools.test.fixtures import PythonFileParser

'''
> python -m unittest tests/parse_test.py
'''

class PythonFileParserTestCase(TestCase):

    def setUp(self):
        self.test_file_dir = os.path.join( os.path.dirname(__file__), 'test_files')
        self.pp = pprint.PrettyPrinter(indent=4)


    def test_blank_file_header(self):
        file_path = os.path.join(self.test_file_dir, 'blank.py')
        parser = PythonFileParser( file_path )

        header = parser.new_get_header()

        self.assertEqual( header, "" )

    def test_blank_file_body(self):
        file_path = os.path.join(self.test_file_dir, 'blank.py')
        parser = PythonFileParser( file_path )

        body = parser.new_get_body()

        self.assertEqual( body, "" )

    def test_blank_file_import_block(self):
        file_path = os.path.join(self.test_file_dir, 'blank.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], None )
        self.assertEqual( parser.structure['last_import_line'], None )

        import_block = parser.get_import_block()

        self.assertEqual( import_block, None )


    def test_models_empty_header(self):
        file_path = os.path.join(self.test_file_dir, 'models_empty.py')
        parser = PythonFileParser( file_path )

        header_array = parser.new_get_header().splitlines()

        self.assertEqual( header_array[-1], "# --------------------------------------------" )

    def test_models_empty_body(self):
        file_path = os.path.join(self.test_file_dir, 'models_empty.py')
        parser = PythonFileParser( file_path )

        body = parser.new_get_body()

        self.assertEqual( body, "" )

    def test_models_empty_import_block(self):
        file_path = os.path.join(self.test_file_dir, 'models_empty.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 9 )

        import_array = parser.get_import_block().splitlines()

        self.assertEqual( import_array[0], "from django.db import models" )
        self.assertEqual( import_array[-1], "from django.utils.translation import ugettext_lazy as _" )


    def test_models_single_header(self):
        file_path = os.path.join(self.test_file_dir, 'models_single.py')
        parser = PythonFileParser( file_path )

        header_array = parser.new_get_header().splitlines()

        self.assertEqual( header_array[-1], "# --------------------------------------------" )

    def test_models_single_body(self):
        file_path = os.path.join(self.test_file_dir, 'models_single.py')
        parser = PythonFileParser( file_path )

        body_array = parser.new_get_body().splitlines()

        self.assertEqual( body_array[0], "" )
        self.assertEqual( body_array[-1], '    name = models.CharField(_("Name"), max_length=300 )' )

    def test_models_single_import_block(self):
        file_path = os.path.join(self.test_file_dir, 'models_single.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 9 )

        import_array = parser.get_import_block().splitlines()

        self.assertEqual( import_array[0], "from django.db import models" )
        self.assertEqual( import_array[-1], "from django.utils.translation import ugettext_lazy as _" )



    def test_models_multiple_header(self):
        file_path = os.path.join(self.test_file_dir, 'models_multiple.py')
        parser = PythonFileParser( file_path )

        header_array = parser.new_get_header().splitlines()

        self.assertEqual( header_array[-1], "# --------------------------------------------" )

    def test_models_multiple_body(self):
        file_path = os.path.join(self.test_file_dir, 'models_multiple.py')
        parser = PythonFileParser( file_path )

        body_array = parser.new_get_body().splitlines()

        self.assertEqual( body_array[0], "" )
        self.assertEqual( body_array[-1], '    address = models.CharField(_("Name"), max_length=300 )' )

    def test_models_multiple_import_block(self):
        file_path = os.path.join(self.test_file_dir, 'models_multiple.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 10 )

        import_array = parser.get_import_block().splitlines()

        self.assertEqual( import_array[0], "from django.db import models" )
        self.assertEqual( import_array[-1], "from django.utils.translation import ugettext_lazy as _     # For localization" )



    def test_admin_empty_header(self):
        file_path = os.path.join(self.test_file_dir, 'admin_empty.py')
        parser = PythonFileParser( file_path )

        header_array = parser.new_get_header().splitlines()

        self.assertEqual( header_array[-1], "# --------------------------------------------" )

    def test_adminempty_body(self):
        file_path = os.path.join(self.test_file_dir, 'admin_empty.py')
        parser = PythonFileParser( file_path )

        body = parser.new_get_body()

        self.assertEqual( body, "" )

    def test_admin_empty_import_block(self):
        file_path = os.path.join(self.test_file_dir, 'admin_empty.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 8 )

        import_array = parser.get_import_block().splitlines()

        self.assertEqual( import_array[0], "from django.contrib import admin" )
        self.assertEqual( import_array[-1], "from django.contrib import admin" )





    def test_admin_multiple_header(self):
        file_path = os.path.join(self.test_file_dir, 'admin_multiple.py')
        parser = PythonFileParser( file_path )

        header_array = parser.new_get_header().splitlines()

        self.assertEqual( header_array[-1], "# --------------------------------------------" )

    def test_admin_multiple_body(self):
        file_path = os.path.join(self.test_file_dir, 'admin_multiple.py')
        parser = PythonFileParser( file_path )

        body_array = parser.new_get_body().splitlines()

        self.assertEqual( body_array[0], "" )
        self.assertEqual( body_array[-1], 'admin.site.register(Product, ProductAdmin)' )

    def test_admin_multiple_import_block(self):
        file_path = os.path.join(self.test_file_dir, 'admin_multiple.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 9 )

        import_array = parser.get_import_block().splitlines()

        self.assertEqual( import_array[0], "from django.contrib import admin" )
        self.assertEqual( import_array[-1], "from .models import Content, Product, Category" )


    # Add test for slicing before and after registration...



    def test_urls_multiple_header(self):
        file_path = os.path.join(self.test_file_dir, 'urls_multiple.py')
        parser = PythonFileParser( file_path )

        header_array = parser.new_get_header().splitlines()

        self.assertEqual( header_array[-1], "# --------------------------------------------" )

    def test_urls_multiple_body(self):
        file_path = os.path.join(self.test_file_dir, 'urls_multiple.py')
        parser = PythonFileParser( file_path )

        body_array = parser.new_get_body().splitlines()

        self.assertEqual( body_array[0], "" )
        self.assertEqual( body_array[-1], ']' )

    def test_urls_multiple_import_block(self):
        file_path = os.path.join(self.test_file_dir, 'urls_multiple.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 10 )

        import_array = parser.get_import_block().splitlines()

        self.assertEqual( import_array[0], "from django.conf.urls import url" )
        self.assertEqual( import_array[-1], "from . import views" )


    # Add test for slicing before and after url list insert point...



    def test_api_views_header(self):
        file_path = os.path.join(self.test_file_dir, 'api_views.py')
        parser = PythonFileParser( file_path )

        header_array = parser.new_get_header().splitlines()

        self.assertEqual( header_array[-1], "# --------------------------------------------" )

    def test_api_views_body(self):
        file_path = os.path.join(self.test_file_dir, 'api_views.py')
        parser = PythonFileParser( file_path )

        body_array = parser.new_get_body().splitlines()

        self.assertEqual( body_array[0], "" )
        self.assertEqual( body_array[-1], "    serializer_class = ReleaseSerializer" )

    def test_api_views_import_block(self):
        file_path = os.path.join(self.test_file_dir, 'api_views.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 11 )

        import_array = parser.get_import_block().splitlines()

        self.assertEqual( import_array[0], "from rest_framework import generics" )
        self.assertEqual( import_array[-1], "from .serializers import ProjectSerializer, ReleaseSerializer" )
