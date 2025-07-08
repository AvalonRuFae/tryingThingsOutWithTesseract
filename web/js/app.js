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
            const preprocessedImage = await this.preprocessImage(file);
            await this.processImageWithTesseract(preprocessedImage);
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

            // Initialize Tesseract with optimized settings
            this.currentWorker = await Tesseract.createWorker('eng', 1, {
                logger: (m) => {
                    console.log('Tesseract:', m);
                    if (m.status === 'loading tesseract core') {
                        this.updateProgress(10 + (m.progress * 10), 'Loading OCR engine...');
                    } else if (m.status === 'initializing tesseract') {
                        this.updateProgress(20 + (m.progress * 5), 'Initializing...');
                    } else if (m.status === 'loading language traineddata') {
                        this.updateProgress(25 + (m.progress * 5), 'Loading language data...');
                    } else if (m.status === 'initializing api') {
                        this.updateProgress(30, 'Starting OCR...');
                    } else if (m.status === 'recognizing text') {
                        const progress = 35 + (m.progress * 50); // 35-85%
                        this.updateProgress(progress, `Recognizing text... ${Math.round(m.progress * 100)}%`);
                    }
                }
            });

            this.currentWorker = worker; // Track the current worker

            // Optimize Tesseract parameters for better performance
            await this.currentWorker.setParameters({
                tessedit_pageseg_mode: Tesseract.PSM.AUTO_OSD,
                tessedit_char_whitelist: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?;:\'"()- ',
            });

            this.updateProgress(35, 'Processing image...');

            // Check if cancelled before starting recognition
            if (this.processingCancelled) return;

            // Process the image with timeout
            const recognizePromise = this.currentWorker.recognize(file);
            const timeoutPromise = new Promise((_, reject) => 
                setTimeout(() => reject(new Error('OCR timeout after 2 minutes')), 120000)
            );

            const { data } = await Promise.race([recognizePromise, timeoutPromise]);

            // Check if cancelled after recognition
            if (this.processingCancelled) return;

            this.updateProgress(85, 'Analyzing results...');

            // Process OCR results
            this.ocrResults = this.processOCRResults(data);
            
            this.updateProgress(95, 'Detecting typos...');

            // Detect typos
            const typos = this.typoDetector.detectTypos(this.ocrResults);
            
            this.updateProgress(100, 'Complete!');

            // Clean up
            await worker.terminate();

            // Show results
            setTimeout(() => {
                this.showResults(this.ocrResults, typos);
            }, 500);

        } catch (error) {
            console.error('Tesseract error:', error);
            throw error;
        }
    }

    processOCRResults(tesseractData) {
        // Convert Tesseract.js results to our format
        const words = tesseractData.words.map(word => ({
            text: word.text,
            confidence: word.confidence / 100, // Convert to 0-1 range
            bbox: {
                x0: word.bbox.x0,
                y0: word.bbox.y0,
                x1: word.bbox.x1,
                y1: word.bbox.y1,
                width: word.bbox.x1 - word.bbox.x0,
                height: word.bbox.y1 - word.bbox.y0
            }
        }));

        return {
            text: tesseractData.text,
            words: words,
            confidence: tesseractData.confidence / 100,
            word_count: words.length
        };
    }

    showResults(ocrResults, typos) {
        const processingTimeMs = Date.now() - this.startTime;
        const processingTimeS = (processingTimeMs / 1000).toFixed(1);

        // Hide processing, show results
        this.processingSection.style.display = 'none';
        this.resultsSection.style.display = 'block';

        // Update statistics
        this.wordCount.textContent = ocrResults.word_count;
        this.confidence.textContent = `${Math.round(ocrResults.confidence * 100)}%`;
        this.processingTime.textContent = `${processingTimeS}s`;

        // Show extracted text
        this.extractedText.textContent = ocrResults.text;

        // Show typo results
        this.displayTypoResults(typos);

        // Create annotated image
        this.createAnnotatedImage(ocrResults, typos);
    }

    displayTypoResults(typos) {
        const typoStats = this.typoDetector.getTypoStats(typos);
        
        if (typos.length === 0) {
            this.typoCount.textContent = 'No issues found';
            this.typoCount.style.background = '#d4edda';
            this.typoCount.style.color = '#155724';
            this.typoList.innerHTML = '<p style="text-align: center; color: #666; font-style: italic;">Great! No typos detected.</p>';
            return;
        }

        this.typoCount.textContent = `${typos.length} issue${typos.length > 1 ? 's' : ''} found`;
        
        // Create typo list
        this.typoList.innerHTML = typos.map(typo => `
            <div class="typo-item">
                <span class="typo-original">${typo.original}</span>
                <i class="fas fa-arrow-right typo-arrow"></i>
                <span class="typo-correction">${typo.correction}</span>
                <span class="typo-confidence">${typo.confidence}</span>
            </div>
        `).join('');
    }

    createAnnotatedImage(ocrResults, typos) {
        const canvas = this.annotatedCanvas;
        const ctx = canvas.getContext('2d');
        const img = this.originalImage;

        // Wait for image to load
        if (img.complete) {
            this.drawAnnotations(canvas, ctx, img, ocrResults, typos);
        } else {
            img.onload = () => {
                this.drawAnnotations(canvas, ctx, img, ocrResults, typos);
            };
        }
    }

    drawAnnotations(canvas, ctx, img, ocrResults, typos) {
        // Set canvas size to match image
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;

        // Draw the original image
        ctx.drawImage(img, 0, 0);

        // Create typo lookup for quick access
        const typoMap = new Map();
        typos.forEach(typo => {
            typoMap.set(typo.original, typo);
        });

        // Draw word bounding boxes and typo annotations
        ocrResults.words.forEach((word, index) => {
            const bbox = word.bbox;
            const isTypo = typoMap.has(word.text);

            if (isTypo) {
                const typo = typoMap.get(word.text);
                
                // Draw typo highlight
                ctx.strokeStyle = typo.confidence === 'high' ? '#dc3545' : '#ffc107';
                ctx.lineWidth = 3;
                ctx.strokeRect(bbox.x0, bbox.y0, bbox.width, bbox.height);

                // Draw correction text
                ctx.fillStyle = typo.confidence === 'high' ? '#dc3545' : '#ffc107';
                ctx.font = '16px Arial';
                ctx.fillText(
                    `→ ${typo.correction}`, 
                    bbox.x0, 
                    bbox.y0 - 5
                );
            } else {
                // Draw normal word boundary (subtle)
                ctx.strokeStyle = '#28a745';
                ctx.lineWidth = 1;
                ctx.globalAlpha = 0.3;
                ctx.strokeRect(bbox.x0, bbox.y0, bbox.width, bbox.height);
                ctx.globalAlpha = 1;
            }
        });

        // Add legend
        this.drawLegend(ctx, canvas.width, canvas.height);
    }

    drawLegend(ctx, canvasWidth, canvasHeight) {
        const legendX = canvasWidth - 200;
        const legendY = 20;

        // Legend background
        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        ctx.fillRect(legendX, legendY, 180, 80);
        ctx.strokeStyle = '#333';
        ctx.lineWidth = 1;
        ctx.strokeRect(legendX, legendY, 180, 80);

        // Legend text
        ctx.fillStyle = '#333';
        ctx.font = '14px Arial';
        ctx.fillText('Legend:', legendX + 10, legendY + 20);

        ctx.fillStyle = '#dc3545';
        ctx.fillText('● High confidence typos', legendX + 10, legendY + 40);

        ctx.fillStyle = '#ffc107';
        ctx.fillText('● Possible typos', legendX + 10, legendY + 55);

        ctx.fillStyle = '#28a745';
        ctx.fillText('● Correct words', legendX + 10, legendY + 70);
    }

    downloadResults() {
        const results = {
            timestamp: new Date().toISOString(),
            image_info: {
                name: this.currentImage.name,
                size: this.currentImage.size,
                type: this.currentImage.type
            },
            ocr_results: this.ocrResults,
            typos: this.typoDetector.detectTypos(this.ocrResults),
            processing_time: Date.now() - this.startTime
        };

        const blob = new Blob([JSON.stringify(results, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `composition-analysis-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    resetApp() {
        this.processingSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.imageInput.value = '';
        this.currentImage = null;
        this.ocrResults = null;
    }

    /**
     * Preprocess image for better OCR performance
     */
    async preprocessImage(file) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                // Limit image size for performance (max 1200px width)
                const maxWidth = 1200;
                const ratio = Math.min(maxWidth / img.width, maxWidth / img.height);
                
                if (ratio < 1) {
                    canvas.width = img.width * ratio;
                    canvas.height = img.height * ratio;
                } else {
                    canvas.width = img.width;
                    canvas.height = img.height;
                }
                
                // Draw and enhance image
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                
                // Convert to blob
                canvas.toBlob((blob) => {
                    resolve(blob);
                }, 'image/png', 0.9);
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
}

// Global functions for HTML onclick handlers
function resetApp() {
    app.resetApp();
}

function downloadResults() {
    app.downloadResults();
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CompositionCorrectorApp();
});
