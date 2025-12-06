from .utils import load_image, preprocess_image
from .ocr_engine import OCREngine
from .parsers.uae import UAEParser
from .parsers.pakistan import PakistanParser
from .parsers.generic import GenericParser
from .parsers.india import IndiaParser
from .parsers.usa import USAParser
from .parsers.uk import UKParser
from .parsers.germany import GermanyParser
from .parsers.saudi import SaudiParser
import json

class UniversalIDExtractor:
    def __init__(self):
        self.ocr_engine = OCREngine()
        self.parsers = {
            'UAE': UAEParser(),
            'Pakistan': PakistanParser(),
            'India': IndiaParser(),
            'USA': USAParser(),
            'UK': UKParser(),
            'United Kingdom': UKParser(),
            'Germany': GermanyParser(),
            'Saudi Arabia': SaudiParser(),
            'KSA': SaudiParser()
        }

    def extract(self, image_source, country='UAE', side_hint=None):
        """
        Main extraction method.
        image_source: path, bytes, or PDF
        country: 'UAE' or 'Pakistan'
        side_hint: 'Front', 'Back', or None (auto-detect)
        """
        images = load_image(image_source)
        results = []

        parser = self.parsers.get(country)
        if not parser:
            parser = GenericParser()

        for img in images:
            # Preprocess
            processed_img = preprocess_image(img)
            
            # OCR
            ocr_data = self.ocr_engine.extract_text(processed_img)
            
            # Parse
            try:
                parsed_data = parser.parse(ocr_data, side_hint=side_hint)
            except Exception as e:
                parsed_data = {'error': str(e), 'raw_text': [x['text'] for x in ocr_data]}

            results.append({
                'country': country,
                'data': parsed_data
            })

        return results

    def extract_to_json(self, image_source, country='UAE', side_hint=None):
        results = self.extract(image_source, country, side_hint)
        return json.dumps(results, indent=4, ensure_ascii=False)
