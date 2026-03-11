# Text Replacement - Quick Start Guide

## 🚀 Get Started in 30 Seconds

### 1. Install Dependencies (if not already done)
```bash
pip3 install -r requirements.txt
```

### 2. Install Tesseract OCR
```bash
# macOS
brew install tesseract

# Linux
sudo apt install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Launch the Application
```bash
python3 main.py
```

---

## 📝 Replace Text in 5 Steps

### Step 1: Load an Image
Click **"Upload Image"** and select an image with text

### Step 2: Detect Text
Press **`Ctrl+F`** or click **"🔍 Detect Text in Image"**

### Step 3: Select Text Block
Click any text block in the list to select it
- Yellow highlight appears on the canvas
- Selection info shows below the list

### Step 4: Enter Replacement
Type your new text in the **"Replace with:"** field

### Step 5: Replace
- Press **`Enter`** or click **"✏️ Replace Selected Text"**
- Or click **"🔄 Replace All Occurrences"** to replace all matching text

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+F` | Detect text in image |
| `Enter` | Replace selected text |
| `Escape` | Deselect text block |
| `Ctrl+Z` | Undo replacement |
| `Ctrl+Y` | Redo replacement |

---

## 💡 Pro Tips

### Get Better Results
1. **Use high-quality images** - Clear text detects better
2. **Adjust contrast first** - If text is faint, increase contrast before detection
3. **Test on one block** - Try single replacement before replacing all
4. **Choose the right color** - Click "Choose Color" to match original text color

### Common Workflows

**Quick Edit:**
```
Ctrl+F → Click text → Type replacement → Enter
```

**Batch Replace:**
```
Ctrl+F → Click text → Type replacement → Click "Replace All"
```

**Undo Mistake:**
```
Ctrl+Z
```

---

## 🎯 Example Use Cases

### 1. Update Product Labels
- Detect text on product packaging
- Replace product name or price
- Export updated image

### 2. Edit Memes
- Detect meme text
- Replace with your own text
- Share your creation

### 3. Translate Signs
- Detect text on signs
- Replace with translated text
- Export localized version

### 4. Fix Typos
- Detect text with typos
- Replace with correct spelling
- Save corrected image

---

## ⚠️ Troubleshooting

### "No text found in image"
**Solution:** Adjust image contrast/brightness first, then try again

### "Tesseract not found"
**Solution:** Install Tesseract OCR (see installation instructions above)

### Text replacement looks wrong
**Solution:** 
- Manually adjust font color
- Try with simpler background
- Use higher resolution image

### Small text warning
**Solution:** Text under 8px may not replace accurately - proceed with caution

---

## 📊 What Gets Detected

✅ **Works Great:**
- Horizontal text
- Clear, readable fonts
- Good contrast with background
- Standard font sizes (12px+)

⚠️ **May Have Issues:**
- Rotated or curved text
- Very small text (<8px)
- Low contrast text
- Handwritten text
- Decorative fonts

---

## 🔧 Advanced Features

### Color Detection
The app automatically detects the original text color. You can override it:
1. Select a text block
2. Click "Choose Color"
3. Pick your desired color
4. Replace text

### Replace All
Replace multiple occurrences at once:
1. Select any instance of the text
2. Enter replacement text
3. Click "🔄 Replace All Occurrences"
4. Confirm the action
5. All matching text is replaced in one operation

### Visual Feedback
- **Yellow highlight** = Selected text block
- **List selection** = Currently selected
- **Status label** = Shows position and text

---

## 📚 More Information

- **Full Guide:** See `TEXT_REPLACEMENT_GUIDE.md`
- **Technical Details:** See `TEXT_REPLACEMENT_COMPLETE.md`
- **General Help:** See `README.md`

---

## ✅ Verification

Run the verification script to check everything is working:
```bash
python3 verify_text_replacement.py
```

Should show: **"✓ All tests passed!"**

---

## 🎉 You're Ready!

The text replacement feature is fully functional and ready to use. Start by loading an image and pressing `Ctrl+F` to detect text!

**Happy Editing! 🖼️✨**
