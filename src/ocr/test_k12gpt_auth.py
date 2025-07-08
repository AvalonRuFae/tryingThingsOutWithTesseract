#!/usr/bin/env python3
"""
K12GPT API Authentication Test
Tests different authentication methods for the K12GPT API
"""

import requests
import base64
import json

def test_with_auth_patterns(base_url: str, image_path: str):
    """Test API with different authentication patterns"""
    
    print(f"🔐 Testing authentication patterns for: {base_url}")
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_content = f.read()
    
    image_base64 = base64.b64encode(image_content).decode('utf-8')
    
    # Basic payload
    payload = {
        "requests": [
            {
                "image": {"content": image_base64},
                "features": [{"type": "TEXT_DETECTION", "maxResults": 100}]
            }
        ]
    }
    
    # Different authentication patterns to test
    auth_patterns = [
        # Pattern 1: API Key in header
        {"headers": {"Content-Type": "application/json", "X-API-Key": "YOUR_API_KEY"}},
        {"headers": {"Content-Type": "application/json", "API-Key": "YOUR_API_KEY"}},
        {"headers": {"Content-Type": "application/json", "Authorization": "ApiKey YOUR_API_KEY"}},
        
        # Pattern 2: Bearer token
        {"headers": {"Content-Type": "application/json", "Authorization": "Bearer YOUR_TOKEN"}},
        
        # Pattern 3: Basic auth (if username/password style)
        {"headers": {"Content-Type": "application/json", "Authorization": "Basic YOUR_CREDENTIALS"}},
        
        # Pattern 4: Custom headers
        {"headers": {"Content-Type": "application/json", "K12GPT-API-Key": "YOUR_KEY"}},
        {"headers": {"Content-Type": "application/json", "X-K12GPT-Key": "YOUR_KEY"}},
        
        # Pattern 5: API key in URL params
        {"params": {"api_key": "YOUR_API_KEY", "key": "YOUR_KEY"}},
        
        # Pattern 6: API key in payload
        {"payload_extra": {"api_key": "YOUR_API_KEY", "auth_token": "YOUR_TOKEN"}},
    ]
    
    endpoints = [
        "",
        "/v1/images:annotate",
        "/vision/v1/images:annotate"
    ]
    
    for endpoint in endpoints:
        url = base_url.rstrip('/') + endpoint
        print(f"\n🔍 Testing endpoint: {url}")
        
        for i, pattern in enumerate(auth_patterns):
            print(f"   🔐 Auth pattern {i+1}...")
            
            # Prepare request parameters
            headers = pattern.get("headers", {"Content-Type": "application/json"})
            params = pattern.get("params", {})
            
            # Modify payload if needed
            test_payload = payload.copy()
            if "payload_extra" in pattern:
                test_payload.update(pattern["payload_extra"])
            
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    params=params,
                    json=test_payload,
                    timeout=10
                )
                
                status = response.status_code
                print(f"      📊 Status: {status}")
                
                if status == 200:
                    print("      ✅ SUCCESS!")
                    return url, headers, params, test_payload, response.json()
                elif status == 401:
                    print("      🔑 401 Unauthorized - wrong or missing credentials")
                elif status == 403:
                    print("      🚫 403 Forbidden - access denied")
                elif status == 400:
                    print("      ❌ 400 Bad Request - check payload format")
                    print(f"         Response: {response.text[:100]}")
                elif status == 404:
                    print("      🔍 404 Not Found - endpoint doesn't exist")
                else:
                    print(f"      ❓ {status}: {response.text[:50]}")
            
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
    
    return None

def suggest_next_steps():
    """Provide suggestions for getting API access"""
    
    print("\n" + "=" * 60)
    print("💡 AUTHENTICATION REQUIRED - NEXT STEPS")
    print("=" * 60)
    
    print("\n🔍 To use the K12GPT API, you likely need:")
    print("1. **API Key** or **Authentication Token**")
    print("2. **Documentation** on how to authenticate")
    print("3. **Account setup** with K12GPT")
    
    print("\n📞 Contact K12GPT Support:")
    print("• Ask for API documentation")
    print("• Request API key/token")
    print("• Get authentication instructions")
    
    print("\n🔧 Common API Authentication Methods:")
    print("• Header: Authorization: Bearer YOUR_TOKEN")
    print("• Header: X-API-Key: YOUR_KEY")
    print("• URL Parameter: ?api_key=YOUR_KEY")
    print("• Payload field: {'api_key': 'YOUR_KEY'}")
    
    print("\n🌐 Alternative OCR Solutions:")
    print("• Google Cloud Vision API (setup guide available)")
    print("• Azure Computer Vision")
    print("• AWS Textract")
    print("• OCR.space (free tier)")
    print("• EasyOCR (local processing)")

def create_api_template():
    """Create a template for when authentication is available"""
    
    template = '''#!/usr/bin/env python3
"""
K12GPT OCR Client - Template
Fill in the authentication details when available
"""

import requests
import base64
import json

class K12GPTOCRClient:
    def __init__(self, api_endpoint, api_key=None, auth_token=None):
        self.api_endpoint = api_endpoint.rstrip('/')
        self.api_key = api_key
        self.auth_token = auth_token
    
    def get_headers(self):
        headers = {"Content-Type": "application/json"}
        
        # Add authentication (uncomment and modify as needed)
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            # OR: headers["Authorization"] = f"ApiKey {self.api_key}"
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        return headers
    
    def extract_text(self, image_path):
        # Read and encode image
        with open(image_path, 'rb') as f:
            image_content = f.read()
        
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Prepare payload
        payload = {
            "requests": [{
                "image": {"content": image_base64},
                "features": [{"type": "TEXT_DETECTION", "maxResults": 100}]
            }]
        }
        
        # Add API key to payload if needed
        # payload["api_key"] = self.api_key
        
        # Make request
        response = requests.post(
            f"{self.api_endpoint}/v1/images:annotate",  # Adjust endpoint as needed
            headers=self.get_headers(),
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API error {response.status_code}: {response.text}")

# Usage example (fill in your credentials):
# client = K12GPTOCRClient(
#     api_endpoint="https://apiproxy.k12gpt.ai/D7Kweqm/",
#     api_key="YOUR_API_KEY_HERE",
#     auth_token="YOUR_TOKEN_HERE"
# )
# result = client.extract_text("path/to/image.png")
'''
    
    template_path = "/Users/terakomari/student composition corrector/src/ocr/k12gpt_ocr_template.py"
    with open(template_path, 'w') as f:
        f.write(template)
    
    print(f"\n💾 Created API template: {template_path}")
    print("   Fill in authentication details when available")

def main():
    """Main function"""
    
    api_url = "https://apiproxy.k12gpt.ai/D7Kweqm/"
    image_path = "/Users/terakomari/student composition corrector/data/input/screenshot_sample.png"
    
    print("🔐 K12GPT API Authentication Testing")
    print("=" * 50)
    
    # Test authentication patterns
    result = test_with_auth_patterns(api_url, image_path)
    
    if result:
        print("\n🎉 WORKING AUTHENTICATION FOUND!")
        url, headers, params, payload, response = result
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Params: {params}")
        
        # Save working config
        config = {
            "url": url,
            "headers": headers,
            "params": params,
            "payload": payload,
            "response_sample": response
        }
        
        config_file = "/Users/terakomari/student composition corrector/config/k12gpt_working_config.json"
        import os
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"💾 Working configuration saved to: {config_file}")
    
    else:
        suggest_next_steps()
        create_api_template()

if __name__ == "__main__":
    main()
