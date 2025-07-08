import React, { useState } from 'react';
import { FileUploader } from './components/FileUpLoader';
import { ProgressBar } from './components/ProgressBar';
import { Language, AppState } from './types/ocr';
import './App.css';
import OCRResults from './components/OCRResults';

function App() {
  const [appState, setAppState] = useState<AppState>({
    selectedImage: null,
    selectedLanguage: 'chi_sim',
    isProcessing: false,
    progress: 0,
    progressMessage: 'Ready to process...',
    ocrResult: null,
    error: null
  });

  const handleFileSelect = (file: File) => {
    setAppState(prev => ({
      ...prev,
      selectedImage: file,
      error: null
    }));
    console.log('File selected:', file.name);
  };

  const handleLanguageChange = (language: Language) => {
    setAppState(prev => ({
      ...prev,
      selectedLanguage: language
    }));
    console.log('Language changed to:', language);
  };

  const startOCR = () => {
    if (!appState.selectedImage) {
      alert('Please select an image first!');
      return;
    }

    setAppState(prev => ({
      ...prev,
      isProcessing: true,
      progress: 0,
      progressMessage: 'Starting OCR...'
    }));

    // TODO: We'll implement actual OCR processing next!
    console.log('OCR would start here...');
  };

  return (
    <div className="App" style={{ 
      maxWidth: '800px', 
      margin: '0 auto', 
      padding: '20px' 
    }}>
      <header style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1>🔍 Chinese OCR App</h1>
        <p>Upload an image and extract Chinese text using Tesseract.js</p>
      </header>

      <FileUploader
        selectedLanguage={appState.selectedLanguage}
        onFileSelect={handleFileSelect}
        onLanguageChange={handleLanguageChange}
        isProcessing={appState.isProcessing}
      />

      <ProgressBar
        progress={appState.progress}
        message={appState.progressMessage}
        isVisible={appState.isProcessing}
      />

      <OCRResults 
        results={appState.ocrResult} 
        isProcessing={appState.isProcessing} 
      />

      {appState.selectedImage && (
        <div style={{ marginBottom: '20px' }}>
          <h3>Selected Image:</h3>
          <p>📄 {appState.selectedImage.name}</p>
          <p>📏 Size: {(appState.selectedImage.size / 1024 / 1024).toFixed(2)} MB</p>
          
          <button 
            onClick={startOCR}
            disabled={appState.isProcessing}
            style={{
              backgroundColor: '#4CAF50',
              color: 'white',
              padding: '10px 20px',
              border: 'none',
              borderRadius: '5px',
              cursor: appState.isProcessing ? 'not-allowed' : 'pointer',
              fontSize: '16px'
            }}
          >
            {appState.isProcessing ? '⏳ Processing...' : '🚀 Start OCR'}
          </button>
        </div>
      )}

      {appState.error && (
        <div style={{ 
          color: 'red', 
          backgroundColor: '#ffebee',
          padding: '10px',
          borderRadius: '5px',
          marginTop: '10px'
        }}>
          ❌ Error: {appState.error}
        </div>
      )}
    </div>
  );
}

export default App;