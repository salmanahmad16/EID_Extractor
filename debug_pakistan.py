from app.core import UniversalIDExtractor
import json

extractor = UniversalIDExtractor()
image_path = '/Users/mac/.gemini/antigravity/brain/86ddf86e-290f-4ca4-92f4-2b8f8cd76bee/uploaded_image_1765025009109.jpg'

# Extract raw dictionary
# We want to see the "ocr_data" (raw text lines) which isn't directly exposed by extract() usually
# But let's verify what extract() returns first, and maybe we can hack it to print raw text
# Actually, I can just use the OCR engine directly if accessible, but let's stick to the high level first to see what the parser sees.
# I'll create a small bypass to just get text.

print("--- Processing Image ---")
try:
    # 1. Load and preprocess (mimicking core.extract logic)
    from app.utils import load_image, preprocess_image
    images = load_image(image_path)
    img = images[0]
    processed = preprocess_image(img)
    
    # 2. Extract Text
    ocr_result = extractor.ocr_engine.extract_text(processed)
    
    print("\n--- Raw OCR Output ---")
    for item in ocr_result:
        print(f"Conf: {item['confidence']:.2f} | Text: '{item['text']}'")

    print("\n--- Current Parser Output ---")
    res = extractor.extract(image_path, country='Pakistan')
    print(json.dumps(res, indent=2))

except Exception as e:
    print(e)
