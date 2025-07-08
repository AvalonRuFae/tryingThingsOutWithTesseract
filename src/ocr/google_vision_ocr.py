#!/usr/bin/env python3
"""
Google Vision OCR Analysis Script
Analyzes the screenshot sample using Google Cloud Vision API
"""

import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from google.cloud import vision
from typing import List, Dict, Tuple
import io

# Optional cv2 import for enhanced visualization
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️  OpenCV not available. Some visualization features may be limited.")

class GoogleVisionOCR:
    """Google Cloud Vision OCR processor with coordinate extraction"""
    
    def __init__(self, credentials_path: str = None):
        """
        Initialize Google Vision client
        
        Args:
            credentials_path: Path to Google Cloud service account JSON file
        """
        if credentials_path:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        try:
            self.client = vision.ImageAnnotatorClient()
            print("✅ Google Vision client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Google Vision client: {e}")
            print("💡 Make sure you have:")
            print("   1. Google Cloud Vision API enabled")
            print("   2. Service account credentials configured")
            print("   3. GOOGLE_APPLICATION_CREDENTIALS environment variable set")
            raise
    
    def extract_text_with_coordinates(self, image_path: str) -> Dict:
        """
        Extract text and coordinates using Google Vision API
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with extracted text data and metadata
        """
        try:
            # Read image file
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            # Create Vision API image object
            image = vision.Image(content=content)
            
            # Perform text detection
            print("🔍 Performing text detection with Google Vision...")
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if response.error.message:
                raise Exception(f"Google Vision API error: {response.error.message}")
            
            if not texts:
                print("⚠️  No text detected in the image")
                return {
                    'full_text': '',
                    'words': [],
                    'word_count': 0,
                    'confidence_avg': 0.0,
                    'image_info': self._get_image_info(image_path)
                }
            
            # Extract full text (first annotation contains all text)
            full_text = texts[0].description if texts else ''
            
            # Extract individual words with coordinates
            words_data = []
            for text_annotation in texts[1:]:  # Skip first element (full text)
                vertices = text_annotation.bounding_poly.vertices
                
                # Convert vertices to bbox format
                x_coords = [vertex.x for vertex in vertices]
                y_coords = [vertex.y for vertex in vertices]
                
                bbox = {
                    'left': min(x_coords),
                    'top': min(y_coords),
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords)
                }
                
                word_data = {
                    'text': text_annotation.description,
                    'bbox': bbox,
                    'vertices': [(v.x, v.y) for v in vertices],
                    'confidence': 0.95  # Google Vision doesn't provide word-level confidence
                }
                words_data.append(word_data)
            
            # Calculate statistics
            word_count = len(words_data)
            confidence_avg = 0.95  # Default high confidence for Google Vision
            
            result = {
                'full_text': full_text,
                'words': words_data,
                'word_count': word_count,
                'confidence_avg': confidence_avg,
                'image_info': self._get_image_info(image_path),
                'api_provider': 'google_vision'
            }
            
            print(f"✅ Text extraction completed:")
            print(f"   📝 Words detected: {word_count}")
            print(f"   📊 Average confidence: {confidence_avg:.2f}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during Google Vision OCR: {str(e)}")
            raise
    
    def _get_image_info(self, image_path: str) -> Dict:
        """Get image metadata"""
        try:
            with Image.open(image_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'file_size': os.path.getsize(image_path)
                }
        except Exception as e:
            print(f"⚠️  Could not get image info: {e}")
            return {}
    
    def visualize_detection(self, image_path: str, ocr_result: Dict, output_path: str):
        """
        Create visualization of detected text with bounding boxes
        
        Args:
            image_path: Path to original image
            ocr_result: OCR result from extract_text_with_coordinates
            output_path: Path to save visualization
        """
        try:
            # Load image using PIL (more reliable than cv2)
            with Image.open(image_path) as pil_image:
                # Convert to RGB if needed
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')
                
                # Create a copy for drawing
                draw_image = pil_image.copy()
                draw = ImageDraw.Draw(draw_image)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
                small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw bounding boxes and text
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
            
            for i, word_data in enumerate(ocr_result['words']):
                color = colors[i % len(colors)]
                
                if 'vertices' in word_data:
                    # Draw polygon for exact boundaries
                    vertices = word_data['vertices']
                    draw.polygon(vertices, outline=color, width=2)
                    # Use first vertex for label position
                    label_x, label_y = vertices[0]
                else:
                    # Draw rectangle for bbox
                    bbox = word_data['bbox']
                    left = bbox['left']
                    top = bbox['top']
                    right = left + bbox['width']
                    bottom = top + bbox['height']
                    
                    draw.rectangle([left, top, right, bottom], outline=color, width=2)
                    label_x, label_y = left, top
                
                # Add text label
                text = word_data['text']
                confidence = word_data['confidence']
                
                # Position label above the bounding box
                label_y = max(0, label_y - 20)
                label_text = f"{text} ({confidence:.2f})"
                draw.text((label_x, label_y), label_text, fill=color, font=small_font)
            
            # Add summary information
            summary_text = (
                f"Google Vision OCR Results\n"
                f"Words detected: {ocr_result['word_count']}\n"
                f"Average confidence: {ocr_result['confidence_avg']:.2f}\n"
                f"API Provider: {ocr_result['api_provider']}"
            )
            
            # Draw summary box
            draw.rectangle([10, 10, 400, 100], fill=(255, 255, 255, 200), outline=(0, 0, 0))
            draw.text((20, 20), summary_text, fill=(0, 0, 0), font=font)
            
            # Save visualization
            draw_image.save(output_path)
            print(f"✅ Visualization saved to: {output_path}")
            
        except Exception as e:
            print(f"❌ Error creating visualization: {str(e)}")
            raise

