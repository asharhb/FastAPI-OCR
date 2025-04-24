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

# Set Tesseract environment variable - this points to your tessdata directory
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata/'

# Create FastAPI app
app = FastAPI(title="Document OCR App")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Create templates object
templates = Jinja2Templates(directory="templates")

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create HTML template file
with open("templates/index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Document OCR</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .container {
            background-color: #f9f9f9;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            white-space: pre-wrap;
        }
        .upload-form {
            margin: 20px 0;
        }
        input[type="file"] {
            margin-bottom: 10px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        h1 {
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Document OCR</h1>
        <p>Upload an image or PDF document to extract text</p>

        <div class="upload-form">
            <form action="/extract_text" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/*,.pdf" required>
                <br>
                <button type="submit">Extract Text</button>
            </form>
        </div>

        {% if extracted_text %}
        <div class="result">
            <h3>Extracted Text:</h3>
            <p>{{ extracted_text }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
    """)


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
def extract_text_from_pdf(pdf_bytes):
    # Convert PDF to images
    images = pdf2image.convert_from_bytes(pdf_bytes)

    # Extract text from each page
    extracted_text = ""
    for img in images:
        page_text = pytesseract.image_to_string(img)
        extracted_text += page_text + "\n\n--- Page Break ---\n\n"

    return extracted_text


# Create routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "extracted_text": ""})


@app.post("/extract_text", response_class=HTMLResponse)
async def extract_text(request: Request, file: UploadFile = File(...)):
    # Read file content
    content = await file.read()

    try:
        extracted_text = ""

        # Check file extension
        if file.filename.lower().endswith('.pdf'):
            # Process PDF file
            extracted_text = extract_text_from_pdf(content)
        else:
            # Process image file
            image = Image.open(io.BytesIO(content))
            extracted_text = pytesseract.image_to_string(image)

        # Return template with extracted text
        return templates.TemplateResponse("index.html", {"request": request, "extracted_text": extracted_text})

    except Exception as e:
        # Return template with error message
        return templates.TemplateResponse("index.html",
                                          {"request": request,
                                           "extracted_text": f"Error processing file: {str(e)}"})


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)