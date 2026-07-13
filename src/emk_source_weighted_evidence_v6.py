"""
EMK Source-Weighted Evidence v6
================================

v6 upgrades the v5 evidence ledger by weighting evidence according to source type.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List
import csv

try:
    from emk_csv_screening_v4 import read_candidate_csv
    from emk_material_screening_v3 import ScreeningResult, screen_candidates
    from emk_evidence_weighted_screening_v5 import EvidenceEntry, read_evidence_csv
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from emk_csv_screening_v4 import read_candidate_csv
    from emk_material_screening_v3 import ScreeningResult, screen_candidates
    from emk_evidence_weighted_screening_v5 import EvidenceEntry, read_evidence_csv

SOURCE_TYPE_WEIGHTS: Dict[str, float] = {
    "primary_paper": 1.00,
    "database": 0.95,
    "review_paper": 0.88,
    "benchmark": 0.82,
    "control": 0.78,
    "candidate_csv": 0.62,
    "proxy": 0.58,
    "model_inference": 0.52,
    "placeholder": 0.35,
    "manual_note": 0.30,
    "unknown": 0.25,
}

@dataclass
class SourceWeightedEvidenceSummary:
    material: str
    evidence_count: int
    raw_mean_confidence: float
    source_weighted_confidence: float
    coverage_score: float
    evidence_strength: float
    strongest_source_type: str
    source_weighted_label: str

@dataclass
class SourceWeightedScreeningResult:
    screening: ScreeningResult
    evidence: SourceWeightedEvidenceSummary
    source_weighted_priority: float
    source_weighted_label: str

def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def source_type_weight(source_type: str) -> float:
    key = (source_type or "unknown").strip().lower()
    return SOURCE_TYPE_WEIGHTS.get(key, SOURCE_TYPE_WEIGHTS["unknown"])

def summarize_source_weighted_evidence(entries: Iterable[EvidenceEntry]) -> Dict[str, SourceWeightedEvidenceSummary]:
    grouped: Dict[str, List[EvidenceEntry]] = {}
    for entry in entries:
        grouped.setdefault(entry.material, []).append(entry)
    summaries: Dict[str, SourceWeightedEvidenceSummary] = {}
    for material, rows in grouped.items():
        count = len(rows)
        raw_mean = sum(r.confidence for r in rows) / count if count else 0.0
        weighted = [r.confidence * source_type_weight(r.source_type) for r in rows]
        source_weighted_conf = sum(weighted) / count if count else 0.0
        coverage = min(1.0, count / 6.0)
        strength = _clip01(0.72 * source_weighted_conf + 0.28 * coverage)
        strongest = max(rows, key=lambda r: r.confidence * source_type_weight(r.source_type))
        if strength >= 0.72:
            label = "SOURCE_STRONG_EVIDENCE"
        elif strength >= 0.52:
            label = "SOURCE_MODERATE_EVIDENCE"
        elif strength > 0.0:
            label = "SOURCE_WEAK_EVIDENCE"
        else:
            label = "SOURCE_NO_EVIDENCE"
        summaries[material] = SourceWeightedEvidenceSummary(
            material, count, float(raw_mean), float(source_weighted_conf), float(coverage),
            float(strength), strongest.source_type, label
        )
    return summaries

def empty_summary(material: str) -> SourceWeightedEvidenceSummary:
    return SourceWeightedEvidenceSummary(material, 0, 0.0, 0.0, 0.0, 0.0, "none", "SOURCE_NO_EVIDENCE")

def classify_source_weighted(priority: float, evidence_strength: float) -> str:
    if priority >= 0.62 and evidence_strength >= 0.60:
        return "SOURCE_SUPPORTED_HIGH_PRIORITY"
    if priority >= 0.50 and evidence_strength >= 0.45:
        return "SOURCE_SUPPORTED_RESEARCH_TARGET"
    if priority >= 0.50 and evidence_strength < 0.45:
        return "PROMISING_BUT_SOURCE_WEAK"
    if evidence_strength >= 0.60:
        return "SOURCE_SUPPORTED_LOW_MODEL_SIGNAL"
    return "EARLY_STAGE_OR_LOW_SUPPORT"

def combine_source_weighted(screening_results: List[ScreeningResult], evidence_summaries: Dict[str, SourceWeightedEvidenceSummary]) -> List[SourceWeightedScreeningResult]:
    combined = []
    for result in screening_results:
        evidence = evidence_summaries.get(result.name, empty_summary(result.name))
        priority = _clip01(0.76 * result.research_priority_score + 0.24 * evidence.evidence_strength)
        combined.append(SourceWeightedScreeningResult(
            result, evidence, priority, classify_source_weighted(priority, evidence.evidence_strength)
        ))
    return sorted(combined, key=lambda r: r.source_weighted_priority, reverse=True)

def write_source_weighted_csv(results: List[SourceWeightedScreeningResult], output_csv: str | Path) -> None:
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for rank, result in enumerate(results, start=1):
        s, e = result.screening, result.evidence
        rows.append({
            "rank": rank, "name": s.name, "family": s.family,
            "source_weighted_label": result.source_weighted_label,
            "source_weighted_priority": result.source_weighted_priority,
            "model_priority_score": s.research_priority_score,
            "evidence_strength": e.evidence_strength,
            "evidence_count": e.evidence_count,
            "raw_mean_confidence": e.raw_mean_confidence,
            "source_weighted_confidence": e.source_weighted_confidence,
            "coverage_score": e.coverage_score,
            "strongest_source_type": e.strongest_source_type,
            "source_evidence_label": e.source_weighted_label,
            "thermoelectric_score": s.thermoelectric_score,
            "nonreciprocal_score": s.nonreciprocal_score,
            "defect_activity_score": s.defect_activity_score,
            "phase_risk_score": s.phase_risk_score,
            "stability_score": s.stability_score,
            "lambda_curvature": s.response.lambda_curvature,
            "reciprocity_gap": s.response.reciprocity_gap,
            "model_rank_label": s.rank_label,
            "response_label": s.response.response_label,
            "notes": s.notes,
        })
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def run_source_weighted_screening(candidate_csv: str | Path = "data/candidate_materials_v4.csv", evidence_csv: str | Path = "data/material_evidence_v5.csv", output_csv: str | Path = "outputs/source_weighted_screening_v6.csv") -> List[SourceWeightedScreeningResult]:
    candidates = read_candidate_csv(candidate_csv)
    screening = screen_candidates(candidates)
    entries = read_evidence_csv(evidence_csv)
    summaries = summarize_source_weighted_evidence(entries)
    results = combine_source_weighted(screening, summaries)
    write_source_weighted_csv(results, output_csv)
    return results

if __name__ == "__main__":
    results = run_source_weighted_screening()
    for i, result in enumerate(results, start=1):
        print(i, result.screening.name, round(result.source_weighted_priority, 4), result.source_weighted_label)
