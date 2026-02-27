import unittest
import os
from pathlib import Path
import shutil

class TestFileDirectories(unittest.TestCase):
    def setUp(self):
        # Set up environment variables for testing
        self.original_output_dir = os.getenv('PDF_OUTPUT_DIR')
        self.test_output_dir = str(Path.cwd() / 'test_pdf_output')
        os.environ['PDF_OUTPUT_DIR'] = self.test_output_dir


    def test_get_output_directory(self):
        from FileDirectories import get_output_directory
        output_dir = get_output_directory()
        self.assertTrue(output_dir.exists())
        self.assertTrue(output_dir.is_dir())
        self.assertTrue(self.test_output_dir in str(output_dir))


    def test_get_source_path(self):
        from FileDirectories import get_source_path
        # Set up environment variable for testing
        self.test_source_dir = str(Path.cwd() / 'test_data')
        self.test_xlsx_filename = 'test.xlsx'
        os.environ['XLSX_SOURCE_DIR'] = self.test_source_dir
        os.environ['XLSX_FILENAME'] = self.test_xlsx_filename
        
        # Create a dummy Excel file for testing
        test_file_path = Path(self.test_source_dir) / self.test_xlsx_filename
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        test_file_path.touch()
        
        source_path = get_source_path()
        self.assertEqual(source_path, test_file_path.resolve())


    def tearDown(self):
        # Clean up environment variables after testing
        if self.original_output_dir is not None:
            os.environ['PDF_OUTPUT_DIR'] = self.original_output_dir
        else:
            os.environ.pop('PDF_OUTPUT_DIR', None)
        
        # Clean up test output directory if it was created
        test_output_path = Path(self.test_output_dir)
        if test_output_path.exists() and test_output_path.is_dir():
            shutil.rmtree(test_output_path)