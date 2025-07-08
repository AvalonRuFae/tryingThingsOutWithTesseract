#!/usr/bin/env python3
"""
Process Screenshot - OCR Analysis
For Student Composition Corrector Project

This script processes a real screenshot image and extracts text with coordinates
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import json
import os
from typing import List, Dict, Tuple

class ScreenshotProcessor:
    def __init__(self):
        """Initialize screenshot processor"""
        self.tesseract_config = {
            'high_quality': r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?;:\'"-()[]{}@ ',
            'auto_detect': r'--oem 3 --psm 3',
            'single_block': r'--oem 3 --psm 6'
        }
    
    def preprocess_screenshot(self, image_path: str) -> tuple:
        """Preprocess screenshot for better OCR accuracy"""
        print(f"📸 Loading screenshot: {image_path}")
        
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        print(f"   Image size: {img.shape[1]}x{img.shape[0]} pixels")
        
        # Convert to RGB for PIL compatibility
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply different preprocessing techniques
        # 1. Basic denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # 2. Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # 3. Morphological operations to clean up text
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return img_rgb, gray, thresh, cleaned
    
    def detect_text_regions(self, image: np.ndarray) -> List[Dict]:
        """Detect potential text regions in the image"""
        # Use different PSM modes to find text
        configs = [
            ('auto', self.tesseract_config['auto_detect']),
            ('single_block', self.tesseract_config['single_block']),
            ('high_quality', self.tesseract_config['high_quality'])
        ]
        
        best_results = None
        best_word_count = 0
        
        for config_name, config in configs:
            try:
                print(f"   🔍 Trying {config_name} detection...")
                data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                
                # Count valid words
                word_count = len([text for text in data['text'] if text.strip() and int(data['conf'][data['text'].index(text)]) > 30])
                print(f"     Found {word_count} words")
                
                if word_count > best_word_count:
                    best_word_count = word_count
                    best_results = (config_name, data)
                    
            except Exception as e:
                print(f"     ❌ {config_name} failed: {e}")
        
        if best_results:
            config_name, data = best_results
            print(f"   ✅ Best results from {config_name}: {best_word_count} words")
            return self.process_ocr_data(data)
        else:
            print("   ❌ No text detected")
            return []
    
    def process_ocr_data(self, data: Dict) -> List[Dict]:
        """Process OCR data into structured format"""
        results = []
        n_boxes = len(data['level'])
        
        for i in range(n_boxes):
            level = data['level'][i]
            conf = int(data['conf'][i])
            text = data['text'][i].strip()
            
            # Only include word-level detections with decent confidence
            if level == 5 and conf > 30 and text and len(text) > 0:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                
                word_data = {
                    'text': text,
                    'confidence': conf,
                    'bbox': {
                        'x': x, 'y': y, 'width': w, 'height': h,
                        'x2': x + w, 'y2': y + h,
                        'center_x': x + w // 2, 'center_y': y + h // 2
                    },
                    'block_num': data['block_num'][i],
                    'par_num': data['par_num'][i],
                    'line_num': data['line_num'][i],
                    'word_num': data['word_num'][i]
                }
                results.append(word_data)
        
        return results
    
    def visualize_detections(self, image: np.ndarray, words: List[Dict], output_path: str):
        """Create visualization of detected text"""
        img_pil = Image.fromarray(image)
        draw = ImageDraw.Draw(img_pil)
        
        # Try to use a decent font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 10)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        print(f"🎨 Drawing {len(words)} detected words...")
        
        for i, word in enumerate(words):
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
            
            # Draw word number and confidence
            label = f"{i+1}: {confidence}%"
            draw.text((bbox['x'], bbox['y'] - 15), label, fill=color, font=font_small)
            
            # Print word info
            if i < 20:  # Print first 20 words
                print(f"   {i+1:2d}. '{text}' at ({bbox['x']}, {bbox['y']}) conf: {confidence}%")
        
        if len(words) > 20:
            print(f"   ... and {len(words) - 20} more words")
        
        # Save visualization
        img_pil.save(output_path)
        print(f"✅ Visualization saved to: {output_path}")
    
    def extract_full_text(self, image: np.ndarray) -> str:
        """Extract full text from image"""
        try:
            # Try multiple approaches and pick the best one
            texts = []
            
            for config_name, config in [
                ('auto', self.tesseract_config['auto_detect']),
                ('high_quality', self.tesseract_config['high_quality'])
            ]:
                try:
                    text = pytesseract.image_to_string(image, config=config).strip()
                    if text:
                        texts.append((config_name, text, len(text.split())))
                except:
                    pass
            
            if texts:
                # Return the text with most words
                best_text = max(texts, key=lambda x: x[2])
                print(f"   📄 Best text extraction from {best_text[0]} ({best_text[2]} words)")
                return best_text[1]
            else:
                return "No text detected"
                
        except Exception as e:
            print(f"   ❌ Text extraction failed: {e}")
            return "Text extraction failed"

def main():
    """Main processing function"""
    screenshot_file = "Screenshot 2025-07-07 at 4.53.59 PM.png"
    
    print("📱 Screenshot OCR Analysis")
    print("=" * 50)
    
    # Debug: Check if file exists
    print(f"🔍 Looking for file: {screenshot_file}")
    if os.path.exists(screenshot_file):
        print(f"✅ File found!")
        file_size = os.path.getsize(screenshot_file)
        print(f"   File size: {file_size:,} bytes")
    else:
        print(f"❌ File not found. Checking directory...")
        files = [f for f in os.listdir('.') if f.startswith('Screenshot')]
        print(f"   Found screenshot files: {files}")
        if files:
            screenshot_file = files[0]
            print(f"   Using: {screenshot_file}")
        else:
            print("   No screenshot files found!")
            return
    
    # Initialize processor
    processor = ScreenshotProcessor()
    
    try:
        # Check if file exists
        if not os.path.exists(screenshot_file):
            print(f"❌ Screenshot file not found: {screenshot_file}")
            return
        
        # Step 1: Preprocess screenshot
        print("🔧 Preprocessing screenshot...")
        original_img, gray_img, thresh_img, cleaned_img = processor.preprocess_screenshot(screenshot_file)
        
        # Step 2: Try OCR on different versions
        print("\n🔍 Detecting text...")
        
        # Try on original image first
        print("   📋 Trying original image...")
        words_original = processor.detect_text_regions(original_img)
        
        # Try on cleaned image
        print("   📋 Trying cleaned image...")
        words_cleaned = processor.detect_text_regions(cleaned_img)
        
        # Use the better result
        if len(words_cleaned) > len(words_original):
            print(f"   ✅ Using cleaned image results ({len(words_cleaned)} vs {len(words_original)} words)")
            final_words = words_cleaned
            final_image = cleaned_img
        else:
            print(f"   ✅ Using original image results ({len(words_original)} vs {len(words_cleaned)} words)")
            final_words = words_original
            final_image = original_img
        
        # Step 3: Extract full text
        print("\n📄 Extracting full text...")
        full_text = processor.extract_full_text(final_image)
        
        # Step 4: Create visualization
        print(f"\n🎨 Creating visualization...")
        processor.visualize_detections(original_img, final_words, 'screenshot_ocr_visualization.png')
        
        # Step 5: Save results
        print(f"\n💾 Saving results...")
        results = {
            'source_file': screenshot_file,
            'words_detected': len(final_words),
            'words': final_words,
            'full_text': full_text,
            'confidence_stats': {}
        }
        
        # Calculate confidence statistics
        if final_words:
            confidences = [word['confidence'] for word in final_words]
            results['confidence_stats'] = {
                'mean': np.mean(confidences),
                'min': min(confidences),
                'max': max(confidences),
                'std': np.std(confidences)
            }
        
        # Save to JSON
        with open('screenshot_ocr_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Step 6: Display summary
        print(f"\n📊 Analysis Summary:")
        print(f"   📱 Source: {screenshot_file}")
        print(f"   📝 Words detected: {len(final_words)}")
        
        if results['confidence_stats']:
            stats = results['confidence_stats']
            print(f"   📈 Confidence: {stats['mean']:.1f}% avg, {stats['min']:.0f}%-{stats['max']:.0f}% range")
        
        print(f"\n📄 Extracted Text Preview:")
        print("-" * 40)
        # Show first 500 characters
        preview_text = full_text[:500] + ("..." if len(full_text) > 500 else "")
        print(preview_text)
        print("-" * 40)
        
        print(f"\n🎉 Analysis completed!")
        print(f"📁 Files created:")
        print(f"   • screenshot_ocr_visualization.png - Bounding box visualization")
        print(f"   • screenshot_ocr_results.json - Detailed OCR results")
        
        # Show some sample words
        if final_words:
            print(f"\n📍 Sample detected words:")
            for word in final_words[:10]:
                print(f"   • '{word['text']}' ({word['confidence']}% confidence)")
            if len(final_words) > 10:
                print(f"   • ... and {len(final_words) - 10} more")
        
    except Exception as e:
        print(f"❌ Error processing screenshot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
