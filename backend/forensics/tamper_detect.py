from PIL import Image
import exifread

def detect_tampering(image_path):
    """
    Forensic analysis to detect signs of image tampering or theft.
    Returns a list of forensic flags with severity levels.
    """
    flags = []
    risk_level = "LOW"

    try:
        img = Image.open(image_path)
        img_format = img.format  # JPEG, PNG, etc.
        img_mode = img.mode

        # Check 1: Is EXIF metadata missing entirely?
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)

        if not tags:
            flags.append({
                "type": "METADATA_STRIPPED",
                "severity": "HIGH",
                "description": "No EXIF metadata found. Metadata may have been deliberately removed — a common sign of re-uploaded stolen content."
            })
            risk_level = "HIGH"

        # Check 2: Missing camera timestamp but file has other tags
        elif "EXIF DateTimeOriginal" not in tags and len(tags) > 5:
            flags.append({
                "type": "TIMESTAMP_MISSING",
                "severity": "MEDIUM",
                "description": "Original capture timestamp is absent. File may have been edited or re-exported."
            })
            if risk_level == "LOW":
                risk_level = "MEDIUM"

        # Check 3: JPEG re-compression artifacts
        if img_format == "JPEG":
            flags.append({
                "type": "JPEG_FORMAT",
                "severity": "INFO",
                "description": "File is JPEG format. Note: JPEG compression can degrade forensic evidence on repeated saves."
            })

        # Check 4: Suspicious color mode (can indicate screenshot or re-capture)
        if img_mode == "P":
            flags.append({
                "type": "PALETTE_MODE",
                "severity": "MEDIUM",
                "description": "Image uses palette color mode — may indicate screenshot or screen-recorded re-capture."
            })

    except Exception as e:
        flags.append({
            "type": "ANALYSIS_ERROR",
            "severity": "INFO",
            "description": f"Could not complete full analysis: {str(e)}"
        })

    return {
        "status": "success",
        "forensic_flags": flags,
        "flag_count": len(flags),
        "tamper_risk": risk_level
    }

if __name__ == "__main__":
    output = detect_tampering(r"D:\Desktop\image_H2Ph4Fz.jpg")
    print(output)