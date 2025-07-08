# Chinese OCR Troubleshooting Guide

## Common Issues and Solutions

### 1. 🔤 Getting Gibberish/Random Characters

**Symptoms:**
- OCR returns random letters, symbols, or nonsensical characters
- Text looks like: "aK3$#mPz" instead of Chinese characters

**Solutions:**
- ✅ **Try Traditional Chinese (`chi_tra`)** if using Simplified fails
- ✅ **Use higher resolution images** (at least 300 DPI)
- ✅ **Ensure text is printed, not handwritten**
- ✅ **Check image preprocessing** - use the debug tool
- ✅ **Verify image contains actual Chinese text**

### 2. 📉 Low Confidence Scores (<30%)

**Symptoms:**
- OCR confidence below 30%
- Some characters recognized but many errors

**Solutions:**
- 📐 **Increase image resolution** (scale up 2-3x)
- 🌓 **Improve contrast** between text and background
- 📏 **Ensure text is not skewed or rotated**
- 🔍 **Use larger font sizes if possible**
- 🧹 **Clean up image noise/artifacts**

### 3. 🚫 No Chinese Characters Detected

**Symptoms:**
- OCR returns empty results or only English characters
- Word count is 0 or very low

**Solutions:**
- 🔄 **Switch between Simplified and Traditional Chinese**
- 📋 **Verify the image actually contains Chinese text**
- 🖼️ **Check if image is too small or low quality**
- 🎯 **Try cropping to focus on text area only**

### 4. 🐌 Very Slow Processing

**Symptoms:**
- OCR takes more than 2-3 minutes
- Browser becomes unresponsive

**Solutions:**
- 📏 **Reduce image file size** (aim for <2MB)
- ✂️ **Crop unnecessary background areas**
- 🖥️ **Close other browser tabs/applications**
- ⏱️ **Wait for initial language data download** (15MB first time)

## 🔧 Advanced Debugging Steps

### Step 1: Test Image Quality
1. Open the [Chinese OCR Debug Tool](debug_chinese_ocr.html)
2. Upload your image
3. Run full diagnostics
4. Compare results across different language settings

### Step 2: Image Preprocessing
```
✅ Good Image Characteristics:
- High resolution (>1200px width)
- Clear contrast (black text on white background)
- Straight/upright text (not rotated)
- Printed text (not handwritten)
- Minimal background noise

❌ Problematic Image Characteristics:
- Low resolution (<600px width)
- Poor contrast (gray text on gray background)
- Skewed/rotated text
- Handwritten or cursive text
- Lots of background elements/noise
```

### Step 3: Language Selection Strategy
1. **Start with `chi_sim`** (Simplified Chinese) for modern text
2. **Try `chi_tra`** (Traditional Chinese) if simplified fails
3. **Use `chi_sim+eng`** for mixed Chinese/English documents
4. **Test both** if uncertain about text type

### Step 4: Browser Console Debugging
1. Open browser Developer Tools (F12)
2. Check Console tab for debug messages
3. Look for Chinese OCR debug information
4. Check for error messages or warnings

## 📊 Performance Benchmarks

| Image Quality | Expected Confidence | Processing Time |
|---------------|-------------------|-----------------|
| High-res printed | 70-90% | 30-60 seconds |
| Medium-res printed | 50-70% | 45-90 seconds |
| Low-res printed | 20-50% | 60-120 seconds |
| Handwritten | 10-30% | 90-180 seconds |

## 🛠️ Tools Available

1. **[Main OCR App](index.html)** - Primary Chinese OCR interface
2. **[Debug Tool](debug_chinese_ocr.html)** - Advanced diagnostics
3. **[Test Image Generator](create_enhanced_chinese_tests.py)** - Create test images

## 💡 Best Practices

### For Students:
- 📸 Take photos in good lighting
- 📱 Use phone's document scanner mode
- 🔍 Ensure text fills most of the image
- 📐 Keep camera parallel to document

### For Teachers:
- 🖨️ Use high-quality document scans
- 📋 Test with sample images first
- 🔄 Keep backup of original documents
- 📊 Check confidence scores for quality assessment

## 🔗 Resources

- [Tesseract.js Documentation](https://tesseract.projectnaptha.com/)
- [Chinese Font Requirements](https://github.com/tesseract-ocr/tessdata)
- [Image Preprocessing Guide](https://github.com/tesseract-ocr/tesseract/wiki/ImproveQuality)

---

**Need more help?** Open the debug tool and run diagnostics on your specific image!
