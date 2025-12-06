import unittest
from app.parsers import FrontParser, BackParser

class TestParsers(unittest.TestCase):
    def setUp(self):
        self.front_parser = FrontParser()
        self.back_parser = BackParser()

    def test_front_parsing(self):
        # Mock OCR data for a front side
        mock_data = [
            {'text': 'UNITED ARAB EMIRATES', 'confidence': 0.99},
            {'text': 'FEDERAL AUTHORITY FOR IDENTITY', 'confidence': 0.98},
            {'text': 'ID Number', 'confidence': 0.95},
            {'text': '784-1980-1234567-1', 'confidence': 0.99},
            {'text': 'Name', 'confidence': 0.95},
            {'text': 'JOHN DOE', 'confidence': 0.96},
            {'text': 'Nationality', 'confidence': 0.95},
            {'text': 'USA', 'confidence': 0.97},
            {'text': 'Date of Birth', 'confidence': 0.95},
            {'text': '01/01/1980', 'confidence': 0.98}
        ]
        
        result = self.front_parser.parse(mock_data)
        
        self.assertEqual(result['id_number'], '784-1980-1234567-1')
        self.assertEqual(result['name'], 'JOHN DOE')
        self.assertEqual(result['nationality'], 'USA')
        self.assertEqual(result['dob'], '1980-01-01')

    def test_back_parsing(self):
        # Mock OCR data for a back side
        mock_data = [
            {'text': 'Resident Identity Card', 'confidence': 0.99},
            {'text': 'Expiry Date', 'confidence': 0.95},
            {'text': '31/12/2025', 'confidence': 0.98},
            {'text': 'I<ARE784198012345671<<<<<<<<<<<', 'confidence': 0.90},
            {'text': '8001018M2512313USA<<<<<<<<<<<6', 'confidence': 0.90},
            {'text': 'DOE<<JOHN<<<<<<<<<<<<<<<<<<<<<', 'confidence': 0.90}
        ]
        
        result = self.back_parser.parse(mock_data)
        
        self.assertEqual(result['expiry_date'], '2025-12-31')
        self.assertTrue(len(result['mrz']) > 0)
        self.assertIn('I<ARE784198012345671<<<<<<<<<<<', result['mrz'][0])

if __name__ == '__main__':
    unittest.main()
