# Auto-Translate Streaming Feature Implementation Guide

This guide will help you add **real-time auto-translate** functionality to the NICO AI Translator, similar to Google Translate's streaming behavior.

---

## 📋 Overview

**Goal**: Automatically translate text as the user types, with a short delay to avoid excessive API calls.

**User Experience**:
- User types in the input box
- After 800ms of no typing, translation starts automatically
- Output updates smoothly without clicking "Translate"
- Optional toggle to enable/disable auto-translate

---

## 🎯 Implementation Steps

### Step 1: Update Frontend JavaScript (`app/static/script.js`)

#### 1.1 Add Auto-Translate State Variables

Add these variables at the top of your script (after existing variable declarations):

```javascript
// Auto-translate feature
let autoTranslateEnabled = false;
let autoTranslateTimer = null;
let currentAbortController = null;
const AUTO_TRANSLATE_DELAY = 800; // milliseconds
const AUTO_TRANSLATE_MIN_LENGTH = 2; // minimum characters to trigger
```

#### 1.2 Add Auto-Translate Toggle UI

Add this HTML to your `app/static/index.html` (place it near the language selectors or settings area):

```html
<div class="auto-translate-toggle">
    <label class="toggle-switch">
        <input type="checkbox" id="autoTranslateToggle">
        <span class="toggle-slider"></span>
    </label>
    <label for="autoTranslateToggle">Auto-translate as I type</label>
</div>
```

#### 1.3 Add CSS Styles for Toggle

Add to `app/static/style.css`:

```css
/* Auto-translate toggle */
.auto-translate-toggle {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 10px 0;
}

.toggle-switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 24px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: 0.3s;
    border-radius: 24px;
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: 0.3s;
    border-radius: 50%;
}

input:checked + .toggle-slider {
    background-color: #4CAF50;
}

input:checked + .toggle-slider:before {
    transform: translateX(26px);
}
```

#### 1.4 Add Auto-Translate Logic

Add this function in `script.js`:

```javascript
// Auto-translate function
function setupAutoTranslate() {
    const toggle = document.getElementById('autoTranslateToggle');
    const inputTextarea = document.getElementById('inputText');
    
    // Toggle event listener
    toggle.addEventListener('change', (e) => {
        autoTranslateEnabled = e.target.checked;
        console.log('Auto-translate:', autoTranslateEnabled ? 'enabled' : 'disabled');
        
        // Clear any pending translation when toggled off
        if (!autoTranslateEnabled && autoTranslateTimer) {
            clearTimeout(autoTranslateTimer);
            autoTranslateTimer = null;
        }
    });
    
    // Input event listener for auto-translate
    inputTextarea.addEventListener('input', () => {
        if (!autoTranslateEnabled) return;
        
        // Clear existing timer
        if (autoTranslateTimer) {
            clearTimeout(autoTranslateTimer);
        }
        
        // Cancel any in-flight request
        if (currentAbortController) {
            currentAbortController.abort();
            currentAbortController = null;
        }
        
        const text = inputTextarea.value.trim();
        
        // Only auto-translate if text meets minimum length
        if (text.length >= AUTO_TRANSLATE_MIN_LENGTH) {
            // Set new timer
            autoTranslateTimer = setTimeout(() => {
                triggerAutoTranslate();
            }, AUTO_TRANSLATE_DELAY);
        } else {
            // Clear output if text is too short
            document.getElementById('outputText').value = '';
        }
    });
}

// Trigger auto-translate
async function triggerAutoTranslate() {
    const inputText = document.getElementById('inputText').value.trim();
    
    if (!inputText) return;
    
    // Create abort controller for this request
    currentAbortController = new AbortController();
    
    try {
        // Show subtle loading indicator (optional)
        showAutoTranslateLoading();
        
        // Call your existing translate function
        await translateText(currentAbortController.signal);
        
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Translation cancelled (user still typing)');
        } else {
            console.error('Auto-translate error:', error);
        }
    } finally {
        hideAutoTranslateLoading();
        currentAbortController = null;
    }
}

// Optional: Visual feedback functions
function showAutoTranslateLoading() {
    const outputTextarea = document.getElementById('outputText');
    outputTextarea.style.opacity = '0.6';
    // You can add a spinner or "translating..." text here
}

function hideAutoTranslateLoading() {
    const outputTextarea = document.getElementById('outputText');
    outputTextarea.style.opacity = '1';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupAutoTranslate();
    // ... your other initialization code
});
```

#### 1.5 Update Existing `translateText()` Function

Modify your existing `translateText()` function to accept an optional abort signal:

