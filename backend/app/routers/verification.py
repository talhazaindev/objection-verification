import os

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import (
    CertificatePublicResponse,
    ReliabilityTier,
    VerificationAnalysis,
    VerificationResponse,
)
from app.services.ai_analyzer import (
    analyze_corroboration,
    analyze_evidence_consistency,
    assess_plausibility,
)
from app.services.certificate_generator import generate_attribution, generate_certificate
from app.services.evidence_processor import (
    detect_evidence_type,
    detect_mime_type,
    extract_text_from_file,
)
from app.services.hash_engine import compute_file_hash
from app.utils.privacy_filter import sanitize_text

router = APIRouter(prefix="/api/verify", tags=["verification"])


@router.post("/", response_model=VerificationResponse)
async def verify_evidence_package(files: list[UploadFile] = File(...)):
    """
    Main endpoint: Accept evidence files, verify, analyze, return certificate + attribution.
    """
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="Groq API key not configured. Set GROQ_API_KEY in backend/.env",
        )

    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per package")

    try:
        evidence_files = []
        for file in files:
            content = await file.read()
            content_hash = compute_file_hash(content)
            mime = detect_mime_type(content, file.filename or "unknown")
            ev_type = detect_evidence_type(file.filename or "unknown", content, mime)
            raw_text = extract_text_from_file(file.filename or "unknown", content, mime)
            sanitized_text = sanitize_text(raw_text)

            from app.models.schemas import EvidenceFile

            evidence_files.append(
                EvidenceFile(
                    filename=file.filename or "unknown",
                    evidence_type=ev_type,
                    content_hash=content_hash,
                    file_size=len(content),
                    mime_type=mime,
                    extracted_text=sanitized_text,
                    metadata={"original_filename": file.filename or "unknown"},
                )
            )

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

        analysis = VerificationAnalysis(
            evidence_files=evidence_files,
            consistency_checks=consistency_checks,
            corroboration_results=corroboration_results,
            plausibility_score=plausibility["plausibility_score"],
            reliability_tier=ReliabilityTier.INDETERMINATE,
            key_findings=plausibility["key_findings"],
            red_flags=plausibility["red_flags"],
            confidence_breakdown={
                "plausibility": plausibility["plausibility_score"],
                "consistency": avg_consistency,
                "corroboration": avg_corroboration,
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

        return VerificationResponse(
            certificate=certificate,
            attribution=attribution,
            analysis=analysis,
        )
    except HTTPException:
        raise
    except Exception as exc:
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
