# Student Composition Corrector - Web Edition

A browser-based OCR and typo detection tool using **Tesseract.js** for real-time student composition analysis.

## 🚀 Quick Start

### Option 1: Python Server (Recommended)
```bash
cd web
python3 server.py
```

### Option 2: Any HTTP Server
```bash
cd web

# Using Python
python3 -m http.server 8080

# Using Node.js (if installed)
npx serve

# Using PHP (if installed)
php -S localhost:8080
```

Then open: `http://localhost:8080`

## ✨ Features

### 🔍 **Real-Time OCR**
- **Tesseract.js** - No server processing needed
- **Drag & Drop** - Easy image upload
- **Progress Tracking** - Visual feedback during processing
- **Multiple Formats** - Supports JPG, PNG, GIF, WebP

### 📝 **Text Extraction**
- Word-level coordinate mapping
- Confidence scores for each word
- Clean text output with formatting

### 🎯 **Typo Detection**
- **16+ Common Typos** - Built-in dictionary
- **Confidence Levels** - High, medium, low
- **Visual Highlighting** - Color-coded corrections
- **Suggestion Engine** - Automatic corrections

### 🎨 **Visual Annotation**
- **Bounding Boxes** - Word-level highlighting
- **Color Coding**:
  - 🔴 **Red**: High confidence typos
  - 🟡 **Yellow**: Possible typos  
  - 🟢 **Green**: Correct words
- **Inline Corrections** - Suggestions overlaid on image

### 📊 **Results & Export**
- **Statistics Dashboard** - Word count, confidence, timing
- **JSON Export** - Downloadable analysis results
- **Detailed Reports** - Complete OCR and typo data

## 🎯 How to Use

1. **Upload Image**
   - Drag & drop a student composition image
   - Or click to browse and select

2. **Wait for Processing** 
   - Tesseract.js will extract text (15-30 seconds)
   - Progress bar shows current status

3. **Review Results**
   - See extracted text and statistics
   - Check detected typos and suggestions
   - View annotated image with corrections

4. **Download Results**
   - Export complete analysis as JSON
   - Use data for further processing

## 🔧 Technical Details

### **Architecture**
```
Browser (Tesseract.js) → Text Extraction → Typo Detection → Visual Annotation
```

### **OCR Engine**
- **Tesseract.js 5.x** - WebAssembly port of Tesseract
- **Client-Side Processing** - No data sent to servers
- **Offline Capable** - Works without internet after initial load

### **File Structure**
```
web/
├── index.html          # Main application
├── css/
│   └── style.css       # Modern responsive styling
├── js/
│   ├── app.js          # Main application logic
│   └── typo-detector.js # Typo detection engine
└── server.py           # Local development server
```

### **Comparison with Python Version**

| Feature | Python Version | Web Version |
|---------|----------------|-------------|
| **OCR Engine** | Tesseract CLI | Tesseract.js |
| **Processing** | Server-side | Client-side |
| **Setup** | pip install | Just open browser |
| **Speed** | Very Fast | Moderate (15-30s) |
| **Accuracy** | Higher | Good |
| **Offline** | ✅ | ✅ |
| **Real-time** | ❌ | ✅ |

## 🌟 Advantages of Web Version

### **User Experience**
- **No Installation** - Works in any modern browser
- **Real-Time Feedback** - Progress bars and live updates
- **Mobile Friendly** - Responsive design for tablets/phones
- **Cross-Platform** - Windows, Mac, Linux, Chrome OS

### **Privacy & Security**
- **Client-Side Processing** - Images never leave the browser
- **No Server Dependencies** - Works offline
- **CORS Enabled** - Secure cross-origin headers

### **Development Benefits**
- **Easy Deployment** - Just serve static files
- **No Backend** - Pure frontend solution
- **Extensible** - Easy to add new features
- **Modern Stack** - ES6+, CSS Grid, Flexbox

## 🚀 Next Steps

1. **Test with Sample Images**
   - Copy images from `../data/input/` to test
   - Try different composition types

2. **Customize Typo Dictionary**
   - Edit `js/typo-detector.js`
   - Add more correction patterns

3. **Enhance UI**
   - Add more statistics
   - Improve annotation styles
   - Add export formats

4. **Integration**
   - Connect to Python backend API
   - Add AI-powered corrections
   - Implement user accounts

## 🔗 Integration with Python Backend

The web app can easily integrate with your existing Python system:

```javascript
// Send OCR results to Python backend
fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        text: ocrResults.text,
        words: ocrResults.words
    })
});
```

This gives you the best of both worlds:
- **Fast client-side OCR** with Tesseract.js
- **Advanced AI analysis** with your Python backend

---

**🎓 Perfect for teachers, students, and educational technology developers!**
