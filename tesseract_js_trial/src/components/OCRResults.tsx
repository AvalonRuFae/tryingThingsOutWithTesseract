import React from 'react';
import { OCRResult, OCRWord } from '../types/ocr';

interface OCRResultsProps {
    results: OCRResult | null;
    isProcessing: boolean;
}

const OCRResults: React.FC<OCRResultsProps> = ({ results, isProcessing }) => {
    //component logic will go here

    return(
        <div className = "ocr-results">
            {isProcessing && (
                <div className="loading">
                    <p>🔍 Processing OCR...</p>
                    <p>This may take a few moments.</p>
                </div>
            )}

            {!isProcessing && !results &&(
                <div className="no-results">
                    <p>📷 Upload an image and click "Start OCR" to begin.</p>
                </div>
            )}

            {!isProcessing && results &&(
                <div className="results-content">
                    <h3>📝 Extracted Text:</h3>
                    <div className="extracted-text">
                        {results.text}
                    </div>
                    <h4>📊 Confidence: {results.confidence.toFixed(1)}%</h4>  
                    <p>🔤 Words found: {results.words.length}</p>
                </div>
            )}
        </div>
    )
}

export default OCRResults;