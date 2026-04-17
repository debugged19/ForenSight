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
    }