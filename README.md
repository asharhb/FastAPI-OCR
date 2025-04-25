# FastAPI OCR Document Extractor

A lightweight and high-performance web application built with FastAPI, offering seamless Optical Character Recognition (OCR) for images and scanned documents. Upload, extract, and view text right from your browser — no authentication or setup required.

---

## Features

- 🔍 **One-Click OCR**  
  Upload documents and extract text in seconds.

- 🖼️ **Supports Multiple Formats**  
  PNG, JPG, JPEG, TIFF, and more.

- 🌐 **Multiple Language Support**  
  Supports OCR in multiple languages using Tesseract's language packs.

- ⚡ **Blazing Fast Performance**  
  Built with FastAPI for minimal latency and maximum throughput.

- 🧠 **Powered by Tesseract**  
  Leverages the open-source Tesseract OCR engine for accurate text extraction.

- 🧩 **Minimal Setup**  
  No authentication or complex configuration needed — just run and use.

---

## Supported Files in the Repository

- `app/main.py` - Main FastAPI application code handling OCR requests and routing.
- `app/__init__.py` - Package initialization.
- `static/` - Contains static assets like CSS and JavaScript files.
- `templates/` - HTML templates for the web interface.
- `requirements.txt` - Python dependencies required to run the application.
- `README.md` - This documentation file.

---

## Built With

- **FastAPI** – Web framework for APIs
- **Tesseract OCR** – OCR engine
- **Jinja2** – HTML templating

---

## Installation & Usage

1. Clone the repository.
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI app:  
   ```bash
   uvicorn app.main:app --reload
   ```
4. Open your browser and navigate to `http://localhost:8000` to use the OCR service.

---

## Notes

- Ensure Tesseract OCR is installed on your system and accessible in your PATH.
- To enable OCR for additional languages, install the corresponding Tesseract language packs.

---

Feel free to contribute or raise issues for improvements!
