from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    from PIL import Image
except Exception:
    Image = None

try:
    import pytesseract
except Exception:
    pytesseract = None

if pytesseract is not None:
    # Windows fallback: use default installer path when PATH is not updated yet.
    tesseract_default = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if tesseract_default.exists():
        pytesseract.pytesseract.tesseract_cmd = str(tesseract_default)


class ExtractionError(Exception):
    pass


@dataclass
class ExtractedContent:
    text: str
    source_type: str


def _extract_pdf_text(path: Path) -> str:
    if pdfplumber is None and fitz is None:
        raise ExtractionError(
            "PDF parsing dependency missing. Install pdfplumber or pymupdf."
        )

    text_chunks: list[str] = []

    if pdfplumber is not None:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                # layout=True keeps spacing/newlines closer to original formatting.
                page_text = page.extract_text(layout=True) or ""
                text_chunks.append(page_text)

    if not any(chunk.strip() for chunk in text_chunks) and fitz is not None:
        text_chunks = []
        with fitz.open(path) as doc:
            for page in doc:
                text_chunks.append(page.get_text("text") or "")

    text = "\n\n".join(text_chunks).strip()
    if not text:
        raise ExtractionError("No text could be extracted from the PDF.")

    return text


def _extract_image_text(path: Path) -> str:
    if pytesseract is None or Image is None:
        raise ExtractionError(
            "OCR dependencies missing. Install pytesseract and pillow."
        )

    try:
        image = Image.open(path)
    except Exception as exc:
        raise ExtractionError("Unable to open image for OCR.") from exc

    try:
        text = pytesseract.image_to_string(image)
    except Exception as exc:
        raise ExtractionError(
            "OCR processing failed. Ensure Tesseract OCR is installed on the host."
        ) from exc

    if not text.strip():
        raise ExtractionError("No text found in the image.")

    return text.strip()


def extract_text_from_file(path: Path) -> ExtractedContent:
    ext = path.suffix.lower()

    if ext == ".pdf":
        return ExtractedContent(text=_extract_pdf_text(path), source_type="pdf")

    if ext in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
        return ExtractedContent(text=_extract_image_text(path), source_type="image")

    raise ExtractionError("Unsupported file type.")
