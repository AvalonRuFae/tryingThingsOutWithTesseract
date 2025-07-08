# Google Cloud Vision API Setup Guide

## 📋 Prerequisites

1. **Google Cloud Account** - Create one at [cloud.google.com](https://cloud.google.com)
2. **Python environment** with required packages installed

## 🛠️ Step-by-Step Setup

### 1. Install Dependencies
```bash
pip install google-cloud-vision
```

### 2. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "New Project" 
3. Enter project name: `student-composition-corrector`
4. Click "Create"

### 3. Enable Vision API
1. Go to **APIs & Services** → **Library**
2. Search for "Cloud Vision API"
3. Click on it and press **"Enable"**

### 4. Create Service Account
1. Go to **IAM & Admin** → **Service Accounts**
2. Click **"Create Service Account"**
3. Enter name: `ocr-service-account`
4. Click **"Create and Continue"**
5. Select role: **"Cloud Vision AI Service Agent"**
6. Click **"Done"**

### 5. Generate Credentials
1. Click on your service account
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Select **"JSON"** format
5. Click **"Create"**
6. Save the downloaded JSON file securely

### 6. Set Environment Variable
```bash
# Replace with your actual path
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"

# For permanent setup, add to your shell profile:
echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"' >> ~/.zshrc
source ~/.zshrc
```

### 7. Test the Setup
```bash
cd src/ocr
python google_vision_ocr.py
```

## 💰 Pricing Information

- **Free Tier**: 1,000 requests per month
- **Paid Tier**: $1.50 per 1,000 requests
- **Text Detection**: Counts as 1 request per image

## 🔧 Alternative Setup (For Testing)

If you want to test without setting up Google Cloud, you can:

1. **Use the existing Tesseract results** as a baseline
2. **Mock the Google Vision API** for development
3. **Use other free OCR APIs** like OCR.space

## 🚨 Security Notes

- **Never commit** credentials JSON to version control
- **Use environment variables** for credentials
- **Restrict API key permissions** to Vision API only
- **Monitor usage** to avoid unexpected charges

## 📞 Support

If you encounter issues:
1. Check the [Google Cloud Vision documentation](https://cloud.google.com/vision/docs)
2. Verify your credentials are correctly configured
3. Ensure the Vision API is enabled for your project
4. Check billing is set up (required even for free tier)
