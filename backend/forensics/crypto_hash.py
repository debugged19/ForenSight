import hashlib
import os
from datetime import datetime

def generate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def create_ownership_record(file_path):
    file_hash = generate_sha256(file_path)
    file_size = os.path.getsize(file_path)
    registration_time = datetime.utcnow().isoformat() + "Z"

    return {
        "sha256_hash": file_hash,
        "file_size_bytes": file_size,
        "registered_at_utc": registration_time,
        "ownership_id": file_hash[:16].upper(),
        "status": "success"
    }