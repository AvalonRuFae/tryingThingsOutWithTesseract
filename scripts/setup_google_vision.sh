#!/bin/bash
# Google Cloud Vision API Setup Script
# This script helps set up Google Cloud Vision API for the student composition corrector

echo "🚀 Google Cloud Vision API Setup for Student Composition Corrector"
echo "=================================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Google Cloud CLI
install_gcloud() {
    echo "📦 Installing Google Cloud CLI..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install google-cloud-sdk
        else
            echo "❌ Homebrew not found. Please install it first or download gcloud manually."
            echo "   Visit: https://cloud.google.com/sdk/docs/install"
            return 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
        curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
        sudo apt-get update && sudo apt-get install google-cloud-cli
    else
        echo "❌ Unsupported operating system. Please install gcloud manually."
        echo "   Visit: https://cloud.google.com/sdk/docs/install"
        return 1
    fi
}

# Function to create Google Cloud project
create_project() {
    echo "🏗️  Setting up Google Cloud project..."
    
    read -p "Enter your Google Cloud project ID (or press Enter to create new): " PROJECT_ID
    
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID="student-composition-$(date +%s)"
        echo "Creating new project: $PROJECT_ID"
        gcloud projects create $PROJECT_ID --name="Student Composition Corrector"
    fi
    
    gcloud config set project $PROJECT_ID
    echo "✅ Project set to: $PROJECT_ID"
}

# Function to enable APIs
enable_apis() {
    echo "🔧 Enabling required APIs..."
    
    gcloud services enable vision.googleapis.com
    gcloud services enable cloudbilling.googleapis.com
    
    echo "✅ APIs enabled successfully"
}

# Function to create service account
create_service_account() {
    echo "👤 Creating service account..."
    
    SERVICE_ACCOUNT_NAME="ocr-service-account"
    SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="OCR Service Account" \
        --description="Service account for student composition corrector OCR"
    
    # Grant necessary permissions
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="roles/vision.serviceAgent"
    
    echo "✅ Service account created: $SERVICE_ACCOUNT_EMAIL"
}

# Function to create and download credentials
create_credentials() {
    echo "🔑 Creating and downloading credentials..."
    
    CREDENTIALS_FILE="${HOME}/.config/gcloud/student-composition-credentials.json"
    mkdir -p "$(dirname "$CREDENTIALS_FILE")"
    
    gcloud iam service-accounts keys create "$CREDENTIALS_FILE" \
        --iam-account="${SERVICE_ACCOUNT_EMAIL}"
    
    echo "✅ Credentials saved to: $CREDENTIALS_FILE"
    
    # Set environment variable
    export GOOGLE_APPLICATION_CREDENTIALS="$CREDENTIALS_FILE"
    
    # Add to shell profile for persistence
    SHELL_PROFILE=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_PROFILE="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_PROFILE="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_PROFILE="$HOME/.bash_profile"
    fi
    
    if [ -n "$SHELL_PROFILE" ]; then
        echo "export GOOGLE_APPLICATION_CREDENTIALS=\"$CREDENTIALS_FILE\"" >> "$SHELL_PROFILE"
        echo "✅ Environment variable added to $SHELL_PROFILE"
    fi
}

# Function to install Python dependencies
install_python_deps() {
    echo "🐍 Installing Python dependencies..."
    
    pip install google-cloud-vision
    
    echo "✅ Python dependencies installed"
}

# Function to test the setup
test_setup() {
    echo "🧪 Testing Google Vision API setup..."
    
    python3 -c "
import os
from google.cloud import vision

try:
    client = vision.ImageAnnotatorClient()
    print('✅ Google Vision client created successfully!')
    print(f'✅ Credentials file: {os.environ.get(\"GOOGLE_APPLICATION_CREDENTIALS\", \"Not set\")}')
except Exception as e:
    print(f'❌ Setup test failed: {e}')
    exit(1)
"
}

# Main setup flow
main() {
    echo "Starting Google Cloud Vision API setup..."
    echo ""
    
    # Check if gcloud is installed
    if ! command_exists gcloud; then
        echo "📦 Google Cloud CLI not found. Installing..."
        install_gcloud || exit 1
    else
        echo "✅ Google Cloud CLI found"
    fi
    
    # Initialize gcloud if needed
    echo "🔐 Authenticating with Google Cloud..."
    gcloud auth login
    
    # Create or set project
    create_project
    
    # Enable APIs
    enable_apis
    
    # Create service account
    create_service_account
    
    # Create credentials
    create_credentials
    
    # Install Python dependencies
    install_python_deps
    
    # Test setup
    test_setup
    
    echo ""
    echo "🎉 Setup completed successfully!"
    echo "=================================================================="
    echo "📋 Next steps:"
    echo "1. Restart your terminal or run: source ~/.zshrc"
    echo "2. Test the OCR script: cd src/ocr && python google_vision_simple.py"
    echo "3. For production use: python google_vision_ocr.py"
    echo ""
    echo "💰 Cost information:"
    echo "• Free tier: 1,000 requests/month"
    echo "• Paid tier: $1.50 per 1,000 requests"
    echo ""
    echo "🔧 Project details:"
    echo "• Project ID: $PROJECT_ID"
    echo "• Service Account: $SERVICE_ACCOUNT_EMAIL"
    echo "• Credentials: $CREDENTIALS_FILE"
}

# Run main function
main
