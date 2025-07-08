#!/usr/bin/env python3
"""
Mock Google Vision OCR Test
Tests the Google Vision OCR script structure without requiring actual API credentials
"""

import os
import json
import sys
from unittest.mock import Mock, patch

# Add the parent directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_mock_google_vision_response():
    """Create a mock response that mimics Google Vision API"""
    
    # Mock text annotations (simulating detected text)
    mock_texts = [
        # First annotation is the full text
        Mock(description="The quick brown fox jumps over the lazy dog. This is a sample text for testing OCR capabilities."),
        
        # Individual word annotations
        Mock(description="The", bounding_poly=Mock(vertices=[
            Mock(x=10, y=20), Mock(x=40, y=20), Mock(x=40, y=40), Mock(x=10, y=40)
        ])),
        Mock(description="quick", bounding_poly=Mock(vertices=[
            Mock(x=45, y=20), Mock(x=85, y=20), Mock(x=85, y=40), Mock(x=45, y=40)
        ])),
        Mock(description="brown", bounding_poly=Mock(vertices=[
            Mock(x=90, y=20), Mock(x=135, y=20), Mock(x=135, y=40), Mock(x=90, y=40)
        ])),
        Mock(description="fox", bounding_poly=Mock(vertices=[
            Mock(x=140, y=20), Mock(x=165, y=20), Mock(x=165, y=40), Mock(x=140, y=40)
        ])),
        # Add more mock words as needed...
    ]
    
    # Mock response object
    mock_response = Mock()
    mock_response.text_annotations = mock_texts
    mock_response.error.message = ""
    
    return mock_response

def test_google_vision_ocr_structure():
    """Test the Google Vision OCR script without actual API calls"""
    
    print("🧪 Testing Google Vision OCR Script Structure")
    print("=" * 60)
    
    # Test file paths
    input_image = "/Users/terakomari/student composition corrector/data/input/screenshot_sample.png"
    output_json = "/Users/terakomari/student composition corrector/data/results/google_vision_test_results.json"
    output_visualization = "/Users/terakomari/student composition corrector/data/output/google_vision_test_visualization.png"
    
    # Check if input image exists
    if not os.path.exists(input_image):
        print(f"❌ Input image not found: {input_image}")
        return False
    
    print(f"✅ Input image found: {os.path.basename(input_image)}")
    
    try:
        # Import the Google Vision OCR module
        from google_vision_ocr import GoogleVisionOCR
        print("✅ Google Vision OCR module imported successfully")
        
        # Test with mock API calls
        with patch('google.cloud.vision.ImageAnnotatorClient') as mock_client:
            # Set up mock
            mock_instance = Mock()
            mock_client.return_value = mock_instance
            mock_instance.text_detection.return_value = create_mock_google_vision_response()
            
            print("🔧 Creating GoogleVisionOCR instance with mocked client...")
            
            # This should work without actual credentials due to mocking
            with patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': 'fake_path.json'}):
                ocr = GoogleVisionOCR()
                print("✅ GoogleVisionOCR instance created successfully")
                
                # Test text extraction
                print("📖 Testing text extraction with mock data...")
                results = ocr.extract_text_with_coordinates(input_image)
                
                # Verify results structure
                expected_keys = ['full_text', 'words', 'word_count', 'confidence_avg', 'image_info', 'api_provider']
                for key in expected_keys:
                    if key not in results:
                        print(f"❌ Missing key in results: {key}")
                        return False
                
                print(f"✅ Results structure validated. Found {len(results['words'])} words")
                
                # Save test results
                os.makedirs(os.path.dirname(output_json), exist_ok=True)
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                print(f"✅ Test results saved to: {output_json}")
                
                # Test visualization (this should work with mock data)
                print("🎨 Testing visualization creation...")
                os.makedirs(os.path.dirname(output_visualization), exist_ok=True)
                ocr.visualize_detection(input_image, results, output_visualization)
                print(f"✅ Test visualization saved to: {output_visualization}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("📊 Test Summary:")
        print(f"   • Module import: ✅")
        print(f"   • Class instantiation: ✅")
        print(f"   • Text extraction: ✅")
        print(f"   • Results structure: ✅")
        print(f"   • JSON export: ✅")
        print(f"   • Visualization: ✅")
        
        print("\n💡 Next Steps:")
        print("1. Set up Google Cloud Vision API credentials")
        print("2. Run the actual script: python google_vision_ocr.py")
        print("3. Compare results with Tesseract OCR")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages: pip install google-cloud-vision")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Google Vision OCR Structure Test")
    print("📝 This test validates the script without requiring API credentials")
    print()
    
    success = test_google_vision_ocr_structure()
    
    if success:
        print("\n🎉 Test completed successfully!")
        return 0
    else:
        print("\n💥 Test failed!")
        return 1

if __name__ == "__main__":
    exit(main())
