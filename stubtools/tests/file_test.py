#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2015-10-27 13:59:25
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-11-28 17:18:52
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


    def test_blank_file(self):
        file_path = os.path.join(self.test_file_dir, 'blank.py')
        parser = PythonFileParser( file_path )
        print("------------")
        print(" Blank File")
        print("------------")

        self.assertEqual( parser.structure['first_import_line'], None )
        self.assertEqual( parser.structure['last_import_line'], None )
        self.assertEqual( parser.structure['last_code_line'], None )

        # Change Slice Point
        parser.set_import_slice("django.db")
        # self.pp.pprint(parser.structure)

        self.assertEqual( parser.structure['header_end_index'], None )   # Last header index (6) + 1, for slicing
        self.assertEqual( parser.structure['body_start_index'], None )
        self.assertEqual( parser.structure['body_end_index'], None )
        self.assertEqual( parser.structure['footer_start_index'], None )

        self.assertEqual( parser.get_body(), '' )

    def test_empty_model_file(self):
        file_path = os.path.join(self.test_file_dir, 'models_empty.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 9 )
        self.assertEqual( parser.structure['last_code_line'], None )

        # Change Slice Point
        parser.set_import_slice("django.db")

        self.assertEqual( parser.structure['header_end_index'], 6 )
        self.assertEqual( parser.structure['body_start_index'], 8 )
        self.assertEqual( parser.structure['body_end_index'], 8 )
        self.assertEqual( parser.structure['footer_start_index'], None )

        header_text = parser.get_header()
        header_text_lines = header_text.splitlines()

        body_text = parser.get_body()
        body_text_lines = body_text.splitlines()

        self.assertEqual( header_text_lines[-1], '# --------------------------------------------')
        self.assertEqual( body_text_lines[0], 'from django.utils.translation import ugettext_lazy as _' )

    def test_single_model_file(self):
        file_path = os.path.join(self.test_file_dir, 'models_single.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 9 )
        self.assertEqual( parser.structure['last_code_line'], 13 )

        # Change Slice Point
        parser.set_import_slice("django.db")

        self.assertEqual( parser.structure['header_end_index'], 6 )  # Last header index (6) + 1, for slicing
        self.assertEqual( parser.structure['body_start_index'], 8 )
        self.assertEqual( parser.structure['body_end_index'], 12 )
        self.assertEqual( parser.structure['footer_start_index'], 13 )

        body_text = parser.get_body()
        body_text_lines = body_text.splitlines()

        self.assertEqual( body_text_lines[0], "from django.utils.translation import ugettext_lazy as _" )

    def test_multiple_model_file(self):
        file_path = os.path.join(self.test_file_dir, 'models_multiple.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 9 )
        self.assertEqual( parser.structure['last_code_line'], 21 )

        # Change Slice Point
        parser.set_import_slice("django.db")

        self.assertEqual( parser.structure['header_end_index'], 6 )  # Last header index (6) + 1, for slicing
        self.assertEqual( parser.structure['body_start_index'], 8 )
        self.assertEqual( parser.structure['body_end_index'], 20 )
        self.assertEqual( parser.structure['footer_start_index'], 21 )

        body_text = parser.get_body()
        body_text_lines = body_text.splitlines()

        self.assertEqual( body_text_lines[0], "from django.utils.translation import ugettext_lazy as _" )
        self.assertEqual( body_text_lines[-1], '    name = models.CharField(_("Name"), max_length=300 )' )

    def test_empty_admin_file(self):
        file_path = os.path.join(self.test_file_dir, 'admin_empty.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 8 )
        self.assertEqual( parser.structure['last_code_line'], None )

        # Change Slice Point
        parser.set_import_slice(".models")

        self.assertEqual( parser.structure['header_end_index'], 8 )
        self.assertEqual( parser.structure['body_start_index'], None )
        self.assertEqual( parser.structure['body_end_index'], None )
        self.assertEqual( parser.structure['footer_start_index'], None )

    def test_multiple_admin_file(self):
        file_path = os.path.join(self.test_file_dir, 'admin_multiple.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 9 )
        self.assertEqual( parser.structure['last_code_line'], 44 )

        # Change Slice Point
        parser.set_import_slice(".models")

        self.assertEqual( parser.structure['header_end_index'], 7 )
        self.assertEqual( parser.structure['body_start_index'], 9 )
        self.assertEqual( parser.structure['body_end_index'], 43 )
        self.assertEqual( parser.structure['footer_start_index'], 44 )


    def test_multiple_urls_file(self):
        file_path = os.path.join(self.test_file_dir, 'urls_multiple.py')
        parser = PythonFileParser( file_path )

        self.assertEqual( parser.structure['first_import_line'], 8 )
        self.assertEqual( parser.structure['last_import_line'], 10 )
        self.assertEqual( parser.structure['last_code_line'], 14 )      # This should be line 15 but the ']' is on line 15 and is not recognized in AST.  A new method to figure this out needs to be developed.

        # # Change Slice Point
        # parser.set_import_slice(".models")

        # self.assertEqual( parser.structure['header_end_index'], 7 )
        self.assertEqual( parser.structure['body_start_index'], 11 )
        # self.assertEqual( parser.structure['body_end_index'], 43 )
        # self.assertEqual( parser.structure['footer_start_index'], 44 )
