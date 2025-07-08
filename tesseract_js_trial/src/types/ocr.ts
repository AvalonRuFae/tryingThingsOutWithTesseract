// OCR Language options
export type Language = 'eng' | 'chi_sim' | 'chi_tra' | 'jpn' | 'kor';

// OCR Results from Tesseract
export interface OCRResult {
  text: string;
  confidence: number;
  words: OCRWord[];
}

export interface OCRWord {
  text: string;
  confidence: number;
  bbox: {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
  };
}

// App State
export interface AppState {
  selectedImage: File | null;
  selectedLanguage: Language;
  isProcessing: boolean;
  progress: number;
  progressMessage: string;
  ocrResult: OCRResult | null;
  error: string | null;
}

// Ensure this file is treated as a module
export {};