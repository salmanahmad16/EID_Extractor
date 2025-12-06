import unittest
from unittest.mock import MagicMock, patch
from app.core import UniversalIDExtractor

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.extractor = UniversalIDExtractor()

    @patch('app.core.load_image')
    @patch('app.core.preprocess_image')
    @patch('app.core.OCREngine')
    def test_generic_fallback(self, mock_ocr, mock_preprocess, mock_load):
        # Setup mocks
        mock_load.return_value = ['dummy_image']
        mock_preprocess.return_value = 'processed_image'
        
        # Mock OCR engine instance
        mock_engine_instance = mock_ocr.return_value
        mock_engine_instance.extract_text.return_value = [
            {'text': 'Hello World', 'confidence': 0.9}
        ]
        
        # We need to re-init extractor to pick up the mocked engine if it was instantiated in __init__
        # But core.py instantiates it in __init__. 
        # So we can just attach the mock to the existing instance
        self.extractor.ocr_engine = mock_engine_instance

        # Test extraction for France
        results = self.extractor.extract('dummy_path', country='France')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['country'], 'France')
        self.assertIn('generic_text', results[0]['data'])
        self.assertIn('Hello World', results[0]['data']['generic_text'])

    @patch('app.core.load_image')
    @patch('app.core.preprocess_image')
    def test_uae_preservation(self, mock_preprocess, mock_load):
        # Ensure UAE still uses UAE parser (mocking OCR result to be valid for UAE if needed, 
        # or just checking it calls the UAE parser)
        # Since I am not mocking the parser itself, I rely on it existing in the map
        
        self.assertIn('UAE', self.extractor.parsers)
        self.assertNotIn('France', self.extractor.parsers)

if __name__ == '__main__':
    unittest.main()
