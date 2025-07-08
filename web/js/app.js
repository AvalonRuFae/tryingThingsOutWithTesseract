/**
 * Student Composition Corrector - Web Application
 * Main application logic using Tesseract.js
 */

class CompositionCorrectorApp {
    constructor() {
        this.typoDetector = new TypoDetector();
        this.currentImage = null;
        this.ocrResults = null;
        this.startTime = null;
        this.currentWorker = null; // Track current Tesseract worker
        this.processingCancelled = false; // Track if user cancelled
        
        this.initializeElements();
        this.setupEventListeners();
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.imageInput = document.getElementById('imageInput');
        this.languageSelect = document.getElementById('languageSelect');
        this.processingSection = document.getElementById('processingSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        
        // Result elements
        this.originalImage = document.getElementById('originalImage');
        this.wordCount = document.getElementById('wordCount');
        this.confidence = document.getElementById('confidence');
        this.processingTime = document.getElementById('processingTime');
        this.extractedText = document.getElementById('extractedText');
        this.typoCount = document.getElementById('typoCount');
        this.typoList = document.getElementById('typoList');
        this.annotatedCanvas = document.getElementById('annotatedCanvas');
    }

    setupEventListeners() {
        // File input change
        this.imageInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleImageUpload(e.target.files[0]);
            }
        });

        // Upload area click
        this.uploadArea.addEventListener('click', () => {
            this.imageInput.click();
        });

        // Language selection change
        this.languageSelect.addEventListener('change', () => {
            this.updateLanguageTips();
        });

        // Initialize language tips
        this.updateLanguageTips();

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                this.handleImageUpload(e.dataTransfer.files[0]);
            }
        });
    }

    async handleImageUpload(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload a valid image file.');
            return;
        }

        this.currentImage = file;
        this.showProcessingSection();
        
        try {
            // Preprocess image for better OCR performance
            this.updateProgress(5, 'Optimizing image...');
            const preprocessedImage = await this.preprocessImage(file);
            await this.processImageWithTesseract(preprocessedImage || file);
        } catch (error) {
            console.error('Error processing image:', error);
            
            if (error.message.includes('timeout')) {
                alert('OCR processing timed out. Try with a smaller or clearer image.');
            } else {
                alert(`Error processing image: ${error.message}. Please try again.`);
            }
            
            this.resetApp();
        }
    }

    showProcessingSection() {
        this.processingSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.progressFill.style.width = '0%';
        this.progressText.textContent = 'Initializing OCR...';
        this.startTime = Date.now();
        this.processingCancelled = false; // Reset cancellation flag
    }

    updateProgress(progress, message) {
        this.progressFill.style.width = `${progress}%`;
        this.progressText.textContent = message;
    }

    async processImageWithTesseract(file) {
        try {
            // Check file size (limit to 5MB for performance)
            if (file.size > 5 * 1024 * 1024) {
                if (!confirm('Large image detected. This may take a long time to process. Continue?')) {
                    this.resetApp();
                    return;
                }
            }

            // Create image URL for preview
            const imageUrl = URL.createObjectURL(file);
            this.originalImage.src = imageUrl;

            this.updateProgress(10, 'Loading Tesseract.js...');

            // Get selected language
            const selectedLanguage = this.languageSelect.value;
            this.updateProgress(15, `Loading ${this.getLanguageName(selectedLanguage)} language data...`);

            // Initialize Tesseract with selected language
            this.currentWorker = await Tesseract.createWorker(selectedLanguage, 1, {
                logger: (m) => {
                    console.log('Tesseract:', m);
                    if (m.status === 'loading tesseract core') {
                        this.updateProgress(10 + (m.progress * 10), 'Loading OCR engine...');
                    } else if (m.status === 'initializing tesseract') {
                        this.updateProgress(20 + (m.progress * 5), 'Initializing...');
                    } else if (m.status === 'loading language traineddata') {
                        this.updateProgress(25 + (m.progress * 5), `Loading ${this.getLanguageName(selectedLanguage)} data...`);
                    } else if (m.status === 'initializing api') {
                        this.updateProgress(30, 'Starting OCR...');
                    } else if (m.status === 'recognizing text') {
                        const progress = 35 + (m.progress * 50); // 35-85%
                        this.updateProgress(progress, `Recognizing ${this.getLanguageName(selectedLanguage)} text... ${Math.round(m.progress * 100)}%`);
                    }
                }
            });

            // Optimize Tesseract parameters for selected language
            const whitelist = this.getCharacterWhitelist(selectedLanguage);
            const params = {};
            
            // Language-specific page segmentation modes
            if (selectedLanguage.startsWith('chi_') || selectedLanguage === 'jpn' || selectedLanguage === 'kor') {
                // For CJK languages, use different segmentation
                params.tessedit_pageseg_mode = Tesseract.PSM.SINGLE_BLOCK;
                params.tessedit_ocr_engine_mode = Tesseract.OEM.LSTM_ONLY; // Use LSTM for better CJK
            } else {
                params.tessedit_pageseg_mode = Tesseract.PSM.AUTO_OSD;
                params.tessedit_ocr_engine_mode = Tesseract.OEM.DEFAULT;
            }
            
            // Only add whitelist for languages that benefit from it
            if (whitelist) {
                params.tessedit_char_whitelist = whitelist;
            }
            
            await this.currentWorker.setParameters(params);

            this.updateProgress(35, 'Processing image...');

            // Use enhanced preprocessing for Chinese languages
            let processedImage = file;
            if (selectedLanguage.startsWith('chi_') || selectedLanguage === 'jpn' || selectedLanguage === 'kor') {
                this.updateProgress(37, 'Preprocessing for CJK languages...');
                processedImage = await this.preprocessImageForChinese(file);
            }

            // Check if cancelled before starting recognition
            if (this.processingCancelled) return;

            // Process the image with timeout
            const recognizePromise = this.currentWorker.recognize(processedImage);
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('OCR timeout after 2 minutes')), 120000)
            );

            const { data } = await Promise.race([recognizePromise, timeoutPromise]);

            // Check if cancelled after recognition
            if (this.processingCancelled) return;

            this.updateProgress(85, 'Analyzing results...');

            // Process OCR results
            this.ocrResults = this.processOCRResults(data);
            
            // Enhanced debug output for Chinese
            if (selectedLanguage.startsWith('chi_')) {
                const chineseChars = (this.ocrResults.text.match(/[\u4e00-\u9fff]/g) || []).length;
                const hasGibberish = /[^a-zA-Z0-9\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]/g.test(this.ocrResults.text);
                const debugInfo = {
                    language: selectedLanguage,
                    totalWords: this.ocrResults.words.length,
                    confidence: this.ocrResults.confidence,
                    chineseCharCount: chineseChars,
                    hasGibberish: hasGibberish,
                    textLength: this.ocrResults.text.length,
                    sampleText: this.ocrResults.text.substring(0, 100),
                    firstFewWords: this.ocrResults.words.slice(0, 5).map(w => ({ text: w.text, conf: w.confidence })),
                    characterAnalysis: this.ocrResults.text.split('').slice(0, 10).map(char => 
                        `'${char}' (U+${char.charCodeAt(0).toString(16).toUpperCase()})`
                    )
                };
                
                console.log('Chinese OCR Debug:', debugInfo);
                
                // Show warning if results look problematic
                if (this.ocrResults.confidence < 30 || chineseChars === 0 || hasGibberish) {
                    console.warn('⚠️ Chinese OCR Issues Detected:');
                    if (this.ocrResults.confidence < 30) console.warn('- Low confidence (<30%)');
                    if (chineseChars === 0) console.warn('- No Chinese characters detected');
                    if (hasGibberish) console.warn('- Possible gibberish characters detected');
                    
                    // Auto-retry with different language if results are very poor
                    if (this.ocrResults.confidence < 20 && selectedLanguage === 'chi_sim') {
                        console.log('🔄 Auto-retrying with Traditional Chinese...');
                        this.updateProgress(50, 'Retrying with Traditional Chinese...');
                        return this.retryWithTraditionalChinese(file);
                    }
                }
            }
            
            this.updateProgress(95, 'Detecting typos...');

            // Detect typos
            const typos = this.typoDetector.detectTypos(this.ocrResults);
            
            this.updateProgress(100, 'Complete!');

            // Clean up
            if (this.currentWorker) {
                await this.currentWorker.terminate();
                this.currentWorker = null;
            }

            // Show results
            setTimeout(() => {
                this.showResults(this.ocrResults, typos);
            }, 500);

        } catch (error) {
            console.error('Tesseract error:', error);
            
            // Clean up worker on error
            if (this.currentWorker) {
                await this.currentWorker.terminate();
                this.currentWorker = null;
            }
            
            throw error;
        }
    }

    async retryWithTraditionalChinese(file) {
        try {
            // Clean up current worker
            if (this.currentWorker) {
                await this.currentWorker.terminate();
                this.currentWorker = null;
            }

            this.updateProgress(55, 'Loading Traditional Chinese data...');

            // Initialize with Traditional Chinese
            this.currentWorker = await Tesseract.createWorker('chi_tra', 1, {
                logger: (m) => {
                    console.log('Tesseract (chi_tra retry):', m);
                    if (m.status === 'recognizing text') {
                        const progress = 60 + (m.progress * 25); // 60-85%
                        this.updateProgress(progress, `Retrying with Traditional Chinese... ${Math.round(m.progress * 100)}%`);
                    }
                }
            });

            // Set parameters for Traditional Chinese
            await this.currentWorker.setParameters({
                tessedit_pageseg_mode: Tesseract.PSM.SINGLE_BLOCK,
                tessedit_ocr_engine_mode: Tesseract.OEM.LSTM_ONLY,
                preserve_interword_spaces: '1'
            });

            // Process with enhanced preprocessing
            const preprocessedImage = await this.preprocessImageForChinese(file, true);
            const { data } = await this.currentWorker.recognize(preprocessedImage);

            // Process results
            const retryResults = this.processOCRResults(data);
            
            console.log('Traditional Chinese retry results:', {
                originalConfidence: this.ocrResults.confidence,
                retryConfidence: retryResults.confidence,
                originalChineseChars: (this.ocrResults.text.match(/[\u4e00-\u9fff]/g) || []).length,
                retryChineseChars: (retryResults.text.match(/[\u4e00-\u9fff]/g) || []).length
            });

            // Use retry results if they're better
            if (retryResults.confidence > this.ocrResults.confidence + 10) {
                console.log('✅ Traditional Chinese retry produced better results');
                this.ocrResults = retryResults;
            } else {
                console.log('📊 Keeping original Simplified Chinese results');
            }

            return this.ocrResults;
        } catch (error) {
            console.error('Traditional Chinese retry failed:', error);
            return this.ocrResults; // Keep original results
        }
    }

    async preprocessImageForChinese(file, enhanced = false) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                // Higher scaling for enhanced mode
                const scale = enhanced ? 3 : 2;
                canvas.width = img.width * scale;
                canvas.height = img.height * scale;
                
                // Disable smoothing for crisp text
                ctx.imageSmoothingEnabled = false;
                
                // Draw scaled image
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                
                if (enhanced) {
                    // Apply advanced preprocessing for difficult cases
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const data = imageData.data;
                    
                    // Convert to grayscale and enhance contrast
                    for (let i = 0; i < data.length; i += 4) {
                        // Calculate luminance
                        const r = data[i];
                        const g = data[i + 1];
                        const b = data[i + 2];
                        let gray = 0.299 * r + 0.587 * g + 0.114 * b;
                        
                        // Apply sigmoid contrast enhancement
                        gray = 255 / (1 + Math.exp(-0.1 * (gray - 128)));
                        
                        // Apply threshold for better text separation
                        gray = gray > 140 ? 255 : gray < 100 ? 0 : gray;
                        
                        data[i] = gray;     // Red
                        data[i + 1] = gray; // Green
                        data[i + 2] = gray; // Blue
                    }
                    
                    ctx.putImageData(imageData, 0, 0);
                }
                
                canvas.toBlob((blob) => {
                    resolve(blob);
                }, 'image/png', 1.0);
            };
            
            img.src = URL.createObjectURL(file);
        });
    }

    async preprocessImage(file) {
        return new Promise((resolve, reject) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                try {
                    // Get selected language for preprocessing
                    const selectedLanguage = this.languageSelect.value;
                    const isCJK = selectedLanguage.startsWith('chi_') || selectedLanguage === 'jpn' || selectedLanguage === 'kor';
                    
                    // For CJK languages, use higher resolution (less aggressive resizing)
                    const maxWidth = isCJK ? 1800 : 1200;
                    const ratio = Math.min(maxWidth / img.width, maxWidth / img.height);
                    
                    if (ratio < 1) {
                        canvas.width = img.width * ratio;
                        canvas.height = img.height * ratio;
                    } else {
                        canvas.width = img.width;
                        canvas.height = img.height;
                    }
                    
                    // Draw image
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    
                    // Apply image enhancement for CJK text
                    if (isCJK) {
                        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                        const data = imageData.data;
                        
                        // Increase contrast for better Chinese character recognition
                        for (let i = 0; i < data.length; i += 4) {
                            const brightness = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
                            const factor = 1.2; // Increase contrast
                            
                            data[i] = Math.min(255, Math.max(0, factor * (data[i] - brightness) + brightness));
                            data[i + 1] = Math.min(255, Math.max(0, factor * (data[i + 1] - brightness) + brightness));
                            data[i + 2] = Math.min(255, Math.max(0, factor * (data[i + 2] - brightness) + brightness));
                        }
                        
                        ctx.putImageData(imageData, 0, 0);
                    }
                    
                    // Convert to blob with higher quality for CJK
                    const quality = isCJK ? 0.95 : 0.9;
                    canvas.toBlob((blob) => {
                        if (blob) {
                            resolve(blob);
                        } else {
                            resolve(file); // Fallback to original file
                        }
                    }, 'image/png', quality);
                } catch (error) {
                    console.warn('Preprocessing failed, using original image:', error);
                    resolve(file); // Fallback to original file
                }
            };
            
            img.onerror = () => {
                console.warn('Failed to load image for preprocessing, using original');
                resolve(file); // Fallback to original file
            };
            
            img.src = URL.createObjectURL(file);
        });
    }

    cancelProcessing() {
        this.processingCancelled = true;
        if (this.currentWorker) {
            this.currentWorker.terminate();
            this.currentWorker = null;
        }
        this.resetApp();
    }

    /**
     * Get human-readable language name
     */
    getLanguageName(langCode) {
        const languages = {
            'eng': 'English',
            'chi_sim': 'Chinese Simplified',
            'chi_tra': 'Chinese Traditional', 
            'jpn': 'Japanese',
            'kor': 'Korean',
            'spa': 'Spanish',
            'fra': 'French',
            'deu': 'German'
        };
        return languages[langCode] || langCode;
    }

    /**
     * Get character whitelist for language
     */
    getCharacterWhitelist(langCode) {
        const whitelists = {
            'eng': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?;:\'"()- ',
            'chi_sim': '', // No whitelist for Chinese - let Tesseract handle all characters
            'chi_tra': '', // No whitelist for Chinese - let Tesseract handle all characters
            'jpn': '', // No whitelist for Japanese - let Tesseract handle all characters
            'kor': '', // No whitelist for Korean - let Tesseract handle all characters
            'spa': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóúüñÁÉÍÓÚÜÑ0123456789.,!?;:\'"()- ',
            'fra': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzàâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ0123456789.,!?;:\'"()- ',
            'deu': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzäöüßÄÖÜ0123456789.,!?;:\'"()- '
        };
        return whitelists[langCode] || '';
    }

    updateLanguageTips() {
        const chineseTips = document.getElementById('chineseTips');
        const selectedLanguage = this.languageSelect.value;
        
        if (selectedLanguage.startsWith('chi_')) {
            chineseTips.style.display = 'block';
        } else {
            chineseTips.style.display = 'none';
        }
    }
}

// Global functions for HTML onclick handlers
function resetApp() {
    app.resetApp();
}

function downloadResults() {
    app.downloadResults();
}

function cancelProcessing() {
    app.cancelProcessing();
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CompositionCorrectorApp();
});
