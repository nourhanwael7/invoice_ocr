# OCR Text Extraction Flask Application

A Flask-based web application for extracting text from images using Tesseract OCR with advanced image preprocessing.

##  Features

- Upload images (PNG, JPG, JPEG, GIF, BMP, JFIF)
- Advanced image preprocessing (shadow removal, noise reduction, binarization)
- Text extraction using Tesseract OCR
- Display extracted text with statistics (characters, words, lines)
- Clean and simple web interface

##  Prerequisites

- Python 3.7+
- Tesseract OCR installed on your system

##  Installation

### 1. Install Python dependencies

```bash
pip install flask opencv-python pytesseract numpy werkzeug pillow
```

### 2. Install Tesseract OCR

- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and note the installation path
  
3. **Upload an image:**
   - Click "Choose File"
   - Select an image containing text
   - Click "Upload and Process"
   - View the extracted text and statistics

##  Project Structure

```
ocr-flask-app/
│
├── main.py                 # Main Flask application
├── templates/
│   └── index.html        # Upload interface
├── uploads/              # Temporary upload directory
├── output_path/ocr/      # Processed images directory
└── README.md             # Project documentation
```

##  How It Works

### Image Preprocessing Pipeline:

1. **Rescaling** - Image is resized by 1.5x for better OCR accuracy
2. **Grayscale Conversion** - Converts to single channel
3. **Shadow Removal** - Using morphological operations
4. **Noise Reduction** - Dilation and erosion operations
5. **Binarization** - OTSU thresholding for black & white conversion
6. **OCR Processing** - Tesseract extracts text with custom configuration

##  License

MIT License

##  Contributing

Contributions, issues, and feature requests are welcome!

