#!/usr/bin/env python3
"""
OCR Coordinate Extraction Test Script
For Student Composition Corrector Project

This script demonstrates:
1. OCR text extraction with coordinates
2. Language detection
3. Bounding box visualization
4. Data structure for annotation placement
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import json
import os
from typing import List, Dict, Tuple

class OCRCoordinateExtractor:
    def __init__(self):
        """Initialize OCR extractor with optimal settings"""
        self.tesseract_config = {
            'word_level': r'--oem 3 --psm 6',
            'line_level': r'--oem 3 --psm 6',
            'auto_detect': r'--oem 3 --psm 3'
        }
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to RGB for PIL compatibility
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Optional: Deskewing (basic rotation correction)
        # coords = np.column_stack(np.where(thresh > 0))
        # angle = cv2.minAreaRect(coords)[-1]
        # if angle < -45:
        #     angle = -(90 + angle)
        # else:
        #     angle = -angle
        # if abs(angle) > 0.5:  # Only correct if angle is significant
        #     (h, w) = thresh.shape[:2]
        #     center = (w // 2, h // 2)
        #     M = cv2.getRotationMatrix2D(center, angle, 1.0)
        #     thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        return img_rgb, thresh
    
    def detect_language(self, image: np.ndarray) -> str:
        """Detect the primary language in the image"""
        try:
            # Use OSD (Orientation and Script Detection)
            osd_data = pytesseract.image_to_osd(image, config='--psm 0')
            
            # Parse script information
            script_line = [line for line in osd_data.split('\n') if 'Script:' in line]
            if script_line:
                script = script_line[0].split(':')[1].strip()
                print(f"Detected script: {script}")
            
            # For now, default to English, but this can be enhanced
            return 'eng'
        except Exception as e:
            print(f"Language detection failed: {e}")
            return 'eng'  # Default to English
    
    def extract_text_with_coordinates(self, image: np.ndarray, lang: str = 'eng') -> Dict:
        """Extract text with detailed coordinate information"""
        
        # Get detailed data using image_to_data
        config = f'{self.tesseract_config["word_level"]} -l {lang}'
        data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
        
        # Process the data
        results = {
            'words': [],
            'lines': [],
            'paragraphs': [],
            'full_text': '',
            'confidence_stats': {}
        }
        
        # Extract word-level data
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            level = data['level'][i]
            conf = int(data['conf'][i])
            text = data['text'][i].strip()
            
            if conf > 0 and text:  # Only include confident detections with text
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                
                word_data = {
                    'text': text,
                    'confidence': conf,
                    'bbox': {
                        'x': x, 'y': y, 'width': w, 'height': h,
                        'x2': x + w, 'y2': y + h,
                        'center_x': x + w // 2, 'center_y': y + h // 2
                    },
                    'level': level,
                    'block_num': data['block_num'][i],
                    'par_num': data['par_num'][i],
                    'line_num': data['line_num'][i],
                    'word_num': data['word_num'][i]
                }
                
                if level == 5:  # Word level
                    results['words'].append(word_data)
                elif level == 4:  # Line level
                    results['lines'].append(word_data)
                elif level == 3:  # Paragraph level
                    results['paragraphs'].append(word_data)
        
        # Calculate confidence statistics
        confidences = [word['confidence'] for word in results['words']]
        if confidences:
            results['confidence_stats'] = {
                'mean': np.mean(confidences),
                'min': min(confidences),
                'max': max(confidences),
                'std': np.std(confidences)
            }
        
        # Get full text
        results['full_text'] = pytesseract.image_to_string(image, lang=lang, config=config).strip()
        
        return results
    
    def visualize_detections(self, image: np.ndarray, ocr_results: Dict, output_path: str):
        """Create visualization of detected text with bounding boxes"""
        img_pil = Image.fromarray(image)
        draw = ImageDraw.Draw(img_pil)
        
        # Try to use a decent font, fall back to default if not available
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                font = ImageFont.load_default()
        
        # Draw word bounding boxes
        for word in ocr_results['words']:
            bbox = word['bbox']
            confidence = word['confidence']
            text = word['text']
            
            # Color based on confidence
            if confidence > 80:
                color = 'green'
            elif confidence > 60:
                color = 'orange'
            else:
                color = 'red'
            
            # Draw bounding box
            draw.rectangle([bbox['x'], bbox['y'], bbox['x2'], bbox['y2']], 
                         outline=color, width=2)
            
            # Draw confidence score
            draw.text((bbox['x'], bbox['y'] - 15), f"{confidence}%", 
                     fill=color, font=font)
        
        # Save the visualization
        img_pil.save(output_path)
        print(f"Visualization saved to: {output_path}")
    
    def save_results_json(self, ocr_results: Dict, output_path: str):
        """Save OCR results to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ocr_results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_path}")