def main():
    """Main function to analyze screenshot with Google Vision"""
    
    # Configuration
    input_image = "/Users/terakomari/student composition corrector/data/input/screenshot_sample.png"
    output_json = "/Users/terakomari/student composition corrector/data/results/google_vision_ocr_results.json"
    output_visualization = "/Users/terakomari/student composition corrector/data/output/google_vision_ocr_visualization.png"
    
    print("🚀 Starting Google Vision OCR Analysis")
    print("=" * 60)
    
    # Check if input image exists
    if not os.path.exists(input_image):
        print(f"❌ Input image not found: {input_image}")
        print("💡 Make sure the screenshot sample exists in data/input/")
        return
    
    try:
        # Initialize Google Vision OCR
        print("🔧 Initializing Google Vision OCR...")
        # Note: You'll need to set up credentials first
        ocr = GoogleVisionOCR()
        
        # Extract text with coordinates
        print(f"📖 Processing image: {os.path.basename(input_image)}")
        results = ocr.extract_text_with_coordinates(input_image)
        
        # Save results to JSON
        print(f"💾 Saving results to: {output_json}")
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Create visualization
        print(f"🎨 Creating visualization...")
        os.makedirs(os.path.dirname(output_visualization), exist_ok=True)
        ocr.visualize_detection(input_image, results, output_visualization)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 GOOGLE VISION OCR ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"📄 Input image: {os.path.basename(input_image)}")
        print(f"📝 Full text preview:")
        print(f"   {results['full_text'][:200]}...")
        print(f"📊 Statistics:")
        print(f"   • Words detected: {results['word_count']}")
        print(f"   • Average confidence: {results['confidence_avg']:.2f}")
        print(f"   • API Provider: {results['api_provider']}")
        print(f"📁 Output files:")
        print(f"   • JSON results: {output_json}")
        print(f"   • Visualization: {output_visualization}")
        
        print("\n✅ Google Vision OCR analysis completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        print("\n💡 Setup Instructions:")
        print("1. Install Google Cloud Vision API library:")
        print("   pip install google-cloud-vision")
        print("2. Set up Google Cloud project and enable Vision API")
        print("3. Create service account and download credentials JSON")
        print("4. Set environment variable:")
        print("   export GOOGLE_APPLICATION_CREDENTIALS='path/to/credentials.json'")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
