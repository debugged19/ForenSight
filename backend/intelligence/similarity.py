<<<<<<< HEAD
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
=======
def calculate_threat_score(web_matches):
    """
    Calculate an overall threat score based on web scan results.
    Higher scores indicate higher risk of image theft or tampering.
    """
    if not web_matches:
        return {
            "score": 0.0,
            "level": "LOW",
            "description": "No similar images found online"
        }

    # Simple scoring: average similarity * number of matches
    avg_similarity = sum(match["similarity"] for match in web_matches) / len(web_matches)
    score = min(avg_similarity * len(web_matches), 1.0)

    if score > 0.8:
        level = "HIGH"
        desc = "High risk - multiple similar images found"
    elif score > 0.5:
        level = "MEDIUM"
        desc = "Medium risk - some similar images detected"
    else:
        level = "LOW"
        desc = "Low risk - minimal online matches"

    return {
        "score": round(score, 2),
        "level": level,
        "description": desc,
        "matches_found": len(web_matches)
>>>>>>> efa620a13ba3088b30acac415fbcd45a0e667f50
    }