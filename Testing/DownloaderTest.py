import unittest
from metadata_storage import get_status, get_pdf_file

class TestDownloader(unittest.TestCase):
    def setUp(self):
        # Set up a sample pdf_mapping for testing
        self.pdf_mapping = {
            '123': '123.pdf',
            '456': '456.pdf',
            '789': 'CORRUPTED'
        }

    def test_get_pdf_file(self):
        # Test valid BRnum
        self.assertEqual(get_pdf_file('123', self.pdf_mapping), '123.pdf')
        # Test another valid BRnum
        self.assertEqual(get_pdf_file('456', self.pdf_mapping), '456.pdf')
        # Test corrupted BRnum
        self.assertIsNone(get_pdf_file('789', self.pdf_mapping))
        # Test not found BRnum
        self.assertIsNone(get_pdf_file('000', self.pdf_mapping))

    def test_get_status(self):
        # Test valid BRnum
        self.assertEqual(get_status('123', self.pdf_mapping), 'Downloaded')
        # Test another valid BRnum
        self.assertEqual(get_status('456', self.pdf_mapping), 'Downloaded')
        # Test corrupted BRnum
        self.assertEqual(get_status('789', self.pdf_mapping), 'Corrupted')
        # Test not found BRnum
        self.assertEqual(get_status('000', self.pdf_mapping), 'Not Found')