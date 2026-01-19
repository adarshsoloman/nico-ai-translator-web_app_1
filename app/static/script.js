// NICO AI Translator - Frontend JavaScript

// ============================================================================
// DOM Elements
// ============================================================================

const inputText = document.getElementById('inputText');
const outputText = document.getElementById('outputText');
const sourceLang = document.getElementById('sourceLang');
const targetLang = document.getElementById('targetLang');
const swapBtn = document.getElementById('swapBtn');
const translateBtn = document.getElementById('translateBtn');
const clearBtn = document.getElementById('clearBtn');
const copyBtn = document.getElementById('copyBtn');
const inputCounter = document.getElementById('inputCounter');
const outputCounter = document.getElementById('outputCounter');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const metricsDisplay = document.getElementById('metricsDisplay');
const metricsText = document.getElementById('metricsText');
const toast = document.getElementById('toast');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = window.location.origin;
const LONG_TEXT_THRESHOLD = 1000; // Characters threshold for long translation

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
    updateCounters();
});

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    inputText.addEventListener('input', updateCounters);
    outputText.addEventListener('input', updateCounters);
    swapBtn.addEventListener('click', swapLanguages);
    translateBtn.addEventListener('click', handleTranslate);
    clearBtn.addEventListener('click', clearAll);
    copyBtn.addEventListener('click', copyOutput);

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter to translate
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            handleTranslate();
        }
        // Ctrl+K to clear
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            clearAll();
        }
    });
}

// ============================================================================
// Health Check
// ============================================================================

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        if (data.status === 'ready') {
            statusDot.classList.add('ready');
            statusText.textContent = 'Ready';
        } else {
            statusDot.classList.add('error');
            statusText.textContent = 'Not Ready';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        statusDot.classList.add('error');
        statusText.textContent = 'Error';
    }
}

// ============================================================================
// Word/Character Counting
// ============================================================================

function countWords(text) {
    if (!text.trim()) return 0;
    return text.trim().split(/\s+/).length;
}

function updateCounters() {
    // Input counter
    const inputValue = inputText.value;
    const inputWords = countWords(inputValue);
    const inputChars = inputValue.length;
    inputCounter.textContent = `${inputWords} words | ${inputChars} characters`;

    // Output counter
    const outputValue = outputText.value;
    const outputWords = countWords(outputValue);
    const outputChars = outputValue.length;
    outputCounter.textContent = `${outputWords} words | ${outputChars} characters`;

    // Show copy button if there's output
    if (outputValue.trim()) {
        copyBtn.style.display = 'inline-flex';
    } else {
        copyBtn.style.display = 'none';
    }
}

// ============================================================================
// Language Swap
// ============================================================================

function swapLanguages() {
    // Swap language selections
    const tempLang = sourceLang.value;
    sourceLang.value = targetLang.value;
    targetLang.value = tempLang;

    // Swap text content
    const tempText = inputText.value;
    inputText.value = outputText.value;
    outputText.value = tempText;

    updateCounters();
}

// ============================================================================
// Translation
// ============================================================================

async function handleTranslate() {
    const text = inputText.value.trim();

    // Validation
    if (!text) {
        showToast('Please enter some text to translate', 'error');
        return;
    }

    if (sourceLang.value === targetLang.value) {
        showToast('Source and target languages must be different', 'error');
        return;
    }

    // Determine if long translation
    const isLongText = text.length > LONG_TEXT_THRESHOLD;

    if (isLongText) {
        await translateLong(text);
    } else {
        await translateShort(text);
    }
}

// Short translation (regular API call)
async function translateShort(text) {
    try {
        // Disable button
        translateBtn.disabled = true;
        translateBtn.textContent = 'Translating...';

        // Hide metrics
        metricsDisplay.style.display = 'none';

        const response = await fetch(`${API_BASE_URL}/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                source_lang: sourceLang.value,
                target_lang: targetLang.value,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Translation failed');
        }

        const data = await response.json();

        // Update output
        outputText.value = data.translated_text;
        updateCounters();

        // Show metrics
        displayMetrics(data.metrics);

        showToast('Translation complete!', 'success');

    } catch (error) {
        console.error('Translation error:', error);
        showToast(error.message || 'Translation failed', 'error');
    } finally {
        translateBtn.disabled = false;
        translateBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 7.5H19M5 7.5L7 5.5M5 7.5L7 9.5"></path>
                <path d="M13 15.5L16 12.5L19 15.5"></path>
                <path d="M16 12.5V20"></path>
            </svg>
            Translate
        `;
    }
}

// Long translation (SSE streaming)
async function translateLong(text) {
    try {
        // Disable button
        translateBtn.disabled = true;
        translateBtn.textContent = 'Translating...';

        // Show progress bar
        progressContainer.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = 'Starting translation...';

        // Hide metrics
        metricsDisplay.style.display = 'none';

        // Clear output
        outputText.value = '';

        const response = await fetch(`${API_BASE_URL}/translate/long`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                source_lang: sourceLang.value,
                target_lang: targetLang.value,
            }),
        });

        if (!response.ok) {
            throw new Error('Translation failed');
        }

        // Process SSE stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));

                    if (data.status === 'chunking') {
                        progressText.textContent = data.message;
                    } else if (data.status === 'translating') {
                        progressFill.style.width = `${data.progress}%`;
                        progressText.textContent = `${data.message} (${data.progress}%)`;

                        // Append chunk result to output
                        if (data.chunk_result) {
                            outputText.value += (outputText.value ? ' ' : '') + data.chunk_result;
                            updateCounters();
                        }
                    }
                } else if (line.startsWith('event: complete')) {
                    // Next line will have the final data
                }
            }
        }

        // Hide progress bar
        setTimeout(() => {
            progressContainer.style.display = 'none';
        }, 1000);

        showToast('Translation complete!', 'success');

    } catch (error) {
        console.error('Long translation error:', error);
        showToast(error.message || 'Translation failed', 'error');
        progressContainer.style.display = 'none';
    } finally {
        translateBtn.disabled = false;
        translateBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M5 7.5H19M5 7.5L7 5.5M5 7.5L7 9.5"></path>
                <path d="M13 15.5L16 12.5L19 15.5"></path>
                <path d="M16 12.5V20"></path>
            </svg>
            Translate
        `;
    }
}

// ============================================================================
// Metrics Display
// ============================================================================

function displayMetrics(metrics) {
    const text = `Translation time: ${metrics.total_time_ms}ms | ` +
        `Tokens: ${metrics.input_tokens} → ${metrics.output_tokens} | ` +
        `Speed: ${metrics.tokens_per_second.toFixed(1)} tokens/s`;

    metricsText.textContent = text;
    metricsDisplay.style.display = 'block';
}

// ============================================================================
// Clear All
// ============================================================================

function clearAll() {
    inputText.value = '';
    outputText.value = '';
    updateCounters();
    metricsDisplay.style.display = 'none';
    progressContainer.style.display = 'none';
    showToast('Cleared!', 'success');
}

// ============================================================================
// Copy to Clipboard
// ============================================================================

async function copyOutput() {
    const text = outputText.value;

    if (!text) {
        showToast('Nothing to copy', 'error');
        return;
    }

    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!', 'success');
    } catch (error) {
        console.error('Copy failed:', error);
        showToast('Failed to copy', 'error');
    }
}

// ============================================================================
// Toast Notifications
// ============================================================================

function showToast(message, type = 'info') {
    toast.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
