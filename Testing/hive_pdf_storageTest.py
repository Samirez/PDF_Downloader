import unittest
import os
import shutil
from pathlib import Path

class TestHivePDFStorage(unittest.TestCase):
    def setUp(self):
        # Set up environment variables for testing
        self.original_output_dir = os.getenv('PDF_OUTPUT_DIR')
        self.test_output_dir = str(Path.cwd() / 'test_pdf_output')
        os.environ['PDF_OUTPUT_DIR'] = self.test_output_dir
       
    def test_hive_pdf_storage(self):
        from FileDirectories import get_output_directory
        output_dir = get_output_directory()
        self.assertTrue(output_dir.exists())
        self.assertTrue(output_dir.is_dir())
        self.assertTrue(self.test_output_dir in str(output_dir))

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