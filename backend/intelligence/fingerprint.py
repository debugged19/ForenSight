import imagehash
from PIL import Image

def generate_phash(image_path):
    """
    Generate a perceptual hash (phash) of the image.
    This hash represents the image's visual content and can be used
    to detect similar or identical images.
    """
    try:
        img = Image.open(image_path)
        phash = imagehash.phash(img)
        return str(phash)
    except Exception as e:
        return f"Error generating phash: {str(e)}"