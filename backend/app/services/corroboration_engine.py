from typing import List, Tuple

from app.models.schemas import ReliabilityTier


def calculate_reliability_tier(
    plausibility_score: float,
    consistency_score: float,
    corroboration_count: int,
    red_flags: List[str],
) -> Tuple[ReliabilityTier, float]:
    """Calculate final reliability tier based on weighted scoring."""
    w_plausibility = 0.35
    w_consistency = 0.30
    w_corroboration = 0.25
    w_red_flags = -0.10

    red_flag_penalty = min(len(red_flags) * abs(w_red_flags), 0.30)
    corroboration_normalized = min(corroboration_count / 5, 1.0)

    overall_score = (
        (plausibility_score * w_plausibility)
        + (consistency_score * w_consistency)
        + (corroboration_normalized * w_corroboration)
        - red_flag_penalty
    )

    overall_score = max(0.0, min(1.0, overall_score))

    if overall_score >= 0.85:
        return ReliabilityTier.HIGH, overall_score
    elif overall_score >= 0.60:
        return ReliabilityTier.MEDIUM, overall_score
    elif overall_score >= 0.40:
        return ReliabilityTier.LOW, overall_score
    else:
        return ReliabilityTier.INDETERMINATE, overall_score
