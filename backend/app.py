
import os
import io

from flask import Flask, request, jsonify, send_from_directory
from matcher import match
import history_store

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/match", methods=["POST"])
def api_match():
    data = request.get_json(silent=True) or {}
    jd_text = (data.get("jd") or "").strip()
    cv_text = (data.get("cv") or "").strip()
    candidate_name = (data.get("candidate_name") or "").strip()

    if not jd_text or not cv_text:
        return jsonify({"error": "Both 'jd' and 'cv' text are required."}), 400

    result = match(jd_text, cv_text)

    
    history_store.add_record(candidate_name, jd_text, result)

    return jsonify(result)


@app.route("/api/history", methods=["GET"])
def api_get_history():
    return jsonify(history_store.get_all_records())


@app.route("/api/history/clear", methods=["POST"])
def api_clear_history():
    history_store.clear_history()
    return jsonify({"status": "cleared"})



@app.route("/api/extract-file", methods=["POST"])
def api_extract_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    f = request.files["file"]
    filename = f.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    try:
        if ext == "txt":
            text = f.read().decode("utf-8", errors="ignore")

        elif ext == "pdf":
            try:
                from PyPDF2 import PdfReader
            except ImportError:
                return jsonify({"error": "PyPDF2 not installed on server. Run: pip install PyPDF2"}), 500
            reader = PdfReader(io.BytesIO(f.read()))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

        elif ext == "docx":
            try:
                import docx
            except ImportError:
                return jsonify({"error": "python-docx not installed on server. Run: pip install python-docx"}), 500
            document = docx.Document(io.BytesIO(f.read()))
            text = "\n".join(p.text for p in document.paragraphs)

        else:
            return jsonify({"error": f"Unsupported file type: .{ext}. Use .txt, .pdf, or .docx"}), 400

    except Exception as e:
        return jsonify({"error": f"Could not read file: {str(e)}"}), 500

    return jsonify({"text": text.strip()})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
