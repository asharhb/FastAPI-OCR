from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pytesseract
from PIL import Image
import pdf2image
import io
import os
import uvicorn
from typing import List, Optional

# Set Tesseract environment variable - this points to your tessdata directory
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata/'

# Create FastAPI app
app = FastAPI(title="Document OCR App")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

# Create templates object
templates = Jinja2Templates(directory="templates")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create CSS file
with open("static/css/style.css", "w") as f:
    f.write("""
 
    :root {
        --primary-color: #4285f4;
        --primary-hover: #2b6cb0;
        --background-color: #f8f9fa;
        --card-bg: #ffffff;
        --text-color: #333333;
        --border-color: #e2e8f0;
    }

    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }

    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        background-color: var(--background-color);
        color: var(--text-color);
    }

    .container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
    }

    .header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: var(--primary-color);
    }

    .header p {
        font-size: 1.1rem;
        color: #666;
    }

    .card {
        background-color: var(--card-bg);
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 2rem;
        margin-bottom: 2rem;
    }

    .upload-form {
        display: flex;
        flex-direction: column;
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .file-input-wrapper {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2rem;
        border: 2px dashed var(--border-color);
        border-radius: 8px;
        background-color: #f7fafc;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .file-input-wrapper:hover {
        background-color: #edf2f7;
    }

    .file-input-wrapper input[type="file"] {
        position: absolute;
        left: 0;
        top: 0;
        opacity: 0;
        width: 100%;
        height: 100%;
        cursor: pointer;
    }

    .file-input-wrapper i {
        font-size: 2.5rem;
        color: var(--primary-color);
        margin-bottom: 1rem;
    }

    .file-input-wrapper p {
        font-size: 1rem;
        text-align: center;
    }

.file-name {
    margin-top: 1rem;
    margin-bottom: 1rem;
    font-size: 1rem;
    color: var(--primary-color);
    background-color: #e8f0fe;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    display: inline-block;
    box-shadow: 0 1px 3px rgba(66, 133, 244, 0.4);
    font-weight: 600;
}
            
.file-name span{
    color: black;
}

    .language-select {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid var(--border-color);
        border-radius: 4px;
        font-size: 1rem;
        background-color: white;
    }

    .btn {
        display: inline-block;
        background-color: var(--primary-color);
        color: white;
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 4px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .btn:hover {
        background-color: var(--primary-hover);
    }

    .btn-block {
        width: 100%;
    }

    .result-card {
        display: none;
    }

    .result-card.active {
        display: block;
    }

    .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }

    .result-content {
        background-color: #f7fafc;
        padding: 1.5rem;
        border-radius: 4px;
        white-space: pre-wrap;
        max-height: 500px;
        overflow-y: auto;
    }

    .copy-btn {
        background-color: transparent;
        color: var(--primary-color);
        border: 1px solid var(--primary-color);
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .copy-btn:hover {
        background-color: var(--primary-color);
        color: white;
    }

    .loader {
        display: none;
        text-align: center;
        margin: 2rem 0;
    }

    .loader.active {
        display: block;
    }

    .spinner {
        width: 50px;
        height: 50px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    .footer {
    text-align: center;
    padding: 1.5rem 0;
    margin-top: 2rem;
    color: #666;
    font-size: 0.9rem;
    border-top: 1px solid var(--border-color);
}

.footer a {
    color: var(--primary-color);
    text-decoration: none;
}

.footer a:hover {
    text-decoration: underline;
}

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .error-message {
        color: #e53e3e;
        background-color: #fed7d7;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }

    @media (max-width: 768px) {
        .container {
            padding: 10px;
        }

        .card {
            padding: 1.5rem;
        }

        .header h1 {
            font-size: 2rem;
        }
    }
    
    """)

# Create JS file
with open("static/js/script.js", "w") as f:
    f.write("""
    document.addEventListener('DOMContentLoaded', function() {
        const fileInput = document.getElementById('file');
        const fileName = document.getElementById('file-name');
        const form = document.getElementById('upload-form');
        const resultCard = document.getElementById('result-card');
        const loader = document.getElementById('loader');
        const copyBtn = document.getElementById('copy-btn');

        // Update file name when file is selected
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                fileName.textContent = this.files[0].name;
                fileName.style.display = 'block';
            } else {
                fileName.style.display = 'none';
            }
        });

        // Handle form submission
        form.addEventListener('submit', function(e) {
            // Show loader
            loader.classList.add('active');

            // Hide previous result if any
            resultCard.classList.remove('active');
        });

        // Copy result to clipboard
        copyBtn.addEventListener('click', function() {
            const resultText = document.getElementById('result-text');

            // Create a temporary textarea element
            const textarea = document.createElement('textarea');
            textarea.value = resultText.textContent;
            document.body.appendChild(textarea);

            // Select and copy the text
            textarea.select();
            document.execCommand('copy');

            // Remove the temporary textarea
            document.body.removeChild(textarea);

            // Update button text temporarily
            const originalText = this.textContent;
            this.textContent = 'Copied!';

            // Reset button text after 2 seconds
            setTimeout(() => {
                this.textContent = originalText;
            }, 2000);
        });
    });
            
            // Handle text download
const downloadBtn = document.getElementById('download-btn');
downloadBtn.addEventListener('click', function() {
    const resultText = document.getElementById('result-text').textContent;

    // Create a Blob with the text content
    const blob = new Blob([resultText], { type: 'text/plain' });

    // Create a temporary anchor element
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'extracted_text.txt'; // File name for download
    document.body.appendChild(a);

    // Trigger the download
    a.click();

    // Clean up
    document.body.removeChild(a);
});
    """)

