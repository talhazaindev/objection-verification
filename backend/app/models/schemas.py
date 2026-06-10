import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    INTAKE_NOTES = "intake_notes"
    EMAIL_CHAIN = "email_chain"
    AUDIO_RECORDING = "audio_recording"
    DATA_MEMO = "data_memo"
    PERSONAL_NOTES = "personal_notes"
    OTHER = "other"


class ReliabilityTier(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INDETERMINATE = "indeterminate"


class EvidenceFile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    evidence_type: EvidenceType
    content_hash: str
    file_size: int
    mime_type: str
    extracted_text: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)


class ConsistencyCheck(BaseModel):
    evidence_pair: tuple[str, str]
    consistency_score: float
    conflicts: List[str]
    agreements: List[str]


class CorroborationResult(BaseModel):
    claim: str
    supporting_evidence_ids: List[str]
    confidence: float
    contradiction_found: bool


class ProvenanceCheck(BaseModel):
    evidence_id: str
    filename: str
    server_hash: str
    client_hash_match: bool
    client_captured_at: Optional[str] = None
    server_received_at: str
    upload_latency_seconds: Optional[float] = None
    provenance_score: float
    file_metadata: Dict = Field(default_factory=dict)
    flags: List[str] = Field(default_factory=list)


class AnomalyFlag(BaseModel):
    evidence_id: str
    category: str  # statistical | metadata
    severity: str  # low | medium | high
    description: str


class VerificationAnalysis(BaseModel):
    evidence_files: List[EvidenceFile]
    provenance_checks: List[ProvenanceCheck] = Field(default_factory=list)
    anomaly_flags: List[AnomalyFlag] = Field(default_factory=list)
    consistency_checks: List[ConsistencyCheck]
    corroboration_results: List[CorroborationResult]
    plausibility_score: float
    reliability_tier: ReliabilityTier
    key_findings: List[str]
    red_flags: List[str]
    confidence_breakdown: Dict[str, float]


class Certificate(BaseModel):
    certificate_id: str = Field(
        default_factory=lambda: f"OBJ-{uuid.uuid4().hex[:12].upper()}"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    evidence_count: int
    reliability_tier: ReliabilityTier
    overall_confidence: float
    evidence_breakdown: List[Dict]
    verification_summary: str
    hash_chain: str


class AttributionLanguage(BaseModel):
    short_form: str
    long_form: str
    legal_disclaimer: str
    certificate_reference: str


class VerificationResponse(BaseModel):
    certificate: Certificate
    attribution: AttributionLanguage
    analysis: VerificationAnalysis


class CertificatePublicResponse(BaseModel):
    certificate: Certificate
    attribution: AttributionLanguage
