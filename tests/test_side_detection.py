import unittest
from app.parsers.uae import UAEParser

class TestUAESideDetection(unittest.TestCase):
    def setUp(self):
        self.parser = UAEParser()

    def test_explicit_front_keywords(self):
        # Scenario: Preprocessing creates noise ("<<") but "Name" is clearly present.
        ocr_data = [
            {'text': 'United Arab Emirates'},
            {'text': 'Name: John Doe'},
            {'text': 'Noise << Artifact'}, # Short noise line
            {'text': 'ID Number: 784-1234-1234567-1'}
        ]
        data = self.parser.parse(ocr_data)
        self.assertEqual(data['side'], 'Front')
        self.assertEqual(data['name'], 'John Doe')

    def test_explicit_back_keywords(self):
        ocr_data = [
            {'text': 'Resident Identity Card'},
            {'text': 'Stuff on back'}
        ]
        data = self.parser.parse(ocr_data)
        self.assertEqual(data['side'], 'Back')

    def test_mrz_back_detection(self):
        # Long line with << should be Back
        ocr_data = [
            {'text': 'Some header'},
            {'text': 'IDARE7841234567<<1234567890<<<<'} # > 15 chars
        ]
        data = self.parser.parse(ocr_data)
        self.assertEqual(data['side'], 'Back')

    def test_noise_mrz_is_front(self):
        # Short '<<' should be ignored if no other Back signals
        ocr_data = [
            {'text': 'Some Random Text'},
            {'text': '<<'}, # Noise, very short
            {'text': 'More text'}
        ]
        # Default fallback is Front
        data = self.parser.parse(ocr_data)
        self.assertEqual(data['side'], 'Front')

if __name__ == '__main__':
    unittest.main()
