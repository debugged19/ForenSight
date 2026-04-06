def calculate_threat_score(scan_results):
    """
    Takes web scan results and calculates an overall
    threat score for the content.
    Returns a score from 0-100 and a risk level label.
    """
    exact = len(scan_results.get("exact_matches", []))
    partial = len(scan_results.get("partial_matches", []))
    pages = len(scan_results.get("pages_with_image", []))

    # Weighted scoring: exact copies are most severe
    score = min(100, (exact * 20) + (partial * 10) + (pages * 5))

    if score == 0:
        level = "CLEAR"
        summary = "No unauthorized copies detected on the web."
    elif score < 30:
        level = "LOW"
        summary = "Minor presence detected. May be authorized shares."
    elif score < 60:
        level = "MEDIUM"
        summary = "Multiple unauthorized copies found. Review required."
    else:
        level = "HIGH"
        summary = "Significant content theft detected. Immediate action recommended."

    return {
        "threat_score": score,
        "risk_level": level,
        "summary": summary,
        "exact_copy_count": exact,
        "partial_copy_count": partial,
        "affected_pages": pages
    }