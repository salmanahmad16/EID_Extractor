import unittest
from app.parsers.uae import UAEParser
from app.utils import preprocess_image
import numpy as np

class TestRobustness(unittest.TestCase):
    def setUp(self):
        self.parser = UAEParser()

    def test_orphan_date_logic(self):
        # Scenario: Labels are garbled, but dates are found
        ocr_data = [
            {'text': 'GarbledDOB 01/01/1990'},
            {'text': 'GarbledIssue 01/01/2020'},
            {'text': 'GarbledExp 01/01/2025'},
            {'text': 'Name: Test'}
        ]
        data = self.parser.parse(ocr_data)
        
        # Heuristic should work:
        # Oldest = DOB
        # Newest = switch
        # Middle = Issue
        self.assertEqual(data['dob'], '1990-01-01')
        self.assertEqual(data['issuing_date'], '2020-01-01')
        self.assertEqual(data['expiry_date'], '2025-01-01')

    def test_text_cleanup(self):
        ocr_data = [
            {'text': 'Name: ,.John Doe'},
            {'text': 'Nationality: .Pakistan'}
        ]
        data = self.parser.parse(ocr_data)
        self.assertEqual(data['name'], 'John Doe')
        self.assertEqual(data['nationality'], 'Pakistan')

    def test_gamma_trigger(self):
        # Create a dark image
        img = np.zeros((100, 100), dtype=np.uint8) + 50 # Dark gray
        processed = preprocess_image(img)
        # Should be brighter
        self.assertTrue(np.mean(processed) > 50)

if __name__ == '__main__':
    unittest.main()
