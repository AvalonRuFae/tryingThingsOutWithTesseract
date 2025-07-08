#!/usr/bin/env python3
"""
K12GPT API Test Script
Tests different API endpoints and methods to find the correct integration
"""

import requests
import base64
import json

def test_api_endpoint(base_url: str, image_path: str):
    """Test the K12GPT API with different configurations"""
    
    print(f"🧪 Testing API endpoint: {base_url}")
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_content = f.read()
    
    image_base64 = base64.b64encode(image_content).decode('utf-8')
    
    # Test different endpoint structures
    endpoints_to_test = [
        "",  # Base URL as-is
        "/v1/images:annotate",  # Google Vision standard
        "/api/v1/images:annotate",  # With api prefix
        "/vision/v1/images:annotate",  # With vision prefix
        "/ocr",  # Simple OCR endpoint
        "/analyze",  # Generic analyze endpoint
    ]
    
    # Test different payload formats
    payloads = [
        # Google Vision API format
        {
            "requests": [
                {
                    "image": {"content": image_base64},
                    "features": [{"type": "TEXT_DETECTION", "maxResults": 100}]
                }
            ]
        },
        # Simple format
        {
            "image": image_base64,
            "features": ["TEXT_DETECTION"]
        },
        # Alternative format
        {
            "image_data": image_base64,
            "ocr_type": "text_detection"
        }
    ]
    
    # Test different headers
    header_sets = [
        {"Content-Type": "application/json"},
        {"Content-Type": "application/json", "User-Agent": "Student-Composition-Corrector/1.0"},
        {"Content-Type": "application/json", "Accept": "application/json"},
    ]
    
    for endpoint in endpoints_to_test:
        url = base_url.rstrip('/') + endpoint
        print(f"\n🔍 Testing endpoint: {url}")
        
        for i, headers in enumerate(header_sets):
            for j, payload in enumerate(payloads):
                try:
                    print(f"   📤 Trying headers set {i+1}, payload format {j+1}...")
                    
                    response = requests.post(
                        url,
                        headers=headers,
                        json=payload,
                        timeout=10
                    )
                    
                    print(f"   📊 Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("   ✅ SUCCESS! API responded with 200")
                        try:
                            result = response.json()
                            print(f"   📝 Response keys: {list(result.keys())}")
                            return url, headers, payload, result
                        except:
                            print(f"   📝 Response text: {response.text[:200]}...")
                            return url, headers, payload, response.text
                    
                    elif response.status_code == 403:
                        print("   ❌ 403 Forbidden - API key might be required")
                    elif response.status_code == 404:
                        print("   ❌ 404 Not Found - endpoint doesn't exist")
                    elif response.status_code == 405:
                        print("   ❌ 405 Method Not Allowed - try GET?")
                    else:
                        print(f"   ❌ {response.status_code}: {response.text[:100]}")
                
                except requests.exceptions.Timeout:
                    print("   ⏰ Request timed out")
                except requests.exceptions.ConnectionError:
                    print("   🔌 Connection error")
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
    
    return None, None, None, None

def test_get_requests(base_url: str):
    """Test GET requests to see if API provides documentation"""
    
    print(f"\n📖 Testing GET requests for documentation...")
    
    endpoints = ["", "/docs", "/api", "/help", "/status"]
    
    for endpoint in endpoints:
        url = base_url.rstrip('/') + endpoint
        try:
            response = requests.get(url, timeout=5)
            print(f"GET {url}: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type:
                    try:
                        data = response.json()
                        print(f"   📝 JSON response: {list(data.keys())}")
                    except:
                        pass
                elif 'html' in content_type:
                    print("   📄 HTML response (documentation page?)")
                else:
                    print(f"   📄 Response: {response.text[:100]}...")
        
        except Exception as e:
            print(f"GET {url}: Error - {str(e)}")

def main():
    """Main test function"""
    
    api_url = "https://apiproxy.k12gpt.ai/D7Kweqm/"
    image_path = "/Users/terakomari/student composition corrector/data/input/screenshot_sample.png"
    
    print("🚀 K12GPT API Testing Tool")
    print("=" * 50)
    print(f"API URL: {api_url}")
    print(f"Test Image: {image_path}")
    print()
    
    # Test GET requests first
    test_get_requests(api_url)
    
    # Test POST requests
    success_result = test_api_endpoint(api_url, image_path)
    
    if success_result[0]:  # If we found a working configuration
        url, headers, payload, result = success_result
        print("\n" + "=" * 50)
        print("🎉 SUCCESSFUL CONFIGURATION FOUND!")
        print("=" * 50)
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Payload format: {type(payload)}")
        
        # Save the working configuration
        config = {
            "url": url,
            "headers": headers,
            "payload_template": payload,
            "test_result": str(result)[:500] if isinstance(result, str) else result
        }
        
        config_file = "/Users/terakomari/student composition corrector/config/k12gpt_api_config.json"
        import os
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"💾 Configuration saved to: {config_file}")
    
    else:
        print("\n" + "=" * 50)
        print("❌ NO WORKING CONFIGURATION FOUND")
        print("=" * 50)
        print("💡 Possible solutions:")
        print("1. Check if API key/authentication is required")
        print("2. Contact K12GPT support for API documentation")
        print("3. Try different API endpoints or methods")
        print("4. Check if there are CORS or access restrictions")

if __name__ == "__main__":
    main()
