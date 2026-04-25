from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os, uuid
from werkzeug.utils import secure_filename

# YOUR modules
from intelligence.fingerprint import generate_phash
from intelligence.web_scan import scan_web_for_matches
from intelligence.similarity import calculate_threat_score

# TEAMMATE'S modules
from forensics.metadata import extract_exif_metadata
from forensics.crypto_hash import create_ownership_record
from forensics.tamper_detect import detect_tampering

app = Flask(__name__)
CORS(app, origins=["https://forensight.netlify.app", "http://localhost:3000"])

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return jsonify({"status": "ForenSight API running", "version": "1.0"})

@app.route("/scan", methods=["POST"])
def scan_image():
    """
    Main endpoint. Accepts an image upload and runs the full forensic scan.
    Returns combined results from both intelligence and forensics modules.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not allowed_file(file.filename):
        return jsonify({"error": "Only image files allowed (png, jpg, jpeg, webp)"}), 400

    # Save uploaded file with a unique ID
    unique_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_{filename}")
    file.save(file_path)

    try:
        # Run ALL modules
        fingerprint = generate_phash(file_path)
        web_matches = scan_web_for_matches(file_path)
        threat_score = calculate_threat_score(web_matches)
        metadata = extract_exif_metadata(file_path)
        ownership = create_ownership_record(file_path)
        tamper = detect_tampering(file_path)

        # Combine everything into one response
        result = {
            "scan_id": unique_id,
            "filename": filename,
            "intelligence": {
                "fingerprint": fingerprint,
                "web_scan": web_matches,
                "threat_assessment": threat_score
            },
            "forensics": {
                "metadata": metadata,
                "ownership_record": ownership,
                "tamper_analysis": tamper
            }
        }
        return jsonify(result)

    finally:
        # Clean up uploaded file after scanning
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)