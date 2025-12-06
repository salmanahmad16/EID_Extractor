from flask import Flask, request, jsonify, render_template
from app.core import UniversalIDExtractor
import os
import tempfile

app = Flask(__name__)
extractor = UniversalIDExtractor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/extract', methods=['POST'])
def extract():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    country = request.form.get('country', 'UAE')
    side = request.form.get('side', '') # Optional
    if not side:
        side = None

    try:
        # Save to temp file to handle PDF/Image loading uniformly
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
            file.save(temp.name)
            temp_path = temp.name

        results = extractor.extract(temp_path, country=country, side_hint=side)
        
        # Cleanup
        os.remove(temp_path)
        
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)