```javascript
async function translateText(abortSignal = null) {
    const inputText = document.getElementById('inputText').value.trim();
    const sourceLang = document.getElementById('sourceLang').value;
    const targetLang = document.getElementById('targetLang').value;
    
    if (!inputText) {
        alert('Please enter text to translate');
        return;
    }
    
    // ... existing validation code ...
    
    try {
        const response = await fetch('/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: inputText,
                source_lang: sourceLang,
                target_lang: targetLang
            }),
            signal: abortSignal // Add abort signal support
        });
        
        // ... rest of your existing code ...
        
    } catch (error) {
        if (error.name === 'AbortError') {
            throw error; // Re-throw abort errors
        }
        // ... existing error handling ...
    }
}
```

---

## 🎨 Optional Enhancements

### Enhancement 1: Character Counter with Auto-Translate Indicator

Add a visual indicator showing when auto-translate will trigger:

```html
<div class="input-info">
    <span id="charCount">0 characters</span>
    <span id="autoTranslateStatus" class="auto-status"></span>
</div>
```

```javascript
inputTextarea.addEventListener('input', () => {
    const length = inputTextarea.value.length;
    document.getElementById('charCount').textContent = `${length} characters`;
    
    if (autoTranslateEnabled && length >= AUTO_TRANSLATE_MIN_LENGTH) {
        document.getElementById('autoTranslateStatus').textContent = '⏱️ Auto-translating...';
    } else {
        document.getElementById('autoTranslateStatus').textContent = '';
    }
});
```

### Enhancement 2: Disable Manual Button When Auto-Translate is On

```javascript
toggle.addEventListener('change', (e) => {
    autoTranslateEnabled = e.target.checked;
    const translateButton = document.getElementById('translateBtn');
    
    if (autoTranslateEnabled) {
        translateButton.disabled = true;
        translateButton.style.opacity = '0.5';
        translateButton.title = 'Auto-translate is enabled';
    } else {
        translateButton.disabled = false;
        translateButton.style.opacity = '1';
        translateButton.title = '';
    }
});
```

### Enhancement 3: Smart Delay Based on Text Length

```javascript
function getAutoTranslateDelay(textLength) {
    if (textLength < 50) return 500;      // Short text: 0.5s
    if (textLength < 200) return 800;     // Medium text: 0.8s
    if (textLength < 500) return 1200;    // Long text: 1.2s
    return 2000;                          // Very long: 2s
}

// Use in input listener:
const delay = getAutoTranslateDelay(text.length);
autoTranslateTimer = setTimeout(() => {
    triggerAutoTranslate();
}, delay);
```

---

## 🧪 Testing Checklist

After implementation, test these scenarios:

- [ ] Toggle auto-translate on/off
- [ ] Type slowly - translation should trigger after delay
- [ ] Type fast - should cancel previous requests
- [ ] Clear input - output should clear
- [ ] Switch languages while auto-translate is on
- [ ] Long text (>1000 chars) - should still work
- [ ] Network error handling
- [ ] Manual translate button behavior

---

## ⚡ Performance Considerations

### GPU Usage
- Auto-translate will increase GPU calls
- Monitor GPU memory if running locally
- Consider disabling for very long texts (>1000 chars)

### Request Optimization
```javascript
// Only auto-translate for short/medium text
const MAX_AUTO_TRANSLATE_LENGTH = 1000;

if (text.length > MAX_AUTO_TRANSLATE_LENGTH) {
    document.getElementById('autoTranslateStatus').textContent = 
        '⚠️ Text too long for auto-translate. Use manual button.';
    return;
}
```

---

## 🐛 Troubleshooting

### Issue: Too many requests
**Solution**: Increase `AUTO_TRANSLATE_DELAY` to 1000-1500ms

### Issue: Translations feel laggy
**Solution**: 
- Check GPU is being used (not CPU)
- Reduce delay to 500ms for better responsiveness
- Ensure abort controller is canceling old requests

### Issue: Output flickers
**Solution**: Add smooth CSS transitions:
```css
#outputText {
    transition: opacity 0.2s ease;
}
```

---

## 📝 Configuration Options

You can customize these values in `script.js`:

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTO_TRANSLATE_DELAY` | 800ms | Wait time after typing stops |
| `AUTO_TRANSLATE_MIN_LENGTH` | 2 chars | Minimum text length to trigger |
| `MAX_AUTO_TRANSLATE_LENGTH` | 1000 chars | Max length for auto-translate |

---

## 🚀 Deployment Notes

1. **Test thoroughly** before deploying to production
2. **Monitor backend logs** for increased request volume
3. **Consider rate limiting** if multiple users are using auto-translate
4. **Update documentation** to mention the new feature

---

## 📚 Additional Resources

- [MDN: AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController)
- [Debouncing in JavaScript](https://www.freecodecamp.org/news/javascript-debounce-example/)
- [Fetch API with Abort](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#aborting_a_fetch)

---

**Happy Coding! 🎉**

If you encounter any issues, check the browser console for errors and verify all event listeners are properly attached.
