import unittest
from app.parsers.generic import GenericParser

class TestGenericParser(unittest.TestCase):
    def setUp(self):
        self.parser = GenericParser()

    def test_generic_parsing(self):
        mock_data = [
            {'text': 'REPUBLIQUE FRANCAISE', 'confidence': 0.99},
            {'text': 'CARTE NATIONALE D\'IDENTITE', 'confidence': 0.98},
            {'text': 'NOM: MARTIN', 'confidence': 0.95},
        ]
        
        result = self.parser.parse(mock_data)
        
        self.assertIn('generic_text', result)
        self.assertIn('REPUBLIQUE FRANCAISE', result['generic_text'])
        self.assertIn('NOM: MARTIN', result['generic_text'])

if __name__ == '__main__':
    unittest.main()
