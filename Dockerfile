# Use official Python slim image
FROM python:3.10-slim

# Install system-level dependencies for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variable to help pytesseract find language data
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# Set working directory
WORKDIR /app

# Copy all project files to container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (optional, for documentation)
EXPOSE 8000

# Start FastAPI app using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

