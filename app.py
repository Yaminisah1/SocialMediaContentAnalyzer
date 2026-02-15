from __future__ import annotations

import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from analyzer import analyze_social_post
from extraction import ExtractionError, extract_text_from_file

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/analyze")
def analyze():
    uploaded = request.files.get("file")
    if uploaded is None:
        return jsonify({"error": "No file uploaded."}), 400

    filename = secure_filename(uploaded.filename or "")
    ext = Path(filename).suffix.lower()

    if not filename or ext not in ALLOWED_EXTENSIONS:
        return (
            jsonify(
                {
                    "error": "Unsupported file type. Upload PDF or image files only.",
                    "allowed_types": sorted(ALLOWED_EXTENSIONS),
                }
            ),
            400,
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / filename
        uploaded.save(file_path)

        try:
            extracted = extract_text_from_file(file_path)
        except ExtractionError as exc:
            return jsonify({"error": str(exc)}), 400
        except Exception:
            return jsonify({"error": "Unexpected processing error."}), 500

    analysis = analyze_social_post(extracted.text)

    return jsonify(
        {
            "filename": filename,
            "source_type": extracted.source_type,
            "extracted_text": extracted.text,
            "analysis": analysis,
        }
    )


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({"error": "File too large. Max size is 10 MB."}), 413


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)