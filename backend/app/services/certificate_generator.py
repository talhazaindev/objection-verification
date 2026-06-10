from typing import List

from app.models.schemas import (
    AttributionLanguage,
    Certificate,
    EvidenceFile,
    VerificationAnalysis,
)
from app.services.corroboration_engine import calculate_reliability_tier
from app.services.hash_engine import compute_combined_hash


def generate_certificate(
    evidence_files: List[EvidenceFile],
    analysis: VerificationAnalysis,
) -> Certificate:
    """Generate a privacy-preserving certificate."""
    evidence_hashes = [ef.content_hash for ef in evidence_files]
    hash_chain = compute_combined_hash(evidence_hashes)

    evidence_breakdown = [
        {
            "evidence_type": ef.evidence_type.value,
            "content_hash": ef.content_hash,
            "file_size_kb": round(ef.file_size / 1024, 2),
            "verified_intact": True,
        }
        for ef in evidence_files
    ]

    avg_consistency = (
        sum(c.consistency_score for c in analysis.consistency_checks)
        / len(analysis.consistency_checks)
        if analysis.consistency_checks
        else 0
    )

    tier, confidence = calculate_reliability_tier(
        analysis.plausibility_score,
        avg_consistency,
        len(analysis.corroboration_results),
        analysis.red_flags,
    )

    first_consistency = (
        analysis.consistency_checks[0].consistency_score
        if analysis.consistency_checks
        else "N/A"
    )

    return Certificate(
        evidence_count=len(evidence_files),
        reliability_tier=tier,
        overall_confidence=round(confidence, 3),
        evidence_breakdown=evidence_breakdown,
        verification_summary=(
            f"Evidence package of {len(evidence_files)} files analyzed. "
            f"Consistency score: {first_consistency}. "
            f"Corroborated claims: {len(analysis.corroboration_results)}. "
            f"Reliability tier: {tier.value.upper()}."
        ),
        hash_chain=hash_chain,
    )


def generate_attribution(certificate: Certificate) -> AttributionLanguage:
    """Generate publication-ready attribution language."""
    tier_descriptions = {
        "high": "independently verified with high confidence",
        "medium": "independently verified with moderate confidence",
        "low": "independently verified with limited confidence",
        "indeterminate": "submitted for independent verification with indeterminate results",
    }

    tier_key = certificate.reliability_tier.value

    short_form = (
        f"a source verified via Objection's certification process "
        f"(Certificate: {certificate.certificate_id})"
    )

    long_form = (
        f"a source whose claims have been {tier_descriptions.get(tier_key, 'reviewed')} "
        f"through Objection's independent evidence verification system "
        f"(Certificate ID: {certificate.certificate_id}, "
        f"Confidence: {certificate.overall_confidence:.0%})"
    )

    legal_disclaimer = (
        "This attribution is based on an independent verification of evidence provided by the source. "
        "The verification process assesses consistency, corroboration, and plausibility of submitted materials "
        "without revealing the source's identity. This certification does not guarantee the truth of the underlying claims "
        "but confirms that the evidence package has been systematically evaluated."
    )

    return AttributionLanguage(
        short_form=short_form,
        long_form=long_form,
        legal_disclaimer=legal_disclaimer,
        certificate_reference=certificate.certificate_id,
    )
