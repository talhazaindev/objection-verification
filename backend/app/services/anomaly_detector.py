import re
import statistics
from typing import Any, Dict, List

from app.models.schemas import AnomalyFlag, EvidenceType


def detect_anomalies(
    evidence_id: str,
    evidence_type: EvidenceType,
    text: str,
    file_metadata: Dict[str, Any],
) -> List[AnomalyFlag]:
    """Run rule-based anomaly checks before LLM analysis."""
    anomalies: List[AnomalyFlag] = []
    anomalies.extend(_metadata_anomalies(evidence_id, file_metadata))
    if evidence_type == EvidenceType.DATA_MEMO or _looks_quantitative(text):
        anomalies.extend(_data_memo_anomalies(evidence_id, text))
    if evidence_type == EvidenceType.EMAIL_CHAIN:
        anomalies.extend(_email_content_anomalies(evidence_id, text, file_metadata))
    return anomalies


def _looks_quantitative(text: str) -> bool:
    numbers = re.findall(r"\b\d+\.?\d*\b", text)
    return len(numbers) >= 6


def _data_memo_anomalies(evidence_id: str, text: str) -> List[AnomalyFlag]:
    """Statistical heuristics on quantitative evidence."""
    anomalies: List[AnomalyFlag] = []
    numbers = [float(n) for n in re.findall(r"\b\d+\.\d+\b", text)]
    integers = [int(n) for n in re.findall(r"\b\d+\b", text)]

    if len(numbers) >= 5:
        try:
            stdev = statistics.stdev(numbers)
            mean = statistics.mean(numbers)
            if mean != 0 and stdev / abs(mean) < 0.01:
                anomalies.append(
                    AnomalyFlag(
                        evidence_id=evidence_id,
                        category="statistical",
                        severity="medium",
                        description="Decimal values show unusually low variance — possible copy-paste fabrication",
                    )
                )
        except statistics.StatisticsError:
            pass

        round_count = sum(1 for n in numbers if n == round(n, 1) or n == round(n))
        if len(numbers) >= 8 and round_count / len(numbers) > 0.85:
            anomalies.append(
                AnomalyFlag(
                    evidence_id=evidence_id,
                    category="statistical",
                    severity="low",
                    description="High proportion of round numeric values in data memo",
                )
            )

    if integers:
        ending_in_zero = sum(1 for n in integers if n % 10 == 0 and n > 10)
        if len(integers) >= 10 and ending_in_zero / len(integers) > 0.7:
            anomalies.append(
                AnomalyFlag(
                    evidence_id=evidence_id,
                    category="statistical",
                    severity="low",
                    description="Many integers end in zero — review for fabricated rounding",
                )
            )

    percent_claims = re.findall(r"(\d+(?:\.\d+)?)\s*%", text)
    for pct in percent_claims:
        if float(pct) > 100:
            anomalies.append(
                AnomalyFlag(
                    evidence_id=evidence_id,
                    category="statistical",
                    severity="high",
                    description=f"Impossible percentage value detected: {pct}%",
                )
            )

    duplicate_lines = _duplicate_substantive_lines(text)
    if duplicate_lines >= 3:
        anomalies.append(
            AnomalyFlag(
                evidence_id=evidence_id,
                category="statistical",
                severity="medium",
                description=f"{duplicate_lines} duplicate substantive lines — possible template reuse",
            )
        )

    return anomalies


def _metadata_anomalies(evidence_id: str, metadata: Dict[str, Any]) -> List[AnomalyFlag]:
    anomalies: List[AnomalyFlag] = []
    fmt = metadata.get("format")

    if fmt == "pdf" and metadata.get("page_count") == 0:
        anomalies.append(
            AnomalyFlag(
                evidence_id=evidence_id,
                category="metadata",
                severity="high",
                description="PDF has zero extractable pages",
            )
        )

    if fmt == "pdf" and not any(metadata.get(k) for k in ("creation_date", "modification_date")):
        anomalies.append(
            AnomalyFlag(
                evidence_id=evidence_id,
                category="metadata",
                severity="medium",
                description="PDF missing creation/modification dates in metadata",
            )
        )

    if fmt == "email_text" and not metadata.get("message_id_present"):
        anomalies.append(
            AnomalyFlag(
                evidence_id=evidence_id,
                category="metadata",
                severity="medium",
                description="Email evidence lacks Message-ID — cannot verify message authenticity",
            )
        )

    return anomalies


def _email_content_anomalies(
    evidence_id: str, text: str, metadata: Dict[str, Any]
) -> List[AnomalyFlag]:
    anomalies: List[AnomalyFlag] = []
    if not re.search(r"^From:\s", text, re.MULTILINE | re.IGNORECASE):
        anomalies.append(
            AnomalyFlag(
                evidence_id=evidence_id,
                category="metadata",
                severity="medium",
                description="Email chain missing From: header block",
            )
        )
    if metadata.get("parsed_date") is None and re.search(r"^Date:\s", text, re.MULTILINE | re.IGNORECASE):
        anomalies.append(
            AnomalyFlag(
                evidence_id=evidence_id,
                category="metadata",
                severity="low",
                description="Email Date header present but could not be parsed",
            )
        )
    return anomalies


def _duplicate_substantive_lines(text: str) -> int:
    lines = [ln.strip().lower() for ln in text.splitlines() if len(ln.strip()) > 40]
    if not lines:
        return 0
    return len(lines) - len(set(lines))
