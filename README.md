# Social Media Content Analyzer

A Flask web app that accepts PDF or image uploads, extracts text, and generates engagement suggestions for social media content.

## Features
- PDF upload and parsing with formatting-preserving extraction (`pdfplumber` with fallback to `PyMuPDF`)
- Image upload and OCR text extraction (`pytesseract` + `Pillow`)
- Drag-and-drop and file picker UI
- Loading and error states
- Basic engagement analysis with score, metrics, and actionable suggestions

## Tech Stack
- Backend: Python, Flask
- Extraction: pdfplumber, PyMuPDF, Tesseract OCR via pytesseract
- Frontend: HTML, CSS, Vanilla JavaScript

## Local Setup
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Tesseract OCR on your machine and ensure it is available in `PATH`.
4. Run the app:
   ```bash
   python app.py
   ```
5. Open `http://localhost:5000`.

## Notes
- Max upload size is 10 MB.
- Supported files: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp`.
- OCR quality depends on image clarity and Tesseract installation.

## Deliverables mapping
- Working app: run locally or deploy this Flask app (Render/Railway/etc.)
- Source code + README: provided
- Brief write-up (200 words max): see `APPROACH.md`