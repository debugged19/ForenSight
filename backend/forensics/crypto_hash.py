import hashlib
import os
from datetime import datetime

def generate_sha256(file_path):
    """
    Generate a SHA-256 cryptographic hash of a file.
    This is the gold standard for proving a file's authenticity.
    The same file will ALWAYS produce the same hash.
    Any modification (even 1 pixel) produces a completely different hash.
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def create_ownership_record(file_path):
    """
    Create a complete ownership record for a file.
    Includes the hash, file size, and timestamp of when
    the creator registered their content with ForenSight.
    """
    file_hash = generate_sha256(file_path)
    file_size = os.path.getsize(file_path)
    registration_time = datetime.utcnow().isoformat() + "Z"

    return {
        "sha256_hash": file_hash,
        "file_size_bytes": file_size,
        "registered_at_utc": registration_time,
        "ownership_id": file_hash[:16].upper(),  # Short ID for display
        "status": "success"
    }