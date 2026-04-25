import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_forensic_summary(scan_results):
    """
    Send the full forensic scan results to Gemini and get back
    a plain-English investigation report written like a forensic analyst.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")

    threat = scan_results["intelligence"]["threat_assessment"]
    metadata = scan_results["forensics"]["metadata"]
    tamper = scan_results["forensics"]["tamper_analysis"]
    ownership = scan_results["forensics"]["ownership_record"]
    web = scan_results["intelligence"]["web_scan"]

    prompt = f"""
You are a digital forensics analyst writing an investigation report 
for a content creator whose image may have been stolen.

Here are the forensic findings:

THREAT ASSESSMENT:
- Risk Level: {threat['risk_level']}
- Threat Score: {threat['threat_score']}/100
- Exact copies found online: {threat['exact_copy_count']}
- Partial copies found: {threat['partial_copy_count']}
- Web pages containing this image: {threat['affected_pages']}

METADATA FORENSICS:
- Device: {metadata.get('device', 'Unknown')}
- Capture Timestamp: {metadata.get('timestamp', 'Not found')}
- GPS Data: {metadata.get('gps', 'Not present')}
- Software: {metadata.get('software', 'Unknown')}

TAMPER ANALYSIS:
- Tamper Risk: {tamper['tamper_risk']}
- Forensic Flags: {[f['type'] for f in tamper['forensic_flags']]}

OWNERSHIP RECORD:
- SHA-256 Hash: {ownership['sha256_hash'][:32]}...
- Registered: {ownership['registered_at_utc']}

Write a clear, professional 3-paragraph forensic report:
1. Overall verdict and risk assessment
2. Key forensic evidence found (or missing)
3. Recommended actions for the creator

Keep it factual, clear, and actionable. Do not use technical jargon without explanation.
"""

    try:
        response = model.generate_content(prompt)
        return {
            "status": "success",
            "analysis": response.text,
            "model_used": "gemini-1.5-flash"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "analysis": "AI analysis unavailable. Please review the raw findings above."
        }22