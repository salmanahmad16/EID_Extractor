import unittest
import numpy as np
import cv2
from app.utils import preprocess_image

class TestPreprocessing(unittest.TestCase):
    def test_pipeline_execution(self):
        # Create a dummy image (100x100, RGB)
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        # Add some "text" (white rectangle)
        cv2.rectangle(img, (10, 10), (90, 40), (255, 255, 255), -1)
        
        # Run preprocessing
        result = preprocess_image(img)
        
        # Check basic properties
        self.assertIsNotNone(result)
        # Should be grayscale (2D)
        self.assertEqual(len(result.shape), 2)
        # Should be upscaled since orig width 100 < 1000
        # Scale factor is 1000/100 = 10, so width should be ~1000
        h, w = result.shape
        self.assertAlmostEqual(w, 1000, delta=5)

    def test_already_grayscale(self):
        img = np.zeros((500, 500), dtype=np.uint8)
        result = preprocess_image(img)
        self.assertEqual(len(result.shape), 2)
        # Upscaled: 500 -> 1000 (x2)
        h, w = result.shape
        self.assertAlmostEqual(w, 1000, delta=5)

    def test_large_image(self):
        # Image larger than 1000px
        img = np.zeros((2000, 2000, 3), dtype=np.uint8)
        result = preprocess_image(img)
        # Should NOT be downscaled, just kept as is (or slightly processed)
        # My code only checks `if w < 1000`, so large images stay large.
        h, w = result.shape
        self.assertEqual(w, 2000)

    def test_invalid_input(self):
        self.assertIsNone(preprocess_image(None))
        self.assertEqual(len(preprocess_image(np.array([]))), 0)

if __name__ == '__main__':
    unittest.main()
