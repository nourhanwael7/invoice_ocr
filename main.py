import os
import cv2
import numpy as np
import pytesseract
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'jfif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Set tesseract path - IMPORTANT: Change this to match your installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('output_path/ocr', exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_string(img_path):
    """
    Process image and extract text using OCR with preprocessing
    """
    try:
        # Read image using opencv
        img = cv2.imread(img_path)
        
        if img is None:
            return "Error: Could not read image"
        
        # Extract the file name without the file extension
        file_name = os.path.basename(img_path).split('.')[0]
        file_name = file_name.split()[0]
        
        # Create a directory for outputs
        output_path = os.path.join('output_path', "ocr")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # Rescale the image, if needed
        img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
        
        # Converting to gray scale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Removing Shadows
        rgb_planes = cv2.split(img)
        result_planes = []
        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            result_planes.append(diff_img)
        img = cv2.merge(result_planes)
        
        # Apply dilation and erosion to remove some noise
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)  # increases white region
        img = cv2.erode(img, kernel, iterations=1)   # erodes boundaries
        
        # Apply threshold to get image with only b&w (binarization)
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Save the filtered image in the output directory
        save_path = os.path.join(output_path, file_name + "_filter_processed.png")
        cv2.imwrite(save_path, img)
        
        # Recognize text with tesseract for python
        custom_config = r'--oem 3 --psm 6'
        result = pytesseract.image_to_string(img, lang="eng", config=custom_config)
        
        # Clean up the result
        result = result.strip()
        return result
        
    except Exception as e:
        return f"Error processing image: {str(e)}"

@app.route('/')
def index():
    """Render the main upload page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and OCR processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid conflicts
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the image and extract text
        extracted_text = get_string(filepath)
        
        # Split text into lines for better display
        text_lines = [line for line in extracted_text.split('\n') if line.strip()]
        
        # Calculate statistics
        stats = {
            'characters': len(extracted_text),
            'words': len(extracted_text.split()),
            'lines': len(text_lines)
        }
        
        # Clean up - remove uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'success': True,
            'text': extracted_text,
            'lines': text_lines,
            'stats': stats
        })
    
    return jsonify({'error': 'Invalid file type. Allowed types: PNG, JPG, JPEG, GIF, BMP, JFIF'})

if __name__ == '__main__':
    print("=" * 60)
    print("OCR Application Started")
    print("=" * 60)
    print("IMPORTANT: Make sure Tesseract is installed at:")
    print(pytesseract.pytesseract.tesseract_cmd)
    print("\nIf not, download from:")
    print("https://github.com/UB-Mannheim/tesseract/wiki")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)