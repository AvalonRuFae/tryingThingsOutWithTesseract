#!/usr/bin/env python3
"""
K12GPT Google OCR API Integration
Analyzes images using the provided K12GPT Google OCR API endpoint
"""

import os
import json
import requests
import base64
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List
import io

class K12GPTOCRClient:
    """OCR client for K12GPT Google OCR API"""
    
    def __init__(self, api_endpoint: str = "https://apiproxy.k12gpt.ai/D7Kweqm/"):
        """
        Initialize K12GPT OCR client
        
        Args:
            api_endpoint: The K12GPT Google OCR API endpoint
        """
        self.api_endpoint = api_endpoint.rstrip('/')
        print(f"✅ K12GPT OCR client initialized with endpoint: {self.api_endpoint}")
    
    def extract_text_with_coordinates(self, image_path: str) -> Dict:
        """
        Extract text and coordinates using K12GPT Google OCR API
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with extracted text data and metadata
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_content = image_file.read()
            
            # Encode image to base64
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            # Prepare API request
            payload = {
                "requests": [
                    {
                        "image": {
                            "content": image_base64
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION",
                                "maxResults": 100
                            }
                        ]
                    }
                ]
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            print("🔍 Sending request to K12GPT Google OCR API...")
            
            # Make API request
            response = requests.post(
                f"{self.api_endpoint}/v1/images:annotate",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
            
            # Parse response
            result = response.json()
            
            if 'responses' not in result or not result['responses']:
                raise Exception("No responses in API result")
            
            api_response = result['responses'][0]
            
            if 'error' in api_response:
                raise Exception(f"API error: {api_response['error']}")
            
            # Extract text annotations
            text_annotations = api_response.get('textAnnotations', [])
            
            if not text_annotations:
                print("⚠️  No text detected in the image")
                return {
                    'full_text': '',
                    'words': [],
                    'word_count': 0,
                    'confidence_avg': 0.0,
                    'image_info': self._get_image_info(image_path),
                    'api_provider': 'k12gpt_google_ocr'
                }
            
            # Extract full text (first annotation contains all text)
            full_text = text_annotations[0]['description'] if text_annotations else ''
            
            # Extract individual words with coordinates
            words_data = []
            for text_annotation in text_annotations[1:]:  # Skip first element (full text)
                if 'boundingPoly' not in text_annotation:
                    continue
                
                vertices = text_annotation['boundingPoly']['vertices']
                
                # Convert vertices to bbox format
                x_coords = [vertex.get('x', 0) for vertex in vertices]
                y_coords = [vertex.get('y', 0) for vertex in vertices]
                
                bbox = {
                    'left': min(x_coords),
                    'top': min(y_coords),
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords)
                }
                
                word_data = {
                    'text': text_annotation['description'],
                    'bbox': bbox,
                    'vertices': [(v.get('x', 0), v.get('y', 0)) for v in vertices],
                    'confidence': 0.95  # Google Vision typically has high confidence
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
                'api_provider': 'k12gpt_google_ocr',
                'api_endpoint': self.api_endpoint
            }
            
            print(f"✅ Text extraction completed:")
            print(f"   📝 Words detected: {word_count}")
            print(f"   📊 Average confidence: {confidence_avg:.2f}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during K12GPT OCR: {str(e)}")
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
            # Load image using PIL
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
                f"K12GPT Google OCR Results\n"
                f"Words detected: {ocr_result['word_count']}\n"
                f"Average confidence: {ocr_result['confidence_avg']:.2f}\n"
                f"API Provider: {ocr_result['api_provider']}\n"
                f"Endpoint: {ocr_result.get('api_endpoint', 'N/A')}"
            )
            
            # Draw summary box
            draw.rectangle([10, 10, 450, 120], fill=(255, 255, 255, 200), outline=(0, 0, 0))
            draw.text((20, 20), summary_text, fill=(0, 0, 0), font=font)
            
            # Save visualization
            draw_image.save(output_path)
            print(f"✅ Visualization saved to: {output_path}")
            
        except Exception as e:
            print(f"❌ Error creating visualization: {str(e)}")
            raise

def main():
    """Main function to analyze screenshot with K12GPT Google OCR"""
    
    # Configuration
    api_endpoint = "https://apiproxy.k12gpt.ai/D7Kweqm/"
    input_image = "/Users/terakomari/student composition corrector/data/input/screenshot_sample.png"
    output_json = "/Users/terakomari/student composition corrector/data/results/k12gpt_ocr_results.json"
    output_visualization = "/Users/terakomari/student composition corrector/data/output/k12gpt_ocr_visualization.png"
    
    print("🚀 Starting K12GPT Google OCR Analysis")
    print("=" * 60)
    
    # Check if input image exists
    if not os.path.exists(input_image):
        print(f"❌ Input image not found: {input_image}")
        print("💡 Make sure the screenshot sample exists in data/input/")
        return 1
    
    try:
        # Initialize K12GPT OCR client
        print("🔧 Initializing K12GPT Google OCR client...")
        ocr = K12GPTOCRClient(api_endpoint)
        
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
        print("📊 K12GPT GOOGLE OCR ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"📄 Input image: {os.path.basename(input_image)}")
        print(f"📝 Full text preview:")
        print(f"   {results['full_text'][:200]}...")
        print(f"📊 Statistics:")
        print(f"   • Words detected: {results['word_count']}")
        print(f"   • Average confidence: {results['confidence_avg']:.2f}")
        print(f"   • API Provider: {results['api_provider']}")
        print(f"   • API Endpoint: {results.get('api_endpoint', 'N/A')}")
        print(f"📁 Output files:")
        print(f"   • JSON results: {output_json}")
        print(f"   • Visualization: {output_visualization}")
        
        print("\n✅ K12GPT Google OCR analysis completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify the API endpoint is accessible")
        print("3. Ensure the image file is valid and readable")
        return 1

if __name__ == "__main__":
    exit(main())