# Create HTML template file
with open("templates/index.html", "w") as f:
    f.write("""

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document OCR Tool</title>
    <link rel="stylesheet" href="{{ url_for('static', path='/css/style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Document OCR Tool</h1>
            <p>Extract text from images and PDF documents in multiple languages</p>
        </div>

        <div class="card">
            <form id="upload-form" class="upload-form" action="/extract_text" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="file">Upload Document</label>
                    <div class="file-input-wrapper">
                        <i class="fas fa-cloud-upload-alt"></i>
                        <p>Drag & drop your file here or click to select</p>
                        <p>Supported formats: PNG, JPG, PDF</p>
                        <input type="file" id="file" name="file" accept="image/*,.pdf" required>
                        <p id="file-name" class="file-name" style="display: none;"></p>
                    </div>
                </div>
{% if uploaded_filename %}              
<p class="file-name" style="display: block;">Uploaded File: <span>{{ uploaded_filename }}</span></p>
{% endif %}
                <div class="form-group">
                    <label for="language">Select Language</label>
                    <select id="language" name="language" class="language-select">
                        <option value="eng">English</option>
                        <option value="deu">German</option>
                        <option value="fra">French</option>
                        <option value="spa">Spanish</option>
                        <option value="ita">Italian</option>
                        <option value="por">Portuguese</option>
                        <option value="rus">Russian</option>
                        <option value="ara">Arabic</option>
                        <option value="urd">Urdu</option>
                        <option value="hin">Hindi</option>
                        <option value="chi_sim">Chinese (Simplified)</option>
                        <option value="jpn">Japanese</option>
                        <option value="kor">Korean</option>
                    </select>
                </div>

                <button type="submit" class="btn btn-block">
                    <i class="fas fa-search"></i> Extract Text
                </button>
            </form>
        </div>

        <div id="loader" class="loader{% if is_processing %} active{% endif %}">
            <div class="spinner"></div>
            <p>Processing your document...</p>
        </div>

        {% if error %}
        <div class="error-message">
            <p>{{ error }}</p>
        </div>
        {% endif %}

        {% if extracted_text %}
        <div id="result-card" class="card result-card active">
    <div class="result-header">
        <h2>Extracted Text</h2>
        <div>
            <button id="copy-btn" class="copy-btn">
                <i class="fas fa-copy"></i> Copy Text
            </button>
            <button id="download-btn" class="copy-btn">
                <i class="fas fa-download"></i> Download Text
            </button>
        </div>
    </div>
    <div id="result-text" class="result-content">{{ extracted_text }}</div>
</div>
        {% endif %}
    </div>
    
    <footer class="footer">
    <p>Developed by Ashar Habib</p>
</footer>

    <script src="{{ url_for('static', path='/js/script.js') }}"></script>
</body>
</html>
    
    """)

# Define available languages
AVAILABLE_LANGUAGES = {
    "eng": "English",
    "deu": "German",
    "fra": "French",
    "spa": "Spanish",
    "ita": "Italian",
    "por": "Portuguese",
    "rus": "Russian",
    "ara": "Arabic",
    "urd": "Urdu",
    "hin": "Hindi",
    "chi_sim": "Chinese (Simplified)",
    "jpn": "Japanese",
    "kor": "Korean"
}


# Add a debug route to check tesseract installation
@app.get("/check_tesseract")
async def check_tesseract():
    try:
        # Get tesseract version
        version = pytesseract.get_tesseract_version()
        # List available languages
        langs = pytesseract.get_languages()
        return {
            "tesseract_version": version,
            "available_languages": langs,
            "tessdata_prefix": os.environ.get('TESSDATA_PREFIX', 'Not set'),
            "status": "Tesseract is working properly"
        }
    except Exception as e:
        return {
            "error": str(e),
            "tessdata_prefix": os.environ.get('TESSDATA_PREFIX', 'Not set'),
            "status": "Tesseract configuration error"
        }


# Function to process PDF files
def extract_text_from_pdf(pdf_bytes, language='eng'):
    # Convert PDF to images
    images = pdf2image.convert_from_bytes(pdf_bytes)

    # Extract text from each page
    extracted_text = ""
    for i, img in enumerate(images):
        page_text = pytesseract.image_to_string(img, lang=language)
        extracted_text += page_text + "\n\n--- Page Break ---\n\n"

    return extracted_text


# Create routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/extract_text", response_class=HTMLResponse)
async def extract_text(request: Request, file: UploadFile = File(...), language: str = Form('eng')):
    # Read file content
    content = await file.read()

    try:
        # Check if selected language is available
        if language not in AVAILABLE_LANGUAGES:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": f"Selected language '{language}' is not supported.",
                    "is_processing": False,
                    "uploaded_filename": file.filename
                }
            )

        extracted_text = ""

        # Check file extension
        if file.filename.lower().endswith('.pdf'):
            # Process PDF file
            extracted_text = extract_text_from_pdf(content, language)
        elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Process image file
            image = Image.open(io.BytesIO(content))
            extracted_text = pytesseract.image_to_string(image, lang=language)
        else:
            # Unsupported file format
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": "This file format is not supported. Please upload a PDF or image file.",
                    "is_processing": False,
                    "uploaded_filename": file.filename
                }
            )

        # Check if extracted text is empty
        if not extracted_text.strip():
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": "The uploaded file contains no text to extract.",
                    "is_processing": False,
                    "uploaded_filename": file.filename
                }
            )

        # Return template with extracted text
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "extracted_text": extracted_text,
                "is_processing": False,
                "uploaded_filename": file.filename
            }
        )

    except Exception as e:
        # Return template with error message
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": f"Error processing file: {str(e)}",
                    "is_processing": False,
                    "uploaded_filename": file.filename
                }
            )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
