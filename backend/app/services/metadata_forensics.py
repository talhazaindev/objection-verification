import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from io import BytesIO
from typing import Any, Dict, List, Optional


def extract_pdf_metadata(content: bytes) -> Dict[str, Any]:
    """Extract PDF document metadata for provenance forensics."""
    try:
        import PyPDF2

        reader = PyPDF2.PdfReader(BytesIO(content))
        meta = reader.metadata or {}
        return {
            "format": "pdf",
            "title": _safe_str(meta.get("/Title")),
            "author": _safe_str(meta.get("/Author")),
            "creator": _safe_str(meta.get("/Creator")),
            "producer": _safe_str(meta.get("/Producer")),
            "creation_date": _safe_str(meta.get("/CreationDate")),
            "modification_date": _safe_str(meta.get("/ModDate")),
            "page_count": len(reader.pages),
        }
    except Exception as exc:
        return {"format": "pdf", "error": str(exc)}


def extract_docx_metadata(content: bytes) -> Dict[str, Any]:
    """Extract DOCX core properties."""
    try:
        from docx import Document

        doc = Document(BytesIO(content))
        props = doc.core_properties
        return {
            "format": "docx",
            "author": _safe_str(props.author),
            "created": _iso_or_str(props.created),
            "modified": _iso_or_str(props.modified),
            "revision": props.revision,
            "title": _safe_str(props.title),
        }
    except Exception as exc:
        return {"format": "docx", "error": str(exc)}


def extract_email_headers(text: str) -> Dict[str, Any]:
    """Parse email-like headers from plain-text email chains."""
    headers: Dict[str, Any] = {"format": "email_text"}
    patterns = {
        "from": r"^From:\s*(.+)$",
        "to": r"^To:\s*(.+)$",
        "date": r"^Date:\s*(.+)$",
        "subject": r"^Subject:\s*(.+)$",
        "message_id": r"^Message-ID:\s*(.+)$",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            headers[key] = match.group(1).strip()

    if "date" in headers:
        try:
            headers["parsed_date"] = parsedate_to_datetime(headers["date"]).isoformat()
        except Exception:
            headers["parsed_date"] = None

    headers["message_id_present"] = bool(headers.get("message_id"))
    return headers


def extract_file_metadata(filename: str, content: bytes, mime_type: str, text: str) -> Dict[str, Any]:
    """Route metadata extraction by file type."""
    lower = filename.lower()
    if mime_type == "application/pdf" or lower.endswith(".pdf"):
        return extract_pdf_metadata(content)
    if lower.endswith(".docx") or "wordprocessingml" in mime_type:
        return extract_docx_metadata(content)
    if any(k in lower for k in ["email", "chain", "correspondence"]) or "from:" in text[:2000].lower():
        return extract_email_headers(text[:8000])
    return {"format": "generic", "byte_size": len(content)}


def _safe_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    return str(value).strip() or None


def _iso_or_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
