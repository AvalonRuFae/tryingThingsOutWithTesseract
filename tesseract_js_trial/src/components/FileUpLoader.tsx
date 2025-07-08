import React, { useState } from 'react';
import { Language } from '../types/ocr';

interface FileUploaderProps {
  selectedLanguage: Language;
  onFileSelect: (file: File) => void;
  onLanguageChange: (language: Language) => void;
  isProcessing: boolean;
}

export const FileUploader: React.FC<FileUploaderProps> = ({
  selectedLanguage,
  onFileSelect,
  onLanguageChange,
  isProcessing
}) => {
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileSelect(file);
      
      // Create image preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleLanguageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    onLanguageChange(event.target.value as Language);
  };

  return (
    <div style={{ 
      border: '2px dashed #ccc', 
      padding: '20px', 
      borderRadius: '8px',
      textAlign: 'center',
      marginBottom: '20px'
    }}>
      <h3>📁 Upload Image for OCR</h3>
      
      <div style={{ marginBottom: '15px' }}>
        <label htmlFor="language-select" style={{ marginRight: '10px' }}>
          🌐 OCR Language:
        </label>
        <select 
          id="language-select"
          value={selectedLanguage} 
          onChange={handleLanguageChange}
          disabled={isProcessing}
          style={{ padding: '5px 10px' }}
        >
          <option value="eng">English</option>
          <option value="chi_sim">Chinese Simplified</option>
          <option value="chi_tra">Chinese Traditional</option>
          <option value="jpn">Japanese</option>
          <option value="kor">Korean</option>
        </select>
      </div>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={isProcessing}
        style={{ marginBottom: '15px' }}
      />
      
      {imagePreview && (
        <div style={{ marginTop: '15px' }}>
          <h4>📷 Image Preview:</h4>
          <img 
            src={imagePreview} 
            alt="Selected image preview" 
            style={{ 
              maxWidth: '100%', 
              maxHeight: '300px',
              border: '1px solid #ddd',
              borderRadius: '5px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }} 
          />
        </div>
      )}
      
      <p style={{ fontSize: '14px', color: '#666', margin: '10px 0' }}>
        💡 Tip: Use clear, high-contrast images for best results
      </p>
    </div>
  );
};

export {};