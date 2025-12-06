# UAE Emirates ID Extractor

A backend-only Python application to extract data from UAE Emirates ID cards (Front, Back, or Both) using PaddleOCR.

## Features
- **High Accuracy**: Uses PaddleOCR for robust text detection.
- **Auto-Detection**: Automatically detects if the image is the front or back of the ID.
- **Clean JSON**: Returns structured JSON output.
- **PDF Support**: Handles PDF files (requires `poppler`).

## Installation

1.  **Install System Dependencies**:
    - **Mac**: `brew install poppler` (for PDF support)
    - **Linux**: `sudo apt-get install poppler-utils`

2.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the CLI tool:

```bash
python main.py path/to/id_card_image.jpg
```

Or force a specific side:

```bash
python main.py path/to/id_card_image.jpg --side Front
```

Save output to a file:

```bash
python main.py path/to/id_card_image.jpg --output result.json
```

## Output Format

```json
[
    {
        "side": "Front",
        "data": {
            "id_number": "784-1980-1234567-1",
            "name": "JOHN DOE",
            "nationality": "USA",
            "dob": "1980-01-01"
        }
    }
]
```
