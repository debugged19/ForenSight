import exifread
from PIL import Image
from PIL.ExifTags import TAGS
import os

def extract_exif_metadata(image_path):
    result = {
        "status": "success",
        "device": {},
        "timestamp": None,
        "gps": None,
        "software": None,
        "raw_tags": {}
    }

    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, details=True)

        for tag, value in tags.items():
            result["raw_tags"][tag] = str(value)

        if "Image Make" in tags:
            result["device"]["make"] = str(tags["Image Make"])
        if "Image Model" in tags:
            result["device"]["model"] = str(tags["Image Model"])

        if "EXIF DateTimeOriginal" in tags:
            result["timestamp"] = str(tags["EXIF DateTimeOriginal"])
        elif "Image DateTime" in tags:
            result["timestamp"] = str(tags["Image DateTime"])

        if "GPS GPSLatitude" in tags:
            result["gps"] = {
                "latitude": str(tags.get("GPS GPSLatitude")),
                "longitude": str(tags.get("GPS GPSLongitude"))
            }

        if "Image Software" in tags:
            result["software"] = str(tags["Image Software"])

    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)

    return result