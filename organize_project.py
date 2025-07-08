#!/usr/bin/env python3
"""
Project Organization Script
Student Composition Corrector Project

This script organizes all project files into a proper directory structure.
"""

import os
import shutil
from pathlib import Path

def create_project_structure():
    """Create the project directory structure"""
    
    print("📁 Creating project directory structure...")
    
    # Define directory structure
    directories = [
        "src",
        "src/core",
        "src/ocr", 
        "src/annotation",
        "src/analysis",
        "data",
        "data/input",
        "data/output", 
        "data/results",
        "tests",
        "examples",
        "examples/sample_images",
        "examples/outputs",
        "docs",
        "config"
    ]
    
    # Create directories
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}/")

def organize_files():
    """Organize existing files into appropriate directories"""
    
    print("\n📋 Organizing existing files...")
    
    # Define file organization mapping
    file_mappings = {
        # Python scripts - Core functionality
        "src/core/": [
            "test_ocr_coordinates.py"
        ],
        
        # OCR specific scripts
        "src/ocr/": [
            "process_screenshot.py",
            "analyze_screenshot.py"
        ],
        
        # Annotation and visualization scripts
        "src/annotation/": [
            "demo_annotations.py",
            "typo_detector.py"
        ],
        
        # Analysis and reporting scripts
        "src/analysis/": [
            "final_report.py"
        ],
        
        # Example and demo scripts
        "examples/": [
            "create_sample_with_typos.py",
            "create_comparison.py"
        ],
        
        # Input images
        "data/input/": [
            "Screenshot 2025-07-07 at 4.53.59 PM.png",
            "sample_composition.png",
            "composition_with_typos.png"
        ],
        
        # Output images (visualizations)
        "data/output/": [
            "ocr_visualization.png",
            "annotated_typos.png",
            "screenshot_ocr_visualization.png",
            "screenshot_detailed_analysis.png"
        ],
        
        # JSON results
        "data/results/": [
            "ocr_results.json",
            "typo_ocr_results.json",
            "screenshot_ocr_results.json",
            "screenshot_enhanced_results.json"
        ]
    }
    
    # Move files to their new locations
    for destination_dir, files in file_mappings.items():
        for filename in files:
            if os.path.exists(filename):
                destination_path = os.path.join(destination_dir, filename)
                
                # Create destination directory if it doesn't exist
                os.makedirs(destination_dir, exist_ok=True)
                
                # Move the file
                shutil.move(filename, destination_path)
                print(f"   📁 Moved: {filename} → {destination_path}")
            else:
                print(f"   ⚠️  File not found: {filename}")

def create_project_files():
    """Create essential project files"""
    
    print("\n📄 Creating project documentation and configuration files...")
    
    # Create README.md
    readme_content = """# Student Composition Corrector

An automated system for correcting student compositions using OCR, coordinate extraction, and AI-powered feedback.

## Features

- **OCR Text Extraction**: Extract text with precise coordinate mapping from student compositions
- **Error Detection**: Identify spelling, grammar, and structural issues
- **Visual Annotation**: Place corrections and feedback directly on the original document
- **Multiple Input Formats**: Support for images, scanned documents, and screenshots
- **AI Integration**: Ready for LLM-powered grammar and style analysis

## Project Structure

```
student-composition-corrector/
├── src/                    # Source code
│   ├── core/              # Core OCR functionality
│   ├── ocr/               # OCR processing modules
│   ├── annotation/        # Annotation and visualization
│   └── analysis/          # Analysis and reporting
├── data/                  # Data files
│   ├── input/            # Input images and documents
│   ├── output/           # Generated visualizations
│   └── results/          # OCR and analysis results (JSON)
├── examples/             # Example scripts and demos
├── tests/                # Unit tests
├── docs/                 # Documentation
└── config/               # Configuration files
```

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install pytesseract pillow opencv-python numpy
   ```

2. **Test OCR Extraction**:
   ```bash
   python src/core/test_ocr_coordinates.py
   ```

3. **Process Your Own Image**:
   ```bash
   python src/ocr/process_screenshot.py
   ```

## Dependencies

- Python 3.8+
- Tesseract OCR
- OpenCV
- PIL/Pillow
- NumPy
- pytesseract

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
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("   ✅ Created: README.md")
    
    # Create requirements.txt
    requirements_content = """# Core dependencies
pytesseract>=0.3.13
Pillow>=10.0.0
opencv-python>=4.8.0
numpy>=1.24.0

# Optional dependencies for enhanced functionality
matplotlib>=3.7.0
scikit-image>=0.21.0

# Development dependencies
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)
    print("   ✅ Created: requirements.txt")
    
    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
