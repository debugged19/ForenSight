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

# GEMINI
from shared.gemini_analyst import generate_forensic_summary

app = Flask(__name__)
CORS(app, origins=["https://forensight.netlify.app", "http://localhost:3000"])

UPLOAD_FOLDER = "uploads"
REPORTS_FOLDER = "reports"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return jsonify({"status": "ForenSight API running", "version": "1.0"})

@app.route("/scan", methods=["POST"])
def scan_image():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not allowed_file(file.filename):
        return jsonify({"error": "Only image files allowed (png, jpg, jpeg, webp)"}), 400

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

        # Run Gemini on the combined result
        ai_report = generate_forensic_summary(result)
        result["ai_forensic_report"] = ai_report

        # Save result to disk so /report can fetch it later
        import json
        report_path = os.path.join(REPORTS_FOLDER, f"{unique_id}.json")
        with open(report_path, "w") as f:
            json.dump(result, f)

        return jsonify(result)

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.route("/report/<scan_id>", methods=["GET"])
def download_report(scan_id):
    """Generate and return a PDF report for the given scan_id."""
    import json
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.units import mm
    from io import BytesIO

    # Load saved scan data
    report_path = os.path.join(REPORTS_FOLDER, f"{scan_id}.json")
    if not os.path.exists(report_path):
        return jsonify({"error": "Report not found. Scan may have expired."}), 404

    with open(report_path, "r") as f:
        data = json.load(f)

    # Build PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()
    story = []

    # Title style
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        fontSize=22, textColor=colors.HexColor("#00d4ff"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#888888"),
        spaceAfter=12
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#00d4ff"),
        spaceBefore=16, spaceAfter=6
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#333333"),
        spaceAfter=6, leading=16
    )
    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#888888"),
        spaceAfter=2
    )

    # Header
    story.append(Paragraph("🔍 ForenSight", title_style))
    story.append(Paragraph("Digital Forensic Report", subtitle_style))
    story.append(Paragraph(f"Case ID: {data.get('scan_id', '—')}", label_style))
    story.append(Paragraph(f"File: {data.get('filename', '—')}", label_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))

    # Threat Assessment
    threat = data.get("intelligence", {}).get("threat_assessment", {})
    story.append(Paragraph("Threat Assessment", section_style))
    story.append(Paragraph(f"Risk Level: <b>{threat.get('risk_level', '—')}</b>", body_style))
    story.append(Paragraph(f"Threat Score: <b>{threat.get('threat_score', 0)}/100</b>", body_style))
    story.append(Paragraph(f"Exact copies found online: {threat.get('exact_copy_count', 0)}", body_style))
    story.append(Paragraph(f"Partial copies found: {threat.get('partial_copy_count', 0)}", body_style))
    story.append(Paragraph(f"Affected pages: {threat.get('affected_pages', 0)}", body_style))

    # Ownership
    own = data.get("forensics", {}).get("ownership_record", {})
    story.append(Paragraph("Ownership Record", section_style))
    story.append(Paragraph(f"Ownership ID: {own.get('ownership_id', '—')}", body_style))
    story.append(Paragraph(f"SHA-256: {own.get('sha256_hash', '—')}", body_style))
    story.append(Paragraph(f"Registered at: {own.get('registered_at_utc', '—')}", body_style))
    story.append(Paragraph(f"File size: {own.get('file_size_bytes', '—')} bytes", body_style))

    # Tamper Analysis
    tam = data.get("forensics", {}).get("tamper_analysis", {})
    story.append(Paragraph("Tamper Analysis", section_style))
    story.append(Paragraph(f"Tamper Risk: <b>{tam.get('tamper_risk', '—')}</b>", body_style))
    flags = tam.get("forensic_flags", [])
    if flags:
        for f in flags:
            story.append(Paragraph(f"• [{f.get('severity','?')}] {f.get('type','')}: {f.get('description','')}", body_style))
    else:
        story.append(Paragraph("No forensic flags detected.", body_style))

    # Web Matches
    web = data.get("intelligence", {}).get("web_scan", {})
    story.append(Paragraph("Web Matches", section_style))
    exact = web.get("exact_matches", [])
    partial = web.get("partial_matches", [])
    story.append(Paragraph(f"Exact matches: {len(exact)} | Partial matches: {len(partial)}", body_style))
    for u in exact[:5]:
        story.append(Paragraph(f"• {u}", body_style))

    # AI Report
    ai = data.get("ai_forensic_report", {})
    story.append(Paragraph("Gemini AI Forensic Analysis", section_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dddddd")))
    story.append(Spacer(1, 6))
    ai_text = ai.get("analysis", "AI analysis not available.")
    # Split into paragraphs for better formatting
    for para in ai_text.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), body_style))

    doc.build(story)
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"forensight_report_{scan_id[:8]}.pdf"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)