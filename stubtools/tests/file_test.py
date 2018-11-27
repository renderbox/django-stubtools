#--------------------------------------------
# Copyright 2013-2018, Grant Viklund
# @Author: Grant Viklund
# @Date:   2015-10-27 13:59:25
# @Last Modified by:   Grant Viklund
# @Last Modified time: 2018-11-27 11:10:15
#--------------------------------------------
import os
import pprint

from django.test import TestCase

from stubtools.core.file import PythonFileParser

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
