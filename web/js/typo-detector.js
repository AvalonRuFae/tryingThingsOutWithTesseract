/**
 * Typo Detection Module - JavaScript version
 * Based on the Python typo detector
 */

class TypoDetector {
    constructor() {
        // Common typos and their corrections (same as Python version)
        this.typoCorrections = {
            'sumer': 'summer',
            'familly': 'family', 
            'wich': 'which',
            'whether': 'weather',
            'beutiful': 'beautiful',
            'enjoied': 'enjoyed',
            'swiming': 'swimming',
            'favrite': 'favorite',
            'bulding': 'building',
            'resturant': 'restaurant',
            'delisious': 'delicious',
            'cant': "can't",
            'wont': "won't",
            'dont': "don't",
            'teh': 'the',
            'recieve': 'receive',
            'seperate': 'separate',
            'occured': 'occurred',
            'begining': 'beginning',
            'accomodate': 'accommodate'
        };

        // Common Chinese typos (Simplified Chinese examples)
        this.chineseTypoCorrections = {
            '的': '地', // Common de/di confusion
            '在': '再', // Common zai confusion  
            '他': '她', // Gender confusion
            '那': '哪', // na/nei confusion
            '做': '作', // zuo confusion
            '像': '象', // xiang confusion
            '以': '已', // yi confusion
            '练': '炼', // lian confusion
        };

        // Basic English word list (simplified)
        this.commonWords = new Set([
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'under', 'over',
            'a', 'an', 'is', 'was', 'are', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'cannot', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their',
            'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'just', 'now', 'here', 'there', 'when', 'where', 'why', 'how',
            'what', 'which', 'who', 'whom', 'whose', 'if', 'because', 'as', 'until',
            'while', 'although', 'though', 'since', 'unless', 'whether', 'wherever'
        ]);
    }

    /**
     * Clean word for comparison
     */
    cleanWord(word) {
        return word.toLowerCase().replace(/[^\w]/g, '');
    }

    /**
     * Detect typos in OCR results
     */
    detectTypos(ocrResults) {
        const typos = [];

        if (!ocrResults.words || !Array.isArray(ocrResults.words)) {
            return typos;
        }

        for (const wordData of ocrResults.words) {
            const originalWord = wordData.text;
            const cleanedWord = this.cleanWord(originalWord);
            
            if (cleanedWord.length < 2) continue; // Skip very short words

            let correction = null;
            let confidence = 'low';

            // Check for exact matches in typo dictionary
            if (this.typoCorrections[cleanedWord]) {
                correction = this.typoCorrections[cleanedWord];
                confidence = 'high';
            }
            // Check for partial matches (typos with punctuation)
            else {
                for (const [typo, fix] of Object.entries(this.typoCorrections)) {
                    if (cleanedWord.includes(typo) || originalWord.toLowerCase().includes(typo)) {
                        correction = fix;
                        confidence = 'high';
                        break;
                    }
                }
            }

            // Check against common words for medium confidence issues
            if (!correction && !this.commonWords.has(cleanedWord)) {
                // Simple heuristics for potential issues
                if (cleanedWord.length > 4) {
                    // Check for common patterns that might be OCR errors
                    const suspiciousPatterns = /[|]{1,}|[1l]{2,}|[0o]{2,}/i;
                    if (suspiciousPatterns.test(originalWord)) {
                        confidence = 'medium';
                        // Try to suggest a simple correction
                        let suggested = originalWord.replace(/[|]/g, 'l')
                                                  .replace(/1/g, 'l')
                                                  .replace(/0/g, 'o');
                        if (suggested !== originalWord) {
                            correction = suggested.toLowerCase();
                        }
                    }
                }
            }

            if (correction) {
                typos.push({
                    original: originalWord,
                    correction: correction,
                    confidence: confidence,
                    bbox: wordData.bbox,
                    position: {
                        x: wordData.bbox ? wordData.bbox.x0 : 0,
                        y: wordData.bbox ? wordData.bbox.y0 : 0
                    }
                });
            }
        }

        return typos;
    }

    /**
     * Get typo statistics
     */
    getTypoStats(typos) {
        const stats = {
            total: typos.length,
            high_confidence: typos.filter(t => t.confidence === 'high').length,
            medium_confidence: typos.filter(t => t.confidence === 'medium').length,
            low_confidence: typos.filter(t => t.confidence === 'low').length
        };

        return stats;
    }

    /**
     * Format typos for display
     */
    formatTyposForDisplay(typos) {
        return typos.map(typo => ({
            ...typo,
            displayClass: `typo-${typo.confidence}`,
            icon: typo.confidence === 'high' ? '❌' : 
                  typo.confidence === 'medium' ? '⚠️' : '💭'
        }));
    }
}

// Export for use in main app
window.TypoDetector = TypoDetector;
