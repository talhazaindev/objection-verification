import json
import logging
import os
from datetime import datetime

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import (
    CertificatePublicResponse,
    EvidenceFile,
    ReliabilityTier,
    VerificationAnalysis,
    VerificationResponse,
)
from app.services.ai_analyzer import (
    analyze_corroboration,
    analyze_evidence_consistency,
    assess_plausibility,
)
from app.services.anomaly_detector import detect_anomalies
from app.services.certificate_generator import generate_attribution, generate_certificate
from app.services.evidence_processor import (
    detect_evidence_type,
    detect_mime_type,
    extract_text_from_file,
)
from app.services.hash_engine import compute_file_hash
from app.services.metadata_forensics import extract_file_metadata
from app.services.provenance_engine import aggregate_provenance_score, build_provenance_check
from app.utils.privacy_filter import sanitize_text

router = APIRouter(prefix="/api/verify", tags=["verification"])
logger = logging.getLogger(__name__)


def _parse_provenance_map(provenance_json: str) -> dict:
    try:
        items = json.loads(provenance_json or "[]")
        return {
            item["filename"]: item
            for item in items
            if isinstance(item, dict) and "filename" in item
        }
    except (json.JSONDecodeError, TypeError):
        return {}


@router.post("/", response_model=VerificationResponse)
async def verify_evidence_package(
    files: list[UploadFile] = File(...),
    provenance: str = Form("[]"),
):
    """
    Main endpoint: Accept evidence files, verify, analyze, return certificate + attribution.
    Optional `provenance` JSON: [{filename, client_hash, captured_at}, ...]
    """
    if not os.getenv("GROQ_API_KEY"):
        logger.warning("Verification rejected: GROQ_API_KEY not configured")
        raise HTTPException(
            status_code=503,
            detail="Groq API key not configured. Set GROQ_API_KEY in Railway Variables.",
        )

    logger.info("Verification started for %d file(s)", len(files))

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per package")

    try:
        provenance_map = _parse_provenance_map(provenance)
        server_received_at = datetime.utcnow()
        evidence_files: list[EvidenceFile] = []
        provenance_checks = []
        anomaly_flags = []
        pre_llm_red_flags: list[str] = []

        for file in files:
            content = await file.read()
            filename = file.filename or "unknown"
            content_hash = compute_file_hash(content)
            mime = detect_mime_type(content, filename)
            ev_type = detect_evidence_type(filename, content, mime)
            raw_text = extract_text_from_file(filename, content, mime)

            file_metadata = extract_file_metadata(filename, content, mime, raw_text)
            client_prov = provenance_map.get(filename, {})
            sanitized_text = sanitize_text(raw_text)
            ef = EvidenceFile(
                filename=filename,
                evidence_type=ev_type,
                content_hash=content_hash,
                file_size=len(content),
                mime_type=mime,
                extracted_text=sanitized_text,
                metadata={
                    "original_filename": filename,
                    "forensics_format": file_metadata.get("format"),
                },
            )

            prov_check = build_provenance_check(
                evidence_id=ef.id,
                filename=filename,
                server_hash=content_hash,
                client_hash=client_prov.get("client_hash"),
                client_captured_at=client_prov.get("captured_at"),
                file_metadata=file_metadata,
                server_received_at=server_received_at,
            )
            provenance_checks.append(prov_check)
            pre_llm_red_flags.extend(prov_check.flags)

            file_anomalies = detect_anomalies(ef.id, ev_type, raw_text, file_metadata)
            anomaly_flags.extend(file_anomalies)
            for anomaly in file_anomalies:
                if anomaly.severity in ("medium", "high"):
                    pre_llm_red_flags.append(anomaly.description)

            evidence_files.append(ef)

        consistency_checks = await analyze_evidence_consistency(evidence_files)
        corroboration_results = await analyze_corroboration(evidence_files)
        plausibility = await assess_plausibility(
            evidence_files, consistency_checks, corroboration_results
        )

        avg_consistency = (
            sum(c.consistency_score for c in consistency_checks) / len(consistency_checks)
            if consistency_checks
            else 0
        )
        avg_corroboration = (
            sum(c.confidence for c in corroboration_results) / len(corroboration_results)
            if corroboration_results
            else 0
        )
        provenance_score = aggregate_provenance_score(provenance_checks)

        all_red_flags = pre_llm_red_flags + plausibility.get("red_flags", [])
        key_findings = plausibility.get("key_findings", [])
        if provenance_score >= 0.85:
            key_findings = [
                f"Strong provenance signals (score: {provenance_score:.0%})",
                *key_findings,
            ]
        if anomaly_flags:
            key_findings.append(
                f"Pre-LLM anomaly scan flagged {len(anomaly_flags)} item(s) for review"
            )

        analysis = VerificationAnalysis(
            evidence_files=evidence_files,
            provenance_checks=provenance_checks,
            anomaly_flags=anomaly_flags,
            consistency_checks=consistency_checks,
            corroboration_results=corroboration_results,
            plausibility_score=plausibility["plausibility_score"],
            reliability_tier=ReliabilityTier.INDETERMINATE,
            key_findings=key_findings,
            red_flags=all_red_flags,
            confidence_breakdown={
                "plausibility": plausibility["plausibility_score"],
                "consistency": avg_consistency,
                "corroboration": avg_corroboration,
                "provenance": provenance_score,
            },
        )

        certificate = generate_certificate(evidence_files, analysis)
        attribution = generate_attribution(certificate)
        analysis.reliability_tier = certificate.reliability_tier

        from app.main import certificate_store

        certificate_store[certificate.certificate_id] = {
            "certificate": certificate,
            "attribution": attribution,
        }

        logger.info(
            "Verification complete: certificate_id=%s tier=%s",
            certificate.certificate_id,
            certificate.reliability_tier,
        )

        return VerificationResponse(
            certificate=certificate,
            attribution=attribution,
            analysis=analysis,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Verification failed")
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {exc}",
        ) from exc


@router.get("/certificate/{certificate_id}", response_model=CertificatePublicResponse)
async def get_certificate(certificate_id: str):
    """Public endpoint to retrieve a certificate by ID."""
    from app.main import certificate_store

    if certificate_id not in certificate_store:
        raise HTTPException(status_code=404, detail="Certificate not found")

    stored = certificate_store[certificate_id]
    return CertificatePublicResponse(
        certificate=stored["certificate"],
        attribution=stored["attribution"],
    )
