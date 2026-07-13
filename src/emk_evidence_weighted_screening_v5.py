"""
EMK Evidence-Weighted Screening v5
==================================

v5 adds an evidence ledger to the v4 CSV screening workflow.

v4 asks:
    What does the geometric screening model rank highest?

v5 asks:
    Which ranked candidates also have traceable evidence support?

This is a necessary step toward a defensible research artifact. Because without
evidence, a score is just a number wearing a lab coat.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List
import csv

try:
    from emk_csv_screening_v4 import read_candidate_csv
    from emk_material_screening_v3 import ScreeningResult, screen_candidates
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from emk_csv_screening_v4 import read_candidate_csv
    from emk_material_screening_v3 import ScreeningResult, screen_candidates

@dataclass
class EvidenceEntry:
    material: str
    property: str
    value: str
    unit: str
    source_type: str
    source: str
    confidence: float
    notes: str

@dataclass
class EvidenceSummary:
    material: str
    evidence_count: int
    mean_confidence: float
    max_confidence: float
    evidence_weight: float
    evidence_label: str

@dataclass
class EvidenceWeightedResult:
    screening: ScreeningResult
    evidence: EvidenceSummary
    evidence_weighted_priority: float
    evidence_weighted_label: str

REQUIRED_EVIDENCE_COLUMNS = [
    "material", "property", "value", "unit", "source_type", "source",
    "confidence", "notes",
]

def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def read_evidence_csv(path: str | Path) -> List[EvidenceEntry]:
    evidence_path = Path(path)
    if not evidence_path.exists():
        raise FileNotFoundError(f"Evidence CSV not found: {evidence_path}")
    entries: List[EvidenceEntry] = []
    with evidence_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Evidence CSV has no header row.")
        missing = [c for c in REQUIRED_EVIDENCE_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise ValueError(f"Evidence CSV missing columns: {missing}")
        for row in reader:
            material = row.get("material", "").strip()
            if not material:
                continue
            try:
                confidence = float(row.get("confidence", "0"))
            except ValueError as exc:
                raise ValueError(f"Invalid confidence value in row: {row}") from exc
            entries.append(EvidenceEntry(
                material=material,
                property=row.get("property", "").strip(),
                value=row.get("value", "").strip(),
                unit=row.get("unit", "").strip(),
                source_type=row.get("source_type", "").strip(),
                source=row.get("source", "").strip(),
                confidence=_clip01(confidence),
                notes=row.get("notes", "").strip(),
            ))
    return entries

def summarize_evidence(entries: Iterable[EvidenceEntry]) -> Dict[str, EvidenceSummary]:
    grouped: Dict[str, List[EvidenceEntry]] = {}
    for e in entries:
        grouped.setdefault(e.material, []).append(e)
    summaries: Dict[str, EvidenceSummary] = {}
    for material, rows in grouped.items():
        confidences = [r.confidence for r in rows]
        count = len(rows)
        mean_conf = sum(confidences) / count if count else 0.0
        max_conf = max(confidences) if confidences else 0.0
        coverage = min(1.0, count / 5.0)
        evidence_weight = _clip01(0.65 * mean_conf + 0.35 * coverage)
        if evidence_weight >= 0.70:
            label = "STRONG_EVIDENCE_SUPPORT"
        elif evidence_weight >= 0.50:
            label = "MODERATE_EVIDENCE_SUPPORT"
        elif evidence_weight > 0.0:
            label = "WEAK_EVIDENCE_SUPPORT"
        else:
            label = "NO_EVIDENCE_SUPPORT"
        summaries[material] = EvidenceSummary(
            material=material,
            evidence_count=count,
            mean_confidence=float(mean_conf),
            max_confidence=float(max_conf),
            evidence_weight=float(evidence_weight),
            evidence_label=label,
        )
    return summaries

def empty_evidence(material: str) -> EvidenceSummary:
    return EvidenceSummary(material, 0, 0.0, 0.0, 0.0, "NO_EVIDENCE_SUPPORT")

def weighted_label(priority: float, evidence: EvidenceSummary) -> str:
    if priority >= 0.62 and evidence.evidence_weight >= 0.60:
        return "SUPPORTED_HIGH_PRIORITY"
    if priority >= 0.50 and evidence.evidence_weight >= 0.50:
        return "SUPPORTED_RESEARCH_TARGET"
    if priority >= 0.50 and evidence.evidence_weight < 0.50:
        return "PROMISING_NEEDS_EVIDENCE"
    if evidence.evidence_weight >= 0.65:
        return "EVIDENCE_SUPPORTED_BUT_LOW_MODEL_SIGNAL"
    return "LOW_SUPPORT_OR_EARLY_STAGE"

def combine_screening_with_evidence(
    screening_results: List[ScreeningResult],
    evidence_summaries: Dict[str, EvidenceSummary],
) -> List[EvidenceWeightedResult]:
    combined: List[EvidenceWeightedResult] = []
    for result in screening_results:
        ev = evidence_summaries.get(result.name, empty_evidence(result.name))
        weighted_priority = _clip01(0.72 * result.research_priority_score + 0.28 * ev.evidence_weight)
        combined.append(EvidenceWeightedResult(
            screening=result,
            evidence=ev,
            evidence_weighted_priority=weighted_priority,
            evidence_weighted_label=weighted_label(weighted_priority, ev),
        ))
    return sorted(combined, key=lambda r: r.evidence_weighted_priority, reverse=True)

def write_weighted_csv(results: List[EvidenceWeightedResult], output_csv: str | Path) -> None:
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, r in enumerate(results, start=1):
        s, e = r.screening, r.evidence
        rows.append({
            "rank": i,
            "name": s.name,
            "family": s.family,
            "evidence_weighted_label": r.evidence_weighted_label,
            "evidence_weighted_priority": r.evidence_weighted_priority,
            "model_priority_score": s.research_priority_score,
            "evidence_weight": e.evidence_weight,
            "evidence_label": e.evidence_label,
            "evidence_count": e.evidence_count,
            "mean_confidence": e.mean_confidence,
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
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

def run_evidence_weighted_screening(
    candidate_csv: str | Path = "data/candidate_materials_v4.csv",
    evidence_csv: str | Path = "data/material_evidence_v5.csv",
    output_csv: str | Path = "outputs/evidence_weighted_screening_v5.csv",
) -> List[EvidenceWeightedResult]:
    candidates = read_candidate_csv(candidate_csv)
    screening_results = screen_candidates(candidates)
    evidence_entries = read_evidence_csv(evidence_csv)
    summaries = summarize_evidence(evidence_entries)
    weighted = combine_screening_with_evidence(screening_results, summaries)
    write_weighted_csv(weighted, output_csv)
    return weighted

def print_results(results: List[EvidenceWeightedResult]) -> None:
    print("=" * 118)
    print("EMK Evidence-Weighted Screening v5")
    print("=" * 118)
    for i, r in enumerate(results, start=1):
        s, e = r.screening, r.evidence
        print(
            f"{i:02d}. {s.name:30s} | {s.family:26s} | "
            f"weighted={r.evidence_weighted_priority:.4f} | "
            f"model={s.research_priority_score:.4f} | "
            f"evidence={e.evidence_weight:.4f} | n={e.evidence_count} | "
            f"{r.evidence_weighted_label}"
        )

def main() -> None:
    results = run_evidence_weighted_screening()
    print_results(results)
    print("\nSaved: outputs/evidence_weighted_screening_v5.csv")

if __name__ == "__main__":
    main()
