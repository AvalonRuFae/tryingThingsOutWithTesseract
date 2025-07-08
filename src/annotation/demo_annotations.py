#!/usr/bin/env python3
"""
Annotation Placement Demo
For Student Composition Corrector Project

This script demonstrates how to use OCR coordinate data 
to place visual annotations on student compositions.
"""

import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Tuple

class AnnotationPlacer:
    def __init__(self):
        """Initialize annotation placer with styling options"""
        self.annotation_styles = {
            'spelling_error': {
                'color': (255, 0, 0),  # Red
                'type': 'circle',
                'thickness': 2
            },
            'grammar_error': {
                'color': (255, 165, 0),  # Orange
                'type': 'underline',
                'thickness': 3
            },
            'suggestion': {
                'color': (0, 128, 0),  # Green
                'type': 'highlight',
                'thickness': 2
            },
            'deletion': {
                'color': (255, 0, 0),  # Red
                'type': 'strikethrough',
                'thickness': 2
            },
            'insertion': {
                'color': (0, 128, 0),  # Green
                'type': 'caret',
                'thickness': 2
            }
        }
    
    def load_ocr_results(self, json_path: str) -> Dict:
        """Load OCR results from JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def find_word_coordinates(self, ocr_results: Dict, target_word: str, case_sensitive: bool = False) -> List[Dict]:
        """Find coordinates of specific words in the OCR results"""
        matches = []
        for word_data in ocr_results['words']:
            word_text = word_data['text']
            if not case_sensitive:
                word_text = word_text.lower()
                target_word = target_word.lower()
            
            if word_text == target_word:
                matches.append(word_data)
        
        return matches
    
    def find_words_in_range(self, ocr_results: Dict, start_word: str, end_word: str) -> List[Dict]:
        """Find all words between start_word and end_word (inclusive)"""
        words = ocr_results['words']
        start_idx = None
        end_idx = None
        
        # Find indices
        for i, word_data in enumerate(words):
            if word_data['text'].lower() == start_word.lower() and start_idx is None:
                start_idx = i
            if word_data['text'].lower() == end_word.lower() and start_idx is not None:
                end_idx = i
                break
        
        if start_idx is not None and end_idx is not None:
            return words[start_idx:end_idx + 1]
        return []
    
    def draw_circle_annotation(self, img: np.ndarray, bbox: Dict, color: Tuple[int, int, int], thickness: int):
        """Draw a circle around a word"""
        center_x = bbox['center_x']
        center_y = bbox['center_y']
        radius = max(bbox['width'], bbox['height']) // 2 + 5
        cv2.circle(img, (center_x, center_y), radius, color, thickness)
    
    def draw_underline_annotation(self, img: np.ndarray, bbox: Dict, color: Tuple[int, int, int], thickness: int):
        """Draw an underline below a word"""
        y_pos = bbox['y2'] + 2
        cv2.line(img, (bbox['x'], y_pos), (bbox['x2'], y_pos), color, thickness)
    
    def draw_strikethrough_annotation(self, img: np.ndarray, bbox: Dict, color: Tuple[int, int, int], thickness: int):
        """Draw a strikethrough across a word"""
        y_pos = bbox['center_y']
        cv2.line(img, (bbox['x'], y_pos), (bbox['x2'], y_pos), color, thickness)
    
    def draw_highlight_annotation(self, img: np.ndarray, bbox: Dict, color: Tuple[int, int, int], thickness: int):
        """Draw a highlight rectangle around a word"""
        # Create a semi-transparent overlay
        overlay = img.copy()
        cv2.rectangle(overlay, (bbox['x'] - 2, bbox['y'] - 2), (bbox['x2'] + 2, bbox['y2'] + 2), color, -1)
        cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)
        # Add border
        cv2.rectangle(img, (bbox['x'] - 2, bbox['y'] - 2), (bbox['x2'] + 2, bbox['y2'] + 2), color, thickness)
    
    def draw_caret_annotation(self, img: np.ndarray, bbox: Dict, color: Tuple[int, int, int], thickness: int):
        """Draw a caret (^) for insertion points"""
        x_pos = bbox['x'] - 10
        y_bottom = bbox['y2']
        y_top = bbox['y']
        
        # Draw caret shape
        cv2.line(img, (x_pos, y_bottom), (x_pos - 5, y_top), color, thickness)
        cv2.line(img, (x_pos, y_bottom), (x_pos + 5, y_top), color, thickness)
    
    def add_margin_comment(self, img: np.ndarray, bbox: Dict, comment: str, color: Tuple[int, int, int]):
        """Add a comment in the margin"""
        # Convert to PIL for text rendering
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        # Position comment in right margin
        comment_x = img.shape[1] - 200
        comment_y = bbox['center_y']
        
        # Draw comment box
        bbox_text = draw.textbbox((comment_x, comment_y), comment, font=font)
        draw.rectangle(bbox_text, fill='lightyellow', outline=color, width=1)
        draw.text((comment_x, comment_y), comment, fill=color, font=font)
        
        # Draw line connecting to the word
        draw.line([(bbox['x2'] + 5, bbox['center_y']), (comment_x - 5, comment_y + 10)], 
                 fill=color, width=1)
        
        # Convert back to OpenCV format
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    
    def apply_annotation(self, img: np.ndarray, word_data: Dict, annotation_type: str, comment: str = None):
        """Apply a specific annotation to a word"""
        style = self.annotation_styles.get(annotation_type, self.annotation_styles['spelling_error'])
        bbox = word_data['bbox']
        color = style['color']
        thickness = style['thickness']
        
        if style['type'] == 'circle':
            self.draw_circle_annotation(img, bbox, color, thickness)
        elif style['type'] == 'underline':
            self.draw_underline_annotation(img, bbox, color, thickness)
        elif style['type'] == 'strikethrough':
            self.draw_strikethrough_annotation(img, bbox, color, thickness)
        elif style['type'] == 'highlight':
            self.draw_highlight_annotation(img, bbox, color, thickness)
        elif style['type'] == 'caret':
            self.draw_caret_annotation(img, bbox, color, thickness)
        
        # Add margin comment if provided
        if comment:
            img = self.add_margin_comment(img, bbox, comment, color)
        
        return img

def create_sample_corrections():
    """Create sample corrections for demonstration"""
    return [
        {
            'word': 'I',  # This appears as '|' in OCR - common OCR error
            'type': 'spelling_error',
            'comment': 'Should be "I"'
        },
        {
            'word': 'castle',
            'type': 'suggestion',
            'comment': 'Good descriptive word!'
        },
        {
            'word': 'huge',
            'type': 'highlight',
            'comment': 'Great adjective'
        },
        {
            'word': 'beautiful',
            'type': 'underline',
            'comment': 'Excellent vocabulary'
        }
    ]

def main():
    """Main demonstration function"""
    print("🎨 Annotation Placement Demo")
    print("=" * 40)
    
    # Initialize annotation placer
    placer = AnnotationPlacer()
    
    try:
        # Load OCR results
        print("📊 Loading OCR results...")
        ocr_results = placer.load_ocr_results('ocr_results.json')
        print(f"✅ Loaded {len(ocr_results['words'])} words")
        
        # Load original image
        print("📸 Loading original image...")
        img = cv2.imread('sample_composition.png')
        if img is None:
            raise ValueError("Could not load sample_composition.png")
        
        # Create sample corrections
        print("✏️ Applying sample corrections...")
        corrections = create_sample_corrections()
        
        annotated_img = img.copy()
        
        for correction in corrections:
            # Find the word to correct
            matches = placer.find_word_coordinates(ocr_results, correction['word'])
            
            if matches:
                print(f"   📍 Annotating '{correction['word']}' as {correction['type']}")
                word_data = matches[0]  # Use first match
                annotated_img = placer.apply_annotation(
                    annotated_img, 
                    word_data, 
                    correction['type'], 
                    correction.get('comment')
                )
            else:
                print(f"   ❌ Word '{correction['word']}' not found")
        
        # Demonstrate finding OCR errors (I vs |)
        print("🔍 Finding OCR errors...")
        pipe_matches = placer.find_word_coordinates(ocr_results, '|')
        for match in pipe_matches:
            print(f"   📍 Found OCR error '|' at ({match['bbox']['x']}, {match['bbox']['y']})")
            annotated_img = placer.apply_annotation(
                annotated_img, 
                match, 
                'spelling_error', 
                'OCR error: should be "I"'
            )
        
        # Save annotated image
        output_path = 'annotated_composition.png'
        cv2.imwrite(output_path, annotated_img)
        print(f"✅ Annotated image saved to: {output_path}")
        
        # Print summary
        print(f"\n📋 Annotation Summary:")
        print(f"   🔴 Red circles: Spelling errors")
        print(f"   🟠 Orange underlines: Grammar suggestions")
        print(f"   🟢 Green highlights: Good word choices")
        print(f"   📝 Margin comments: Detailed feedback")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"   📁 Input: sample_composition.png")
        print(f"   📁 Output: annotated_composition.png")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
