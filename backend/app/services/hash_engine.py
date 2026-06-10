import hashlib
from typing import List


def compute_file_hash(file_bytes: bytes) -> str:
    """Compute SHA-256 hash of file contents."""
    return hashlib.sha256(file_bytes).hexdigest()


def compute_combined_hash(hashes: List[str]) -> str:
    """Compute a Merkle-like combined hash for the evidence chain."""
    combined = "".join(sorted(hashes))
    return hashlib.sha256(combined.encode()).hexdigest()


def verify_hash(file_bytes: bytes, expected_hash: str) -> bool:
    """Verify file integrity against stored hash."""
    return compute_file_hash(file_bytes) == expected_hash
