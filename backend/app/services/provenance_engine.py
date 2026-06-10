from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.models.schemas import ProvenanceCheck


def verify_client_server_hash(
    client_hash: Optional[str], server_hash: str
) -> tuple[bool, Optional[str]]:
    """Compare client-side capture hash with server-computed hash."""
    if not client_hash:
        return False, "No client-side hash provided at capture"
    normalized_client = client_hash.lower().strip()
    normalized_server = server_hash.lower().strip()
    if normalized_client == normalized_server:
        return True, None
    return False, "Client capture hash does not match server hash (file may have changed in transit)"


def assess_capture_timestamp(
    client_captured_at: Optional[str], server_received_at: datetime
) -> tuple[float, List[str], Optional[float]]:
    """
    Score timestamp trust and flag suspicious upload delays.
    Returns (score 0-1, flags, latency_seconds).
    """
    flags: List[str] = []
    if not client_captured_at:
        flags.append("No client capture timestamp — provenance window unknown")
        return 0.5, flags, None

    try:
        captured = datetime.fromisoformat(client_captured_at.replace("Z", "+00:00"))
        if captured.tzinfo is None:
            captured = captured.replace(tzinfo=timezone.utc)
        received = server_received_at.replace(tzinfo=timezone.utc)
        latency = (received - captured).total_seconds()
    except (ValueError, TypeError):
        flags.append("Invalid client capture timestamp format")
        return 0.4, flags, None

    if latency < 0:
        flags.append("Client capture timestamp is in the future relative to server")
        return 0.2, flags, latency

    if latency > 86400 * 30:
        flags.append(
            f"Evidence captured {int(latency / 86400)} days before upload — stale capture window"
        )
        return 0.6, flags, latency

    if latency > 3600:
        flags.append(
            f"Evidence captured {int(latency / 60)} minutes before upload — verify chain of custody"
        )
        return 0.75, flags, latency

    return 1.0, flags, latency


def build_provenance_check(
    evidence_id: str,
    filename: str,
    server_hash: str,
    client_hash: Optional[str],
    client_captured_at: Optional[str],
    file_metadata: Dict[str, Any],
    server_received_at: Optional[datetime] = None,
) -> ProvenanceCheck:
    """Build a full provenance record for one evidence file."""
    received = server_received_at or datetime.utcnow()
    hash_match, hash_error = verify_client_server_hash(client_hash, server_hash)
    ts_score, ts_flags, latency = assess_capture_timestamp(client_captured_at, received)

    metadata_flags = _metadata_provenance_flags(file_metadata)
    all_flags = ([hash_error] if hash_error else []) + ts_flags + metadata_flags

    integrity_score = 1.0 if hash_match else 0.0
    provenance_score = round((integrity_score * 0.6) + (ts_score * 0.4), 3)

    sanitized_meta = _sanitize_metadata_for_storage(file_metadata)

    return ProvenanceCheck(
        evidence_id=evidence_id,
        filename=filename,
        server_hash=server_hash,
        client_hash_match=hash_match,
        client_captured_at=client_captured_at,
        server_received_at=received.isoformat(),
        upload_latency_seconds=latency,
        provenance_score=provenance_score,
        file_metadata=sanitized_meta,
        flags=all_flags,
    )


def _metadata_provenance_flags(metadata: Dict[str, Any]) -> List[str]:
    """Flag suspicious metadata without exposing values on the certificate."""
    flags: List[str] = []
    if metadata.get("error"):
        flags.append(f"Metadata extraction failed: {metadata['error']}")

    creator = (metadata.get("creator") or metadata.get("producer") or "").lower()
    if any(tool in creator for tool in ("canva", "fake", "generator", "online converter")):
        flags.append("Document metadata suggests non-standard authoring tool")

    if metadata.get("format") == "email_text" and not metadata.get("message_id_present"):
        flags.append("Email chain missing Message-ID header — weaker authenticity signal")

    if metadata.get("modification_date") and metadata.get("creation_date"):
        if metadata["modification_date"] != metadata["creation_date"]:
            flags.append("PDF shows modification after creation — review edit timeline")

    return flags


def _sanitize_metadata_for_storage(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Keep forensic signals, redact direct identifiers from stored metadata."""
    safe_keys = {
        "format",
        "page_count",
        "message_id_present",
        "parsed_date",
        "creation_date",
        "modification_date",
        "created",
        "modified",
        "revision",
        "byte_size",
        "error",
    }
    result: Dict[str, Any] = {}
    for key, value in metadata.items():
        if key in safe_keys:
            result[key] = value
        elif key in ("author", "creator", "producer", "from", "to", "title", "subject"):
            result[f"{key}_present"] = bool(value)
    return result


def aggregate_provenance_score(checks: List[ProvenanceCheck]) -> float:
    if not checks:
        return 0.5
    return round(sum(c.provenance_score for c in checks) / len(checks), 3)