data/input/*.png
data/input/*.jpg
data/input/*.jpeg
!data/input/sample_*
data/output/*.png
data/output/*.jpg
data/results/*.json

# Temporary files
*.tmp
*.temp
*.log
"""
    
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print("   ✅ Created: .gitignore")
    
    # Create setup.py
    setup_content = """from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="student-composition-corrector",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An automated system for correcting student compositions using OCR and AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/student-composition-corrector",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "composition-corrector=src.core.test_ocr_coordinates:main",
        ],
    },
)
"""
    
    with open("setup.py", "w", encoding="utf-8") as f:
        f.write(setup_content)
    print("   ✅ Created: setup.py")

def create_init_files():
    """Create __init__.py files for Python packages"""
    
    print("\n🐍 Creating Python package __init__.py files...")
    
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py", 
        "src/ocr/__init__.py",
        "src/annotation/__init__.py",
        "src/analysis/__init__.py"
    ]
    
    for init_file in init_files:
        with open(init_file, "w", encoding="utf-8") as f:
            f.write('"""Student Composition Corrector Package"""\n')
        print(f"   ✅ Created: {init_file}")

def create_sample_config():
    """Create sample configuration files"""
    
    print("\n⚙️ Creating configuration files...")
    
    # OCR configuration
    ocr_config = """{
    "tesseract": {
        "default_config": "--oem 3 --psm 6",
        "language": "eng",
        "char_whitelist": "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?'\\"-()[]{}@ ",
        "confidence_threshold": 60
    },
    "preprocessing": {
        "denoise": true,
        "adaptive_threshold": true,
        "contrast_enhancement": false,
        "deskew": false
    },
    "output": {
        "save_visualizations": true,
        "save_json_results": true,
        "image_format": "png"
    }
}"""
    
    with open("config/ocr_config.json", "w", encoding="utf-8") as f:
        f.write(ocr_config)
    print("   ✅ Created: config/ocr_config.json")
    
    # Annotation configuration
    annotation_config = """{
    "annotation_styles": {
        "spelling_error": {
            "color": [255, 0, 0],
            "type": "circle",
            "thickness": 2
        },
        "grammar_error": {
            "color": [255, 165, 0],
            "type": "underline", 
            "thickness": 3
        },
        "suggestion": {
            "color": [0, 128, 0],
            "type": "highlight",
            "thickness": 2
        },
        "deletion": {
            "color": [255, 0, 0],
            "type": "strikethrough",
            "thickness": 2
        },
        "insertion": {
            "color": [0, 128, 0],
            "type": "caret",
            "thickness": 2
        }
    },
    "fonts": {
        "default_font": "/System/Library/Fonts/Arial.ttf",
        "fallback_font": "default",
        "comment_font_size": 12,
        "label_font_size": 10
    }
}"""
    
    with open("config/annotation_config.json", "w", encoding="utf-8") as f:
        f.write(annotation_config)
    print("   ✅ Created: config/annotation_config.json")

def main():
    """Main organization function"""
    
    print("🗂️  ORGANIZING STUDENT COMPOSITION CORRECTOR PROJECT")
    print("=" * 60)
    
    try:
        # Step 1: Create directory structure
        create_project_structure()
        
        # Step 2: Organize existing files
        organize_files()
        
        # Step 3: Create project files
        create_project_files()
        
        # Step 4: Create Python package files
        create_init_files()
        
        # Step 5: Create configuration files
        create_sample_config()
        
        print(f"\n🎉 PROJECT ORGANIZATION COMPLETED!")
        print(f"=" * 60)
        
        print(f"\n📁 Final Project Structure:")
        print(f"student-composition-corrector/")
        print(f"├── 📂 src/                   # Source code")
        print(f"│   ├── 📂 core/              # Core OCR functionality")
        print(f"│   ├── 📂 ocr/               # OCR processing modules")
        print(f"│   ├── 📂 annotation/        # Annotation and visualization")
        print(f"│   └── 📂 analysis/          # Analysis and reporting")
        print(f"├── 📂 data/                  # Data files")
        print(f"│   ├── 📂 input/             # Input images")
        print(f"│   ├── 📂 output/            # Visualizations")
        print(f"│   └── 📂 results/           # JSON results")
        print(f"├── 📂 examples/              # Example scripts")
        print(f"├── 📂 config/                # Configuration files")
        print(f"├── 📄 README.md              # Project documentation")
        print(f"├── 📄 requirements.txt       # Dependencies")
        print(f"├── 📄 setup.py               # Package setup")
        print(f"└── 📄 .gitignore             # Git ignore rules")
        
        print(f"\n🚀 Next Steps:")
        print(f"1. Install dependencies: pip install -r requirements.txt")
        print(f"2. Test core functionality: python src/core/test_ocr_coordinates.py")
        print(f"3. Process your images: python src/ocr/process_screenshot.py")
        print(f"4. Explore examples: check examples/ directory")
        print(f"5. Read documentation: open README.md")
        
    except Exception as e:
        print(f"❌ Error during organization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
