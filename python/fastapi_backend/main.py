#!/usr/bin/env python3
"""
FastAPI Backend for Student Composition OCR
Using Google Vision API for better accuracy

Run with: python main.py
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
import base64
import requests
from typing import List, Dict, Any
import json

app = FastAPI(title="Student Composition OCR API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GOOGLE_OCR_API_KEY = "your-google-vision-api-key-here"  # TODO: Replace with your actual API key
UPLOAD_DIR = "uploads"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Student Composition OCR API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OCR API"}

@app.post("/ocr/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze uploaded image using Google Vision API"""
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_location = None
    try:
        # Save uploaded file
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"📸 Processing image: {file.filename}")
        
        # Read and encode image
        with open(file_location, "rb") as image_file:
            content = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Prepare Google Vision API request
        url = f'https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_OCR_API_KEY}'
        payload = {
            "requests": [{
                "image": {"content": content},
                "features": [
                    {"type": "TEXT_DETECTION"},
                    {"type": "DOCUMENT_TEXT_DETECTION"}  # Better for documents
                ]
            }]
        }
        headers = {"Content-Type": "application/json"}
        
        print("🔍 Sending request to Google Vision API...")
        
        # Send request to Google Vision API
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            ocr_result = response.json()
            processed_result = process_google_vision_response(ocr_result)
            
            print(f"✅ OCR completed: {processed_result['word_count']} words detected")
            
            # Clean up uploaded file
            os.remove(file_location)
            
            return JSONResponse(content={
                "success": True,
                "filename": file.filename,
                **processed_result
            })
        else:
            print(f"❌ Google Vision API error: {response.status_code}")
            raise HTTPException(status_code=500, detail=f"Google Vision API error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error processing image: {str(e)}")
        # Clean up on error
        if file_location and os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=str(e))

def process_google_vision_response(ocr_result: Dict[Any, Any]) -> Dict[str, Any]:
    """Process Google Vision API response into our format"""
    
    if not ocr_result.get('responses') or not ocr_result['responses'][0]:
        return {
            "full_text": "",
            "words": [],
            "confidence": 0,
            "word_count": 0,
            "error": "No text detected"
        }
    
    response = ocr_result['responses'][0]
    
    # Check for errors
    if 'error' in response:
        return {
            "full_text": "",
            "words": [],
            "confidence": 0,
            "word_count": 0,
            "error": response['error']['message']
        }
    
    # Extract full text
    full_text = ""
    if 'fullTextAnnotation' in response:
        full_text = response['fullTextAnnotation']['text']
    
    # Extract word-level data with coordinates
    words = []
    text_annotations = response.get('textAnnotations', [])
    
    # Skip first annotation (it's the full text), process individual words
    for annotation in text_annotations[1:]:
        if 'boundingPoly' in annotation and 'vertices' in annotation['boundingPoly']:
            vertices = annotation['boundingPoly']['vertices']
            
            # Calculate bounding box
            x_coords = [v.get('x', 0) for v in vertices]
            y_coords = [v.get('y', 0) for v in vertices]
            
            words.append({
                "text": annotation['description'],
                "confidence": 0.95,  # Google doesn't provide word-level confidence
                "bbox": {
                    "x": min(x_coords),
                    "y": min(y_coords),
                    "width": max(x_coords) - min(x_coords),
                    "height": max(y_coords) - min(y_coords),
                    "x2": max(x_coords),
                    "y2": max(y_coords),
                    "center_x": (min(x_coords) + max(x_coords)) // 2,
                    "center_y": (min(y_coords) + max(y_coords)) // 2
                },
                "vertices": vertices
            })
    
    return {
        "full_text": full_text,
        "words": words,
        "confidence": 0.95 if full_text else 0,
        "word_count": len(words)
    }

@app.post("/ocr/test")
async def test_ocr():
    """Test endpoint to verify the API is working"""
    return {
        "message": "OCR API is working!",
        "google_api_configured": GOOGLE_OCR_API_KEY != "your-google-vision-api-key-here"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Student Composition OCR API...")
    print("📋 Available endpoints:")
    print("   GET  /              - Root endpoint")
    print("   GET  /health        - Health check")
    print("   POST /ocr/analyze   - Analyze image")
    print("   POST /ocr/test      - Test endpoint")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
