export type ReliabilityTier = "high" | "medium" | "low" | "indeterminate";

export type EvidenceType =
  | "intake_notes"
  | "email_chain"
  | "audio_recording"
  | "data_memo"
  | "personal_notes"
  | "other";

export interface EvidenceBreakdownItem {
  evidence_type: EvidenceType;
  content_hash: string;
  file_size_kb: number;
  verified_intact: boolean;
  client_hash_verified?: boolean;
  provenance_score?: number;
  metadata_format?: string;
}

export interface ProvenanceCheck {
  evidence_id: string;
  filename: string;
  server_hash: string;
  client_hash_match: boolean;
  client_captured_at?: string;
  server_received_at: string;
  upload_latency_seconds?: number;
  provenance_score: number;
  file_metadata: Record<string, unknown>;
  flags: string[];
}

export interface AnomalyFlag {
  evidence_id: string;
  category: string;
  severity: "low" | "medium" | "high";
  description: string;
}

export interface Certificate {
  certificate_id: string;
  timestamp: string;
  evidence_count: number;
  reliability_tier: ReliabilityTier;
  overall_confidence: number;
  evidence_breakdown: EvidenceBreakdownItem[];
  verification_summary: string;
  hash_chain: string;
}

export interface AttributionLanguage {
  short_form: string;
  long_form: string;
  legal_disclaimer: string;
  certificate_reference: string;
}

export interface ConsistencyCheck {
  evidence_pair: [string, string];
  consistency_score: number;
  conflicts: string[];
  agreements: string[];
}

export interface CorroborationResult {
  claim: string;
  supporting_evidence_ids: string[];
  confidence: number;
  contradiction_found: boolean;
}

export interface VerificationAnalysis {
  evidence_files: unknown[];
  provenance_checks: ProvenanceCheck[];
  anomaly_flags: AnomalyFlag[];
  consistency_checks: ConsistencyCheck[];
  corroboration_results: CorroborationResult[];
  plausibility_score: number;
  reliability_tier: ReliabilityTier;
  key_findings: string[];
  red_flags: string[];
  confidence_breakdown: Record<string, number>;
}

export interface VerificationResponse {
  certificate: Certificate;
  attribution: AttributionLanguage;
  analysis: VerificationAnalysis;
}

export interface CertificatePublicResponse {
  certificate: Certificate;
  attribution: AttributionLanguage;
}

export interface ApiError {
  detail: string;
}
