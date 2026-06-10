import json
import os
import re
from typing import Dict, List

from openai import AsyncOpenAI

from app.models.schemas import (
    ConsistencyCheck,
    CorroborationResult,
    EvidenceFile,
)

_client: AsyncOpenAI | None = None

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=GROQ_BASE_URL,
        )
    return _client


def _parse_json_response(content: str) -> dict:
    """Parse JSON from GPT response, stripping markdown fences if present."""
    text = content.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence_match:
        text = fence_match.group(1).strip()
    return json.loads(text)


async def analyze_evidence_consistency(
    evidence_files: List[EvidenceFile],
) -> List[ConsistencyCheck]:
    """Use AI to compare evidence files and identify consistencies/conflicts."""
    checks = []

    for i in range(len(evidence_files)):
        for j in range(i + 1, len(evidence_files)):
            file_a = evidence_files[i]
            file_b = evidence_files[j]

            text_a = file_a.extracted_text or ""
            text_b = file_b.extracted_text or ""

            prompt = f"""
            You are an expert forensic analyst evaluating evidence consistency.

            EVIDENCE A ({file_a.evidence_type.value}):
            {text_a[:4000]}

            EVIDENCE B ({file_b.evidence_type.value}):
            {text_b[:4000]}

            TASK:
            1. Identify all factual claims in both pieces of evidence
            2. Compare them for consistency
            3. List specific agreements (same facts stated)
            4. List specific conflicts (contradictory facts)
            5. Assign a consistency score from 0.0 to 1.0

            Respond ONLY in this JSON format:
            {{
                "consistency_score": float,
                "agreements": [string],
                "conflicts": [string]
            }}
            """

            response = await _get_client().chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a forensic evidence analyst. Respond only in valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=2000,
            )

            try:
                result = _parse_json_response(response.choices[0].message.content or "")
                checks.append(
                    ConsistencyCheck(
                        evidence_pair=(file_a.id, file_b.id),
                        consistency_score=result["consistency_score"],
                        conflicts=result["conflicts"],
                        agreements=result["agreements"],
                    )
                )
            except Exception as e:
                checks.append(
                    ConsistencyCheck(
                        evidence_pair=(file_a.id, file_b.id),
                        consistency_score=0.5,
                        conflicts=[f"Analysis error: {str(e)}"],
                        agreements=[],
                    )
                )

    return checks


async def analyze_corroboration(
    evidence_files: List[EvidenceFile],
) -> List[CorroborationResult]:
    """Identify claims supported by multiple independent evidence sources."""
    all_text = "\n\n---\n\n".join(
        [
            f"SOURCE {ef.id} ({ef.evidence_type.value}):\n{(ef.extracted_text or '')[:3000]}"
            for ef in evidence_files
        ]
    )

    prompt = f"""
    You are analyzing multiple pieces of evidence to find corroborated claims.

    {all_text}

    TASK:
    Identify claims that are supported by 2 or more independent evidence sources.
    For each corroborated claim:
    - State the claim clearly
    - List which source IDs support it
    - Rate confidence 0.0-1.0
    - Note if any source contradicts it

    Respond ONLY in this JSON format:
    {{
        "corroborated_claims": [
            {{
                "claim": string,
                "supporting_source_ids": [string],
                "confidence": float,
                "contradiction_found": bool
            }}
        ]
    }}
    """

    response = await _get_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a forensic evidence analyst. Respond only in valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=2500,
    )

    try:
        result = _parse_json_response(response.choices[0].message.content or "")
        return [
            CorroborationResult(
                claim=claim["claim"],
                supporting_evidence_ids=claim["supporting_source_ids"],
                confidence=claim["confidence"],
                contradiction_found=claim["contradiction_found"],
            )
            for claim in result["corroborated_claims"]
        ]
    except Exception:
        return []


async def assess_plausibility(
    evidence_files: List[EvidenceFile],
    consistency_checks: List[ConsistencyCheck],
    corroboration_results: List[CorroborationResult],
) -> Dict:
    """Assess overall plausibility of the evidence narrative."""
    narrative_summary = "\n".join(
        [
            f"- {ef.evidence_type.value}: {(ef.extracted_text or '')[:1000]}..."
            for ef in evidence_files
        ]
    )

    avg_consistency = (
        sum(c.consistency_score for c in consistency_checks) / len(consistency_checks)
        if consistency_checks
        else 0.5
    )
    corroboration_count = len(corroboration_results)
    avg_corroboration_confidence = (
        sum(c.confidence for c in corroboration_results) / len(corroboration_results)
        if corroboration_results
        else 0.5
    )

    prompt = f"""
    Assess the plausibility of this evidence narrative.

    EVIDENCE SUMMARY:
    {narrative_summary}

    METRICS:
    - Average consistency across evidence pairs: {avg_consistency:.2f}
    - Number of corroborated claims: {corroboration_count}
    - Average corroboration confidence: {avg_corroboration_confidence:.2f}

    TASK:
    1. Assign an overall plausibility score (0.0 to 1.0)
    2. List key findings that support or undermine plausibility
    3. List any red flags (gaps, inconsistencies, suspicious patterns)

    Respond ONLY in this JSON format:
    {{
        "plausibility_score": float,
        "key_findings": [string],
        "red_flags": [string]
    }}
    """

    response = await _get_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a forensic evidence analyst. Respond only in valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=1500,
    )

    try:
        return _parse_json_response(response.choices[0].message.content or "")
    except Exception as e:
        return {
            "plausibility_score": 0.5,
            "key_findings": ["Analysis failed, defaulting to neutral"],
            "red_flags": [f"Error: {str(e)}"],
        }
