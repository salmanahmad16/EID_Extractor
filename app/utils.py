import cv2
import numpy as np
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image
import io
import os

def load_image(source):
    """
    Load an image from a file path, bytes, or PDF.
    Returns a list of numpy arrays (images) to handle multi-page PDFs.
    """
    images = []

    if isinstance(source, str):
        if source.lower().endswith('.pdf'):
            try:
                pil_images = convert_from_path(source)
                for pil_img in pil_images:
                    images.append(np.array(pil_img))
            except Exception as e:
                raise ValueError(f"Error converting PDF: {e}")
        else:
            img = cv2.imread(source)
            if img is None:
                raise ValueError(f"Could not read image from {source}")
            images.append(img)
    
    elif isinstance(source, bytes):
        # Try to detect if it's a PDF by header
        if source.startswith(b'%PDF'):
            try:
                pil_images = convert_from_bytes(source)
                for pil_img in pil_images:
                    images.append(np.array(pil_img))
            except Exception as e:
                raise ValueError(f"Error converting PDF bytes: {e}")
        else:
            nparr = np.frombuffer(source, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image bytes")
            images.append(img)
            
    elif isinstance(source, Image.Image):
        images.append(np.array(source))
        
    elif isinstance(source, np.ndarray):
        images.append(source)
        
    else:
        raise ValueError("Unsupported source type")

    return images

def preprocess_image(image):
    """
    Advanced preprocessing pipeline to improve OCR accuracy on faded, blurry, or low-contrast images.
    """
    # Ensure image is valid
    if image is None or image.size == 0:
        return image

    # 1. Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # 2. Check resolution and upscale if too small (OCR struggles with small text)
    # A standard ID card is roughly 85mm x 55mm. 
    # At 300 DPI, that's ~1000px width. If significantly smaller, upscale.
    h, w = gray.shape
    if w < 1000:
        scale = 1000 / w
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 3. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # This is excellent for handling uneven lighting and faded text
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 3b. Gamma Correction (Automatic)
    # If image is too dark, or just generally to improve contrast
    # A gamma < 1.0 will brighten the image and bring out details in dark areas
    mean_brightness = np.mean(enhanced)
    if mean_brightness < 100: # If relatively dark
        gamma = 0.8
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
        enhanced = cv2.LUT(enhanced, table)

    # 4. Denoise
    # fastNlMeansDenoising is effective but slow. 
    # GaussianBlur is faster but blurs edges.
    # Bilateral Filter is a good middle ground: keeps edges sharp, removes noise.
    denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)

    # 5. Sharpening using a kernel
    # This recovers some crispness lost in denoising or blur
    kernel = np.array([[0, -0.5, 0],
                       [-0.5, 3,-0.5],
                       [0, -0.5, 0]])
    sharpened = cv2.filter2D(denoised, -1, kernel)

    # 6. Optional: Adaptive Thresholding (Binarization)
    # PaddleOCR handles grayscale well, but sometimes binarization helps isolate text.
    # However, aggressive binarization can hurt if parameters aren't perfect.
    # We will stick to the sharpened grayscale image as it preserves more info for the deep learning model.
    # But checking if the image is too bright/dark might be useful.
    
    return sharpened
