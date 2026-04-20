<<<<<<< HEAD
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()
VISION_API_KEY = os.getenv("VISION_API_KEY")

def encode_image_to_base64(image_path):
    """Convert image file to base64 string for API."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def scan_web_for_matches(image_path):
    """
    Use Google Vision API Web Detection to find where
    this image (or visually similar ones) appear on the internet.
    Returns list of found URLs with match type.
    """
    image_b64 = encode_image_to_base64(image_path)

    url = f"https://vision.googleapis.com/v1/images:annotate?key={VISION_API_KEY}"

    payload = {
        "requests": [{
            "image": {"content": image_b64},
            "features": [{"type": "WEB_DETECTION", "maxResults": 10}]
        }]
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if "error" in data:
        return {"status": "error", "message": data["error"]}

    web_data = data["responses"][0].get("webDetection", {})

    results = {
        "status": "success",
        "exact_matches": [],
        "partial_matches": [],
        "similar_images": [],
        "pages_with_image": []
    }

    for match in web_data.get("fullMatchingImages", []):
        results["exact_matches"].append(match["url"])

    for match in web_data.get("partialMatchingImages", []):
        results["partial_matches"].append(match["url"])

    for match in web_data.get("visuallySimilarImages", []):
        results["similar_images"].append(match["url"])

    for page in web_data.get("pagesWithMatchingImages", []):
        results["pages_with_image"].append({
            "url": page.get("url"),
            "title": page.get("pageTitle", "Unknown Page")
        })

    return results
=======
def scan_web_for_matches(image_path):
    """
    Scan the web for identical or similar images.
    Returns a list of potential matches with URLs and similarity scores.
    """
    # Stub implementation - in a real system, this would:
    # 1. Generate image hash/fingerprint
    # 2. Query reverse image search APIs (Google, TinEye, etc.)
    # 3. Return list of matching URLs with confidence scores

    return [
        {
            "url": "https://example.com/matching-image.jpg",
            "similarity": 0.95,
            "platform": "Example Search Engine",
            "description": "Potential match found"
        }
    ]
>>>>>>> efa620a13ba3088b30acac415fbcd45a0e667f50
