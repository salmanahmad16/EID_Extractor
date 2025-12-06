from paddleocr import PaddleOCR
import logging

# Suppress PaddleOCR logging
logging.getLogger('ppocr').setLevel(logging.ERROR)

class OCREngine:
    def __init__(self, use_gpu=False, lang='en'):
        """
        Initialize PaddleOCR engine.
        """
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang, use_gpu=use_gpu, show_log=False)

    def extract_text(self, image):
        """
        Extract text from an image.
        Returns a list of tuples: (text, confidence, bounding_box)
        """
        result = self.ocr.ocr(image, cls=True)
        
        extracted_data = []
        if result and result[0]:
            for line in result[0]:
                box = line[0]
                text = line[1][0]
                confidence = line[1][1]
                extracted_data.append({
                    'text': text,
                    'confidence': confidence,
                    'box': box
                })
        
        return extracted_data
