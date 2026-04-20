import imagehash
from PIL import Image
import hashlib

def generate_phash(image_path):
    """
    Generate a perceptual hash of an image.
    Returns a hex string that represents the image's visual fingerprint.
    Similar images will have similar (close) hashes.
    """
    try:
        img = Image.open(image_path)
        phash = imagehash.phash(img)
        dhash = imagehash.dhash(img)
        return {
            "phash": str(phash),
            "dhash": str(dhash),
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def compare_hashes(hash1_str, hash2_str):
    """
    Compare two perceptual hashes.
    Returns similarity as a percentage (100% = identical).
    """
    h1 = imagehash.hex_to_hash(hash1_str)
    h2 = imagehash.hex_to_hash(hash2_str)
    # Hamming distance: 0 = identical, 64 = completely different
    distance = h1 - h2
    similarity = round((1 - distance / 64) * 100, 2)
    return max(0, similarity)

