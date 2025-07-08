#!/usr/bin/env python3
"""
Typo Detection and Annotation Demo
For Student Composition Corrector Project

This script demonstrates how to detect and annotate typos
in student compositions using OCR and spelling correction.
"""

import json
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple
import difflib

class TypoDetector:
    def __init__(self):
        """Initialize typo detector with common corrections"""
        # Common typos and their corrections
        self.typo_corrections = {
            'sumer': 'summer',
            'familly': 'family', 
            'wich': 'which',
            'whether': 'weather',
            'beutiful': 'beautiful',
            'enjoied': 'enjoyed',
            'swiming': 'swimming',
            'favrite': 'favorite',
            'bulding': 'building',
            'resturant': 'restaurant',
            'delisious': 'delicious',
            'cant': "can't",
            'wont': "won't",
            'dont': "don't",
            'teh': 'the',
            'recieve': 'receive',
            'seperate': 'separate',
            'occured': 'occurred',
            'begining': 'beginning',
            'accomodate': 'accommodate'
        }
        
        # Basic English word list (simplified for demo)
        self.common_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'under', 'over',
            'a', 'an', 'is', 'was', 'are', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that',
            'these', 'those', 'i', 'me', 'my', 'mine', 'we', 'us', 'our', 'ours',
            'you', 'your', 'yours', 'he', 'him', 'his', 'she', 'her', 'hers',
            'it', 'its', 'they', 'them', 'their', 'theirs', 'what', 'which',
            'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'all', 'any',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'one', 'two',
            'three', 'first', 'last', 'good', 'new', 'old', 'great', 'little',
            'small', 'large', 'big', 'right', 'left', 'long', 'short', 'high',
            'low', 'next', 'early', 'young', 'important', 'different', 'following',
            'public', 'able', 'summer', 'family', 'beautiful', 'swimming',
            'favorite', 'building', 'restaurant', 'delicious', 'vacation',
            'beach', 'hotel', 'ocean', 'waves', 'castle', 'weather', 'perfect',
            'activity', 'enjoyed', 'stayed', 'served', 'wait', 'year', 'day',
            'every', 'back', 'went', 'also', 'food', 'sea'
        }
    
    def extract_text_with_coordinates(self, image_path: str) -> Dict:
        """Extract text with coordinates using Tesseract OCR"""
        print(f"🔍 Processing image: {image_path}")
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to RGB for Tesseract
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Get detailed OCR data
        ocr_data = pytesseract.image_to_data(
            rgb_img, 
            lang='eng',
            output_type=pytesseract.Output.DICT,
            config='--psm 6'  # Uniform block of text
        )
        
        # Process OCR results
        words = []
        n_boxes = len(ocr_data['text'])
        
        for i in range(n_boxes):
            if int(ocr_data['conf'][i]) > 30:  # Confidence threshold
                text = ocr_data['text'][i].strip()
                if text:  # Only non-empty text
                    x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i], 
                                 ocr_data['width'][i], ocr_data['height'][i])
                    
                    words.append({
                        'text': text,
                        'confidence': int(ocr_data['conf'][i]),
                        'bbox': {
                            'x': x,
                            'y': y,
                            'x2': x + w,
                            'y2': y + h,
                            'width': w,
                            'height': h,
                            'center_x': x + w // 2,
                            'center_y': y + h // 2
                        }
                    })
        
        result = {
            'image_path': image_path,
            'image_dimensions': {'width': img.shape[1], 'height': img.shape[0]},
            'words': words,
            'total_words': len(words)
        }
        
        print(f"✅ Extracted {len(words)} words")
        return result
    
    def clean_word(self, word: str) -> str:
        """Clean word by removing punctuation"""
        return ''.join(c for c in word.lower() if c.isalpha())
    
    def detect_typos(self, ocr_results: Dict) -> List[Dict]:
        """Detect typos in the extracted text"""
        typos_found = []
        
        for word_data in ocr_results['words']:
            original_word = word_data['text']
            clean_word = self.clean_word(original_word)
            
            if len(clean_word) < 2:  # Skip very short words
                continue
            
            # Check if it's a known typo
            if clean_word in self.typo_corrections:
                typos_found.append({
                    'word_data': word_data,
                    'original': original_word,
                    'clean': clean_word,
                    'correction': self.typo_corrections[clean_word],
                    'type': 'known_typo',
                    'confidence': 'high'
                })
            
            # Check if it's not in common words (potential typo)
            elif clean_word not in self.common_words:
                # Find closest match
                closest_matches = difflib.get_close_matches(
                    clean_word, 
                    list(self.common_words) + list(self.typo_corrections.values()),
                    n=1, 
                    cutoff=0.7
                )
                
                if closest_matches:
                    typos_found.append({
                        'word_data': word_data,
                        'original': original_word,
                        'clean': clean_word,
                        'correction': closest_matches[0],
                        'type': 'possible_typo',
                        'confidence': 'medium'
                    })
        
        return typos_found
    
    def draw_typo_annotation(self, img: np.ndarray, typo: Dict) -> np.ndarray:
        """Draw annotation for a typo"""
        bbox = typo['word_data']['bbox']
        
        # Different colors for different confidence levels
        if typo['confidence'] == 'high':
            color = (0, 0, 255)  # Red for known typos
        else:
            color = (0, 165, 255)  # Orange for possible typos
        
        # Draw circle around the typo
        center_x = bbox['center_x']
        center_y = bbox['center_y']
        radius = max(bbox['width'], bbox['height']) // 2 + 8
        cv2.circle(img, (center_x, center_y), radius, color, 2)
        
        # Add correction annotation
        img = self.add_correction_comment(img, bbox, typo, color)
        
        return img
    
    def add_correction_comment(self, img: np.ndarray, bbox: Dict, typo: Dict, color: Tuple[int, int, int]) -> np.ndarray:
        """Add correction comment in the margin"""
        # Convert to PIL for text rendering
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 11)
        except:
            font = ImageFont.load_default()
        
        # Create correction text
        correction_text = f"{typo['clean']} → {typo['correction']}"
        if typo['confidence'] == 'medium':
            correction_text += " (?)"
        
        # Position in right margin
        margin_x = img.shape[1] - 180
        margin_y = bbox['center_y'] - 10
        
        # Draw comment box
        text_bbox = draw.textbbox((margin_x, margin_y), correction_text, font=font)
        draw.rectangle([text_bbox[0]-2, text_bbox[1]-2, text_bbox[2]+2, text_bbox[3]+2], 
                      fill='lightyellow', outline=color, width=1)
        draw.text((margin_x, margin_y), correction_text, fill=color, font=font)
        
        # Draw connecting line
        draw.line([(bbox['x2'] + 5, bbox['center_y']), (margin_x - 5, margin_y + 8)], 
                 fill=color, width=1)
        
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def main():
    """Main demonstration function"""
    print("🔍 Typo Detection and Annotation Demo")
    print("=" * 45)
    
    detector = TypoDetector()
    
    try:
        # Process the composition with typos
        image_path = 'data/input/composition_with_typos.png'
        print(f"📸 Processing: {image_path}")
        
        # Extract text with coordinates
        ocr_results = detector.extract_text_with_coordinates(image_path)
        
        # Save OCR results
        with open('data/results/typo_ocr_results.json', 'w') as f:
            json.dump(ocr_results, f, indent=2)
        print("💾 OCR results saved to: data/results/typo_ocr_results.json")
        
        # Detect typos
        print("🔍 Detecting typos...")
        typos = detector.detect_typos(ocr_results)
        
        if typos:
            print(f"📝 Found {len(typos)} potential typos:")
            for typo in typos:
                print(f"   ❌ '{typo['original']}' → ✅ '{typo['correction']}' ({typo['confidence']} confidence)")
        else:
            print("✅ No typos detected!")
        
        # Load and annotate image
        img = cv2.imread(image_path)
        annotated_img = img.copy()
        
        # Apply annotations
        for typo in typos:
            annotated_img = detector.draw_typo_annotation(annotated_img, typo)
        
        # Save annotated image
        output_path = 'data/output/annotated_typos.png'
        cv2.imwrite(output_path, annotated_img)
        print(f"✅ Annotated image saved to: {output_path}")
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"   📄 Total words extracted: {len(ocr_results['words'])}")
        print(f"   ❌ Known typos found: {len([t for t in typos if t['confidence'] == 'high'])}")
        print(f"   ⚠️  Possible typos found: {len([t for t in typos if t['confidence'] == 'medium'])}")
        print(f"   🔴 Red circles: Confirmed typos")
        print(f"   🟠 Orange circles: Possible typos")
        print(f"   📝 Margin notes: Suggested corrections")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
