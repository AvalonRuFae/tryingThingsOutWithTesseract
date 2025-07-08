#!/usr/bin/env python3
"""
Screenshot Analysis and Enhancement
For Student Composition Corrector Project

This script analyzes the screenshot OCR results and tries to improve detection
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import json
import os

class ScreenshotAnalyzer:
    def __init__(self):
        """Initialize analyzer"""
        pass
    
    def load_and_analyze_screenshot(self, image_path):
        """Load screenshot and provide detailed analysis"""
        print(f"🔍 Analyzing screenshot: {image_path}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load {image_path}")
        
        print(f"   📏 Image dimensions: {img.shape[1]} x {img.shape[0]} pixels")
        print(f"   🎨 Color channels: {img.shape[2]}")
        
        # Convert to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Analyze image properties
        self.analyze_image_properties(img_rgb)
        
        return img_rgb
    
    def analyze_image_properties(self, img_rgb):
        """Analyze image properties that affect OCR"""
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        
        # Calculate brightness
        brightness = np.mean(gray)
        print(f"   💡 Average brightness: {brightness:.1f}/255")
        
        # Calculate contrast
        contrast = np.std(gray)
        print(f"   🌓 Contrast (std dev): {contrast:.1f}")
        
        # Check for potential text regions
        # Apply edge detection to find text-like regions
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        print(f"   📝 Edge density: {edge_density:.3f} (higher = more text-like)")
        
        # Detect potential handwriting vs printed text
        # Handwriting typically has more irregular edges
        if edge_density > 0.05:
            print(f"   📖 Likely contains text content")
        else:
            print(f"   🖼️  Likely mostly image/graphics content")
    
    def try_enhanced_ocr(self, img_rgb):
        """Try different enhancement techniques for better OCR"""
        print(f"\n🔧 Trying enhanced OCR techniques...")
        
        results = []
        
        # Technique 1: Original image
        print("   1️⃣ Original image...")
        try:
            text1 = pytesseract.image_to_string(img_rgb, config='--psm 6').strip()
            words1 = len(text1.split()) if text1 else 0
            results.append(("Original", text1, words1))
            print(f"      Words detected: {words1}")
        except Exception as e:
            print(f"      ❌ Failed: {e}")
        
        # Technique 2: Grayscale
        print("   2️⃣ Grayscale conversion...")
        try:
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            text2 = pytesseract.image_to_string(gray, config='--psm 6').strip()
            words2 = len(text2.split()) if text2 else 0
            results.append(("Grayscale", text2, words2))
            print(f"      Words detected: {words2}")
        except Exception as e:
            print(f"      ❌ Failed: {e}")
        
        # Technique 3: Enhanced contrast
        print("   3️⃣ Enhanced contrast...")
        try:
            img_pil = Image.fromarray(img_rgb)
            enhancer = ImageEnhance.Contrast(img_pil)
            enhanced = enhancer.enhance(2.0)  # Increase contrast
            enhanced_array = np.array(enhanced)
            text3 = pytesseract.image_to_string(enhanced_array, config='--psm 6').strip()
            words3 = len(text3.split()) if text3 else 0
            results.append(("Enhanced Contrast", text3, words3))
            print(f"      Words detected: {words3}")
        except Exception as e:
            print(f"      ❌ Failed: {e}")
        
        # Technique 4: Different PSM modes
        for psm in [3, 4, 6, 8, 11]:
            print(f"   4️⃣ PSM mode {psm}...")
            try:
                text = pytesseract.image_to_string(img_rgb, config=f'--psm {psm}').strip()
                words = len(text.split()) if text else 0
                results.append((f"PSM {psm}", text, words))
                print(f"      Words detected: {words}")
            except Exception as e:
                print(f"      ❌ Failed: {e}")
        
        # Technique 5: Specific language optimization
        print("   5️⃣ Language-specific optimization...")
        try:
            text5 = pytesseract.image_to_string(img_rgb, lang='eng', config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?\'" ').strip()
            words5 = len(text5.split()) if text5 else 0
            results.append(("Language Optimized", text5, words5))
            print(f"      Words detected: {words5}")
        except Exception as e:
            print(f"      ❌ Failed: {e}")
        
        return results
    
    def find_best_result(self, results):
        """Find the best OCR result"""
        if not results:
            return None, "", 0
        
        # Sort by word count, then by text length
        best = max(results, key=lambda x: (x[2], len(x[1])))
        return best
    
    def create_detailed_visualization(self, img_rgb, output_path):
        """Create a detailed visualization showing OCR regions"""
        print(f"🎨 Creating detailed visualization...")
        
        # Get word-level data with coordinates
        try:
            data = pytesseract.image_to_data(img_rgb, config='--psm 6', output_type=pytesseract.Output.DICT)
            
            img_pil = Image.fromarray(img_rgb)
            draw = ImageDraw.Draw(img_pil)
            
            # Try to load font
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
                font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 10)
            except:
                font = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Draw all detected regions
            n_boxes = len(data['level'])
            word_count = 0
            
            for i in range(n_boxes):
                level = data['level'][i]
                conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
                text = data['text'][i].strip()
                
                if level == 5 and conf > 0 and text:  # Word level
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    
                    # Color based on confidence
                    if conf > 80:
                        color = 'darkgreen'
                    elif conf > 60:
                        color = 'orange'
                    elif conf > 40:
                        color = 'red'
                    else:
                        color = 'gray'
                    
                    # Draw bounding box
                    draw.rectangle([x, y, x + w, y + h], outline=color, width=2)
                    
                    # Draw word number and confidence
                    word_count += 1
                    label = f"{word_count}: {text} ({conf}%)"
                    
                    # Position label above or below the box
                    label_y = y - 20 if y > 20 else y + h + 5
                    draw.text((x, label_y), label, fill=color, font=font_small)
            
            img_pil.save(output_path)
            print(f"   ✅ Detailed visualization saved: {output_path}")
            print(f"   📊 Total words visualized: {word_count}")
            
        except Exception as e:
            print(f"   ❌ Visualization failed: {e}")

def main():
    """Main analysis function"""
    screenshot_file = [f for f in os.listdir('.') if f.startswith('Screenshot')][0]
    
    print("🔍 Screenshot Enhanced Analysis")
    print("=" * 50)
    
    analyzer = ScreenshotAnalyzer()
    
    try:
        # Load and analyze screenshot
        img_rgb = analyzer.load_and_analyze_screenshot(screenshot_file)
        
        # Try enhanced OCR techniques
        results = analyzer.try_enhanced_ocr(img_rgb)
        
        # Find best result
        best_method, best_text, best_word_count = analyzer.find_best_result(results)
        
        print(f"\n🏆 Best OCR Result:")
        print(f"   Method: {best_method}")
        print(f"   Words detected: {best_word_count}")
        print(f"   Text preview:")
        print("   " + "-" * 40)
        # Show first 300 characters
        preview = best_text[:300] + ("..." if len(best_text) > 300 else "")
        for line in preview.split('\n'):
            if line.strip():
                print(f"   {line}")
        print("   " + "-" * 40)
        
        # Create detailed visualization
        analyzer.create_detailed_visualization(img_rgb, 'screenshot_detailed_analysis.png')
        
        # Save enhanced results
        enhanced_results = {
            'source_file': screenshot_file,
            'analysis_methods': [
                {'method': method, 'text': text, 'word_count': words} 
                for method, text, words in results
            ],
            'best_method': best_method,
            'best_text': best_text,
            'best_word_count': best_word_count
        }
        
        with open('screenshot_enhanced_results.json', 'w', encoding='utf-8') as f:
            json.dump(enhanced_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Analysis Summary:")
        print(f"   📁 Source: {screenshot_file}")
        print(f"   🔬 Methods tested: {len(results)}")
        print(f"   🏅 Best method: {best_method}")
        print(f"   📝 Best word count: {best_word_count}")
        
        print(f"\n📁 Files created:")
        print(f"   • screenshot_detailed_analysis.png")
        print(f"   • screenshot_enhanced_results.json")
        
        # Provide insights for composition correction
        print(f"\n💡 Insights for Composition Correction:")
        if best_word_count > 50:
            print(f"   ✅ Good text detection - suitable for composition analysis")
        elif best_word_count > 20:
            print(f"   ⚠️  Moderate text detection - may need preprocessing")
        else:
            print(f"   ❌ Low text detection - image may need enhancement")
        
        if 'Level' in best_text and 'exemplar' in best_text:
            print(f"   📚 Appears to be an educational document or assignment")
        
        if any(word.lower() in best_text.lower() for word in ['writing', 'essay', 'composition', 'story']):
            print(f"   📝 Detected writing-related content")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
