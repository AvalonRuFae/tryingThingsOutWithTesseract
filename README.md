# Student Composition Corrector

An automated system for correcting student compositions using OCR, coordinate extraction, and AI-powered feedback.

## Features

- **OCR Text Extraction**: Extract text with precise coordinate mapping from student compositions
- **Cloud OCR Integration**: Google Vision API support with fallback options
- **Error Detection**: Identify spelling, grammar, and structural issues
- **Visual Annotation**: Place corrections and feedback directly on the original document
- **Multiple Input Formats**: Support for images, scanned documents, and screenshots
- **AI Integration**: Ready for LLM-powered grammar and style analysis
- **Web Application Ready**: Backend structure prepared for FastAPI integration

## Project Structure

```
student-composition-corrector/
├── src/                          # Source code
│   ├── core/                     # Core OCR functionality
│   │   └── test_ocr_coordinates.py
│   ├── ocr/                      # OCR processing modules
│   │   ├── analyze_screenshot.py
│   │   ├── process_screenshot.py
│   │   ├── google_vision_ocr.py
│   │   ├── google_vision_simple.py
│   │   └── test_google_vision_structure.py
│   ├── annotation/               # Annotation and visualization
│   │   ├── demo_annotations.py
│   │   └── typo_detector.py
│   └── analysis/                 # Analysis and reporting
│       └── final_report.py
├── data/                         # Data files
│   ├── input/                   # Input images and documents
│   │   ├── sample_composition.png
│   │   ├── composition_with_typos.png
│   │   └── screenshot_sample.png
│   ├── output/                  # Generated visualizations
│   │   ├── ocr_visualization.png
│   │   ├── annotated_typos.png
│   │   ├── screenshot_ocr_visualization.png
│   │   ├── screenshot_detailed_analysis.png
│   │   └── google_vision_simple_visualization.png
│   └── results/                 # OCR and analysis results (JSON)
│       ├── ocr_results.json
│       ├── typo_ocr_results.json
│       ├── screenshot_ocr_results.json
│       ├── screenshot_enhanced_results.json
│       └── google_vision_simple_results.json
├── examples/                     # Example scripts and demos
│   ├── create_sample_with_typos.py
│   └── create_comparison.py
├── scripts/                      # Setup and utility scripts
│   └── setup_google_vision.sh
├── tests/                        # Unit tests
├── docs/                         # Documentation
│   └── google_vision_setup.md
├── config/                       # Configuration files
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## OCR Options

### 1. Local Tesseract OCR (Default)
```bash
# Install Tesseract (macOS)
brew install tesseract

# Run local OCR
python src/core/test_ocr_coordinates.py
python src/ocr/analyze_screenshot.py
```

### 2. Google Cloud Vision API (Recommended for Production)
```bash
# Install Google Cloud Vision
pip install google-cloud-vision

# Set up Google Cloud credentials
./scripts/setup_google_vision.sh

# Or follow manual setup
open docs/google_vision_setup.md

# Run Google Vision OCR
python src/ocr/google_vision_simple.py
```

### 3. Mock Data (Development/Testing)
```bash
# No setup required - uses sample data
python src/ocr/google_vision_simple.py
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test OCR Extraction (Local)**:
   ```bash
   python src/core/test_ocr_coordinates.py
   ```

3. **Test Google Vision OCR**:
   ```bash
   python src/ocr/google_vision_simple.py
   ```

4. **Process Your Own Image**:
   ```bash
   python src/ocr/process_screenshot.py
   ```

5. **Generate Analysis Report**:
   ```bash
   python src/analysis/final_report.py
   ```

## Dependencies

### Core Dependencies
- Python 3.8+
- PIL/Pillow
- NumPy

### OCR Engines
- **Tesseract OCR** (local processing)
- **Google Cloud Vision API** (cloud processing)
- pytesseract (Tesseract Python wrapper)

### Visualization
- OpenCV (optional, for enhanced visualization)
- Matplotlib (optional, for plotting)

## Usage Examples

### Basic OCR with Coordinates
```python
from src.core.test_ocr_coordinates import OCRCoordinateExtractor

extractor = OCRCoordinateExtractor()
results = extractor.extract_text_with_coordinates(image, lang='eng')
```

### Annotation Placement
```python
from src.annotation.demo_annotations import AnnotationPlacer

placer = AnnotationPlacer()
annotated_img = placer.apply_annotation(img, word_data, 'spelling_error', 'Correction needed')
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
