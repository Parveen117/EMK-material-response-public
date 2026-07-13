"""
EMK Material Screening v3
=========================

This module adds a candidate-screening layer over the v1 material response engine
and the v2 lattice Onsager engine.

The screening scores are not empirical truth. They are geometric research-priority
signals: a triage engine, not an oracle.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import csv
import math

try:
    from emk_lambda_material_response_v1 import MaterialState, MaterialResponse, evaluate_material
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from emk_lambda_material_response_v1 import MaterialState, MaterialResponse, evaluate_material


@dataclass
class CandidateMaterial:
    name: str
    family: str
    temperature_K: float
    electric_field: float
    temperature_gradient: float
    strain: float
    defect_density: float
    carrier_density: float
    ion_mobility: float
    symmetry_breaking: float
    notes: str = ""

    def to_state(self) -> MaterialState:
        return MaterialState(
            name=self.name,
            temperature_K=self.temperature_K,
            electric_field=self.electric_field,
            temperature_gradient=self.temperature_gradient,
            strain=self.strain,
            defect_density=self.defect_density,
            carrier_density=self.carrier_density,
            ion_mobility=self.ion_mobility,
            symmetry_breaking=self.symmetry_breaking,
        )


@dataclass
class ScreeningResult:
    name: str
    family: str
    response: MaterialResponse
    thermoelectric_score: float
    nonreciprocal_score: float
    defect_activity_score: float
    phase_risk_score: float
    stability_score: float
    research_priority_score: float
    rank_label: str
    notes: str


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def thermoelectric_score(candidate: CandidateMaterial, response: MaterialResponse) -> float:
    gradient = _clip01(abs(candidate.temperature_gradient))
    carrier = _clip01(candidate.carrier_density)
    bounded_curvature = math.exp(-abs(response.lambda_curvature - 0.28))
    stability = response.stability_score
    return _clip01(0.35 * gradient + 0.30 * carrier + 0.20 * bounded_curvature + 0.15 * stability)


def nonreciprocal_score(candidate: CandidateMaterial, response: MaterialResponse) -> float:
    gap = _clip01(response.reciprocity_gap / 0.35)
    symmetry = _clip01(candidate.symmetry_breaking)
    field = _clip01(abs(candidate.electric_field))
    curvature = _clip01(response.lambda_curvature / 0.70)
    return _clip01(0.35 * gap + 0.30 * symmetry + 0.20 * field + 0.15 * curvature)


def defect_activity_score(candidate: CandidateMaterial, response: MaterialResponse) -> float:
    defects = _clip01(candidate.defect_density)
    ion = _clip01(candidate.ion_mobility)
    curvature = _clip01(response.lambda_curvature / 0.70)
    gap = _clip01(response.reciprocity_gap / 0.35)
    return _clip01(0.35 * defects + 0.30 * ion + 0.20 * curvature + 0.15 * gap)


def phase_risk_score(candidate: CandidateMaterial, response: MaterialResponse) -> float:
    temperature_drive = _clip01((candidate.temperature_K - 300.0) / 700.0)
    strain = _clip01(abs(candidate.strain))
    defects = _clip01(candidate.defect_density)
    curvature = _clip01(response.lambda_curvature / 0.70)
    instability = 1.0 - response.stability_score
    return _clip01(0.25 * temperature_drive + 0.20 * strain + 0.20 * defects + 0.20 * curvature + 0.15 * instability)


def research_priority(thermo: float, nonreciprocal: float, defect: float, phase: float, stability: float) -> float:
    useful_instability = 1.0 - abs(stability - 0.62)
    return _clip01(0.28 * thermo + 0.28 * nonreciprocal + 0.20 * defect + 0.14 * phase + 0.10 * useful_instability)


def label_rank(result: ScreeningResult) -> str:
    if result.research_priority_score >= 0.62:
        return "HIGH_PRIORITY_CANDIDATE"
    if result.nonreciprocal_score >= 0.55:
        return "NONRECIPROCAL_TRANSPORT_TARGET"
    if result.thermoelectric_score >= 0.60:
        return "THERMOELECTRIC_SCREENING_TARGET"
    if result.defect_activity_score >= 0.55:
        return "DEFECT_ACTIVE_TARGET"
    if result.phase_risk_score >= 0.50:
        return "PHASE_SWITCHING_RISK_TARGET"
    return "LOW_TO_MODERATE_PRIORITY"


def screen_candidate(candidate: CandidateMaterial) -> ScreeningResult:
    response = evaluate_material(candidate.to_state())
    thermo = thermoelectric_score(candidate, response)
    nonrecip = nonreciprocal_score(candidate, response)
    defect = defect_activity_score(candidate, response)
    phase = phase_risk_score(candidate, response)
    stability = response.stability_score
    priority = research_priority(thermo, nonrecip, defect, phase, stability)
    provisional = ScreeningResult(candidate.name, candidate.family, response, thermo, nonrecip, defect, phase, stability, priority, "", candidate.notes)
    provisional.rank_label = label_rank(provisional)
    return provisional


def screen_candidates(candidates: Iterable[CandidateMaterial]) -> List[ScreeningResult]:
    return sorted([screen_candidate(c) for c in candidates], key=lambda r: r.research_priority_score, reverse=True)


def demo_candidates() -> List[CandidateMaterial]:
    return [
        CandidateMaterial("Si_reference", "semiconductor_reference", 300, 0.05, 0.05, 0.02, 0.01, 0.30, 0.05, 0.02, "Stable baseline reference."),
        CandidateMaterial("Bi2Te3_proxy", "thermoelectric", 360, 0.18, 0.55, 0.07, 0.08, 0.78, 0.10, 0.16, "Thermoelectric-style heat-charge coupling target."),
        CandidateMaterial("SnSe_proxy", "thermoelectric_low_dimensional", 520, 0.16, 0.62, 0.12, 0.12, 0.62, 0.15, 0.25, "Layered thermoelectric proxy with stronger anisotropy."),
        CandidateMaterial("MoS2_monolayer_proxy", "broken_symmetry_2D", 300, 0.35, 0.20, 0.15, 0.06, 0.55, 0.08, 0.55, "Broken-symmetry 2D transport target."),
        CandidateMaterial("WTe2_proxy", "topological_nonreciprocal", 280, 0.42, 0.25, 0.10, 0.07, 0.72, 0.06, 0.62, "Strong nonreciprocal/topological-style proxy."),
        CandidateMaterial("oxygen_vacancy_oxide_proxy", "defective_ion_conductor", 720, 0.28, 0.38, 0.18, 0.38, 0.26, 0.82, 0.28, "Oxygen-vacancy ion-conductor proxy."),
        CandidateMaterial("GST_phase_change_proxy", "phase_change", 610, 0.32, 0.42, 0.32, 0.30, 0.58, 0.45, 0.34, "Phase-change/pulse-switching proxy."),
        CandidateMaterial("strained_SiGe_proxy", "strained_semiconductor", 330, 0.16, 0.15, 0.28, 0.07, 0.48, 0.08, 0.18, "Strain-tuned semiconductor proxy."),
    ]


def write_screening_csv(results: List[ScreeningResult], output_csv: str) -> None:
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, r in enumerate(results, start=1):
        rows.append({
            "rank": i,
            "name": r.name,
            "family": r.family,
            "rank_label": r.rank_label,
            "research_priority_score": r.research_priority_score,
            "thermoelectric_score": r.thermoelectric_score,
            "nonreciprocal_score": r.nonreciprocal_score,
            "defect_activity_score": r.defect_activity_score,
            "phase_risk_score": r.phase_risk_score,
            "stability_score": r.stability_score,
            "lambda_curvature": r.response.lambda_curvature,
            "reciprocity_gap": r.response.reciprocity_gap,
            "response_label": r.response.response_label,
            "notes": r.notes,
        })
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_screening_demo(output_csv: str = "outputs/material_screening_v3_demo.csv") -> List[ScreeningResult]:
    results = screen_candidates(demo_candidates())
    write_screening_csv(results, output_csv)
    return results


if __name__ == "__main__":
    results = run_screening_demo()
    print("=" * 110)
    print("EMK Material Screening v3")
    print("=" * 110)
    print("Ranked candidate materials by geometric research-priority score")
    print("-" * 110)
    for i, r in enumerate(results, start=1):
        print(i, r.name, r.rank_label, round(r.research_priority_score, 5))
    print("\nSaved: outputs/material_screening_v3_demo.csv")