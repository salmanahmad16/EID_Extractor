import unittest
from app.parsers.generic import GenericParser
from app.parsers.pakistan import PakistanParser

class TestSmartParsing(unittest.TestCase):
    def setUp(self):
        self.generic_parser = GenericParser()
        self.pakistan_parser = PakistanParser()

    def test_generic_heuristics_france(self):
        mock_data = [
            {'text': 'REPUBLIQUE FRANCAISE', 'confidence': 0.99},
            {'text': 'CARTE NATIONALE D\'IDENTITE', 'confidence': 0.98},
            {'text': 'Nom: MARTIN', 'confidence': 0.95},
            {'text': 'Né le: 01/01/1990', 'confidence': 0.95},
            {'text': 'Valid until: 01/01/2030', 'confidence': 0.95},
            {'text': 'Sex: M', 'confidence': 0.99},
            {'text': 'Document No: 12A34B56', 'confidence': 0.99}
        ]
        
        result = self.generic_parser.parse(mock_data)
        
        self.assertEqual(result['dob'], '1990-01-01')
        self.assertEqual(result['expiry_date'], '2030-01-01')
        self.assertEqual(result['sex'], 'M')
        # check if 12A34B56 is extracted or at least some ID
        self.assertTrue(result['id_number'] is not None)

    def test_pakistan_robustness(self):
        # Case provided by user where data was null
        mock_data = [
            {'text': 'Pakistan National Identity Card', 'confidence': 0.99},
            {'text': 'Name Salman Ahmad', 'confidence': 0.95}, # Same line name
            {'text': 'Father Name Muhammad Ahmad', 'confidence': 0.95},
            {'text': 'Gender Male', 'confidence': 0.95},
            {'text': 'Country of Stay Pakistan', 'confidence': 0.95},
            {'text': 'Identity Number 35202-2432431-7', 'confidence': 0.99},
            {'text': 'Date of Birth 02.10.1995', 'confidence': 0.95}, 
            {'text': 'Date of Expiry 02.10.2025', 'confidence': 0.95}
        ]
        
        result = self.pakistan_parser.parse(mock_data, side_hint='Front')
        
        self.assertEqual(result['name'], 'Salman Ahmad')
        self.assertEqual(result['father_name'], 'Muhammad Ahmad')
        self.assertEqual(result['dob'], '1995-10-02')
        self.assertEqual(result['expiry_date'], '2025-10-02')
        self.assertEqual(result['sex'], 'M')
        self.assertEqual(result['id_number'], '35202-2432431-7')

if __name__ == '__main__':
    unittest.main()
