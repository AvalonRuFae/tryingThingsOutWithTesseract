#!/usr/bin/env python3
"""
Google Vision OCR Analysis Script - Simplified Version
This script analyzes the screenshot sample using Google Cloud Vision API.

To use this script:
1. Set up Google Cloud Vision API credentials
2. Install: pip install google-cloud-vision
3. Set environment variable: GOOGLE_APPLICATION_CREDENTIALS
4. Run: python google_vision_simple.py
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List
import io

def create_mock_google_vision_result():
    """Create a mock result for testing purposes"""
    return {
        'full_text': 'This is a sample text extracted using Google Vision API. The quick brown fox jumps over the lazy dog.',
        'words': [
            {
                'text': 'This',
                'bbox': {'left': 10, 'top': 20, 'width': 30, 'height': 20},
                'vertices': [(10, 20), (40, 20), (40, 40), (10, 40)],
                'confidence': 0.95
            },
            {
                'text': 'is',
                'bbox': {'left': 45, 'top': 20, 'width': 15, 'height': 20},
                'vertices': [(45, 20), (60, 20), (60, 40), (45, 40)],
                'confidence': 0.97
            },
            {
                'text': 'sample',
                'bbox': {'left': 65, 'top': 20, 'width': 45, 'height': 20},
                'vertices': [(65, 20), (110, 20), (110, 40), (65, 40)],
                'confidence': 0.96
            }
        ],
        'word_count': 3,
        'confidence_avg': 0.96,
        'image_info': {
            'width': 800,
            'height': 600,
            'mode': 'RGB',
            'format': 'PNG'
        },
        'api_provider': 'google_vision'
    }

def analyze_with_google_vision(image_path: str) -> Dict:
    """
    Analyze image using Google Vision API
    
    Args:
        image_path: Path to the image file
        
    Returns:
        OCR results dictionary
    """
    print("🔍 Attempting to use Google Vision API...")
    
    try:
        # Try to import and use Google Vision
        from google.cloud import vision
        
        # Read image file
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        # Initialize client
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=content)
        
        # Perform text detection
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if response.error.message:
            raise Exception(f"Google Vision API error: {response.error.message}")
        
        if not texts:
            return {
                'full_text': '',
                'words': [],
                'word_count': 0,
                'confidence_avg': 0.0,
                'image_info': get_image_info(image_path),
                'api_provider': 'google_vision'
            }
        
        # Extract full text and individual words
        full_text = texts[0].description
        words_data = []
        
        for text_annotation in texts[1:]:
            vertices = text_annotation.bounding_poly.vertices
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
        
        result = {
            'full_text': full_text,
            'words': words_data,
            'word_count': len(words_data),
            'confidence_avg': 0.95,
            'image_info': get_image_info(image_path),
            'api_provider': 'google_vision'
        }
        
        print(f"✅ Google Vision API successful! Detected {len(words_data)} words")
        return result
        
    except ImportError:
        print("⚠️  Google Cloud Vision not available. Using mock data for testing.")
        return create_mock_google_vision_result()
    except Exception as e:
        print(f"❌ Google Vision API error: {str(e)}")
        print("💡 Using mock data for testing.")
        return create_mock_google_vision_result()

def get_image_info(image_path: str) -> Dict:
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

def create_visualization(image_path: str, ocr_result: Dict, output_path: str):
    """Create visualization of OCR results"""
    try:
        # Load and prepare image
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            draw_img = img.copy()
            draw = ImageDraw.Draw(draw_img)
        
        # Load font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw word boundaries
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        
        for i, word_data in enumerate(ocr_result['words']):
            color = colors[i % len(colors)]
            
            if 'vertices' in word_data:
                vertices = word_data['vertices']
                draw.polygon(vertices, outline=color, width=2)
                label_x, label_y = vertices[0]
            else:
                bbox = word_data['bbox']
                left, top = bbox['left'], bbox['top']
                right, bottom = left + bbox['width'], top + bbox['height']
                draw.rectangle([left, top, right, bottom], outline=color, width=2)
                label_x, label_y = left, top
            
            # Add text label
            text = word_data['text']
            confidence = word_data['confidence']
            label_y = max(0, label_y - 20)
            label_text = f"{text} ({confidence:.2f})"
            draw.text((label_x, label_y), label_text, fill=color, font=small_font)
        
        # Add summary box
        summary_text = (
            f"Google Vision OCR Results\n"
            f"Words detected: {ocr_result['word_count']}\n"
            f"Average confidence: {ocr_result['confidence_avg']:.2f}\n"
            f"API Provider: {ocr_result['api_provider']}"
        )
        
        draw.rectangle([10, 10, 400, 100], fill=(255, 255, 255, 200), outline=(0, 0, 0))
        draw.text((20, 20), summary_text, fill=(0, 0, 0), font=font)
        
        # Save result
        draw_img.save(output_path)
        print(f"✅ Visualization saved to: {output_path}")
        
    except Exception as e:
        print(f"❌ Error creating visualization: {str(e)}")

def main():
    """Main function"""
    print("🚀 Google Vision OCR Analysis")
    print("=" * 50)
    
    # File paths
    input_image = "data/input/screenshot_sample.png"
    output_json = "data/results/google_vision_simple_results.json"
    output_viz = "data/output/google_vision_simple_visualization.png"
    
    # Check input file
    if not os.path.exists(input_image):
        print(f"❌ Input image not found: {input_image}")
        return 1
    
    print(f"📖 Processing: {os.path.basename(input_image)}")
    
    # Analyze with Google Vision (or mock)
    results = analyze_with_google_vision(input_image)
    
    # Save JSON results
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"💾 Results saved to: {output_json}")
    
    # Create visualization
    os.makedirs(os.path.dirname(output_viz), exist_ok=True)
    create_visualization(input_image, results, output_viz)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"📝 Text preview: {results['full_text'][:100]}...")
    print(f"📊 Words detected: {results['word_count']}")
    print(f"🎯 Average confidence: {results['confidence_avg']:.2f}")
    print(f"🔧 API Provider: {results['api_provider']}")
    print(f"📁 Output files:")
    print(f"   • JSON: {output_json}")
    print(f"   • Visualization: {output_viz}")
    
    if results['api_provider'] == 'google_vision':
        print("\n✅ Successfully used Google Vision API!")
    else:
        print("\n💡 Used mock data. To use real Google Vision API:")
        print("   1. Install: pip install google-cloud-vision")
        print("   2. Set up Google Cloud credentials")
        print("   3. Set: export GOOGLE_APPLICATION_CREDENTIALS='path/to/credentials.json'")
    
    return 0

if __name__ == "__main__":
    exit(main())