def create_sample_image():
    """Create a sample handwritten-style image for testing"""
    # Create a white image
    img = Image.new('RGB', (800, 600), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to get a font that looks handwritten
    try:
        # Use a larger system font
        font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Sample composition text
    text_lines = [
        "My Summer Vacation",
        "",
        "This summer I went to the beach with my family.",
        "We had so much fun playing in the sand and swimming.",
        "I built a huge sand castle that looked like a real castle!",
        "My little sister helped me collect seashells.",
        "The best part was watching the sunset over the ocean.",
        "It was the most beautiful thing I have ever seen.",
        "I can't wait to go back next year.",
        "",
        "The End"
    ]
    
    y_position = 50
    for i, line in enumerate(text_lines):
        if line:  # Skip empty lines in drawing but account for spacing
            if i == 0:  # Title
                draw.text((50, y_position), line, fill='black', font=font_large)
                y_position += 40
            else:
                draw.text((50, y_position), line, fill='black', font=font_medium)
                y_position += 30
        else:
            y_position += 20
    
    # Save the sample image
    sample_path = 'sample_composition.png'
    img.save(sample_path)
    return sample_path

def main():
    """Main test function"""
    print("🔍 OCR Coordinate Extraction Test")
    print("=" * 50)
    
    # Initialize OCR extractor
    extractor = OCRCoordinateExtractor()
    
    # Create sample image if no test image exists
    test_image_path = 'sample_composition.png'
    if not os.path.exists(test_image_path):
        print("📝 Creating sample composition image...")
        test_image_path = create_sample_image()
        print(f"✅ Sample image created: {test_image_path}")
    
    try:
        # Step 1: Preprocess image
        print("\n📸 Preprocessing image...")
        original_img, processed_img = extractor.preprocess_image(test_image_path)
        print("✅ Image preprocessing complete")
        
        # Step 2: Detect language
        print("\n🌍 Detecting language...")
        detected_lang = extractor.detect_language(processed_img)
        print(f"✅ Detected language: {detected_lang}")
        
        # Step 3: Extract text with coordinates
        print("\n📊 Extracting text with coordinates...")
        ocr_results = extractor.extract_text_with_coordinates(original_img, detected_lang)
        
        # Display results summary
        print(f"✅ OCR extraction complete!")
        print(f"   📝 Words found: {len(ocr_results['words'])}")
        print(f"   📄 Lines found: {len(ocr_results['lines'])}")
        print(f"   📋 Paragraphs found: {len(ocr_results['paragraphs'])}")
        
        if ocr_results['confidence_stats']:
            stats = ocr_results['confidence_stats']
            print(f"   📈 Confidence: {stats['mean']:.1f}% (avg), {stats['min']:.0f}%-{stats['max']:.0f}% (range)")
        
        # Step 4: Show sample words with coordinates
        print("\n📍 Sample words with coordinates:")
        for i, word in enumerate(ocr_results['words'][:5]):  # Show first 5 words
            bbox = word['bbox']
            print(f"   {i+1}. '{word['text']}' at ({bbox['x']}, {bbox['y']}) "
                  f"size: {bbox['width']}×{bbox['height']} confidence: {word['confidence']}%")
        
        if len(ocr_results['words']) > 5:
            print(f"   ... and {len(ocr_results['words']) - 5} more words")
        
        # Step 5: Create visualization
        print("\n🎨 Creating visualization...")
        extractor.visualize_detections(original_img, ocr_results, 'ocr_visualization.png')
        
        # Step 6: Save JSON results
        print("\n💾 Saving results...")
        extractor.save_results_json(ocr_results, 'ocr_results.json')
        
        # Step 7: Display full extracted text
        print("\n📄 Full extracted text:")
        print("-" * 30)
        print(ocr_results['full_text'])
        print("-" * 30)
        
        print("\n🎉 Test completed successfully!")
        print("\nFiles created:")
        print("  📁 sample_composition.png - Sample test image")
        print("  📁 ocr_visualization.png - Bounding box visualization")
        print("  📁 ocr_results.json - Detailed OCR results")
        
        print("\n💡 Next steps for your project:")
        print("  1. Use the coordinate data to place annotations")
        print("  2. Feed the text to an LLM for correction suggestions")
        print("  3. Generate visual feedback overlays")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
