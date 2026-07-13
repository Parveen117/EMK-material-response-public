"""EMK Candidate Audit Report v7."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List
import csv
import textwrap

try:
    from emk_source_weighted_evidence_v6 import SourceWeightedScreeningResult, run_source_weighted_screening
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from emk_source_weighted_evidence_v6 import SourceWeightedScreeningResult, run_source_weighted_screening

@dataclass
class CandidateAudit:
    rank: int
    name: str
    family: str
    source_weighted_priority: float
    model_priority_score: float
    evidence_strength: float
    strongest_signal: str
    warning_flags: List[str]
    missing_evidence: List[str]
    next_action: str
    audit_text: str

def strongest_functional_signal(result: SourceWeightedScreeningResult) -> str:
    s = result.screening
    scores = {
        "thermoelectric": s.thermoelectric_score,
        "nonreciprocal": s.nonreciprocal_score,
        "defect_activity": s.defect_activity_score,
        "phase_risk": s.phase_risk_score,
    }
    name, value = max(scores.items(), key=lambda item: item[1])
    return f"{name}:{value:.4f}"

def warning_flags(result: SourceWeightedScreeningResult) -> List[str]:
    s, e = result.screening, result.evidence
    flags: List[str] = []
    if e.evidence_strength < 0.35: flags.append("weak_source_weighted_evidence")
    if e.evidence_count < 3: flags.append("low_evidence_coverage")
    if s.response.reciprocity_gap > 0.25 and e.evidence_strength < 0.45: flags.append("high_model_gap_needs_external_support")
    if s.phase_risk_score > 0.45: flags.append("phase_or_switching_risk")
    if s.defect_activity_score > 0.55: flags.append("defect_dominated_signal")
    if s.stability_score < 0.45: flags.append("low_stability_score")
    if result.source_weighted_priority >= 0.50 and e.evidence_strength < 0.45: flags.append("promising_but_under_evidenced")
    return flags or ["no_major_warning_flags"]

def missing_evidence(result: SourceWeightedScreeningResult) -> List[str]:
    s, e = result.screening, result.evidence
    missing: List[str] = []
    if e.evidence_count < 3: missing.append("add_at_least_three_material_specific_evidence_rows")
    if e.strongest_source_type in {"placeholder", "manual_note", "unknown", "model_inference"}: missing.append("replace_placeholder_or_model_inference_with_external_source")
    if s.thermoelectric_score > 0.55: missing.append("add_heat_charge_transport_metric")
    if s.nonreciprocal_score > 0.55: missing.append("add_symmetry_or_directional_transport_evidence")
    if s.defect_activity_score > 0.50: missing.append("add_defect_mobility_or_defect_density_evidence")
    if s.phase_risk_score > 0.40: missing.append("add_switching_or_phase_stability_evidence")
    return missing or ["evidence_basis_currently_acceptable_for_seed_stage"]

def next_action(result: SourceWeightedScreeningResult) -> str:
    s, e = result.screening, result.evidence
    if e.evidence_strength < 0.35 and s.research_priority_score >= 0.50:
        return "Prioritize literature/data collection before upgrading claims."
    if s.nonreciprocal_score >= max(s.thermoelectric_score, s.defect_activity_score, s.phase_risk_score):
        return "Search for directional transport, symmetry-breaking, or nonreciprocal response evidence."
    if s.thermoelectric_score >= max(s.nonreciprocal_score, s.defect_activity_score, s.phase_risk_score):
        return "Collect heat-charge transport evidence such as Seebeck-like or conductivity-like descriptors."
    if s.defect_activity_score >= max(s.thermoelectric_score, s.nonreciprocal_score, s.phase_risk_score):
        return "Collect defect mobility, vacancy, disorder, or ion-transport evidence."
    if s.phase_risk_score >= 0.40:
        return "Collect switching, phase transition, hysteresis, or stability-window evidence."
    return "Keep as baseline or low-priority comparison candidate."

def build_audit_text(rank: int, result: SourceWeightedScreeningResult) -> str:
    s, e = result.screening, result.evidence
    text = f"""
    ## {rank}. {s.name}

    Family: {s.family}

    Source-weighted priority: {result.source_weighted_priority:.4f}
    Model priority: {s.research_priority_score:.4f}
    Evidence strength: {e.evidence_strength:.4f}
    Evidence count: {e.evidence_count}
    Strongest source type: {e.strongest_source_type}
    Source-weighted label: {result.source_weighted_label}
    Model label: {s.rank_label}
    Response label: {s.response.response_label}

    Strongest functional signal: {strongest_functional_signal(result)}

    Warning flags:
    {chr(10).join('- ' + item for item in warning_flags(result))}

    Missing evidence:
    {chr(10).join('- ' + item for item in missing_evidence(result))}

    Suggested next action:
    {next_action(result)}
    """
    return textwrap.dedent(text).strip()

def make_audits(results: List[SourceWeightedScreeningResult]) -> List[CandidateAudit]:
    audits = []
    for rank, result in enumerate(results, start=1):
        s, e = result.screening, result.evidence
        audits.append(CandidateAudit(rank, s.name, s.family, result.source_weighted_priority,
            s.research_priority_score, e.evidence_strength, strongest_functional_signal(result),
            warning_flags(result), missing_evidence(result), next_action(result), build_audit_text(rank, result)))
    return audits

def write_audit_markdown(audits: List[CandidateAudit], output_md: str | Path) -> None:
    path = Path(output_md); path.parent.mkdir(parents=True, exist_ok=True)
    header = "# EMK Candidate Audit Report v7\n\nResearch-prioritization audit, not empirical validation."
    path.write_text(header + "\n\n" + "\n\n".join(a.audit_text for a in audits) + "\n", encoding="utf-8")

def write_audit_csv(audits: List[CandidateAudit], output_csv: str | Path) -> None:
    path = Path(output_csv); path.parent.mkdir(parents=True, exist_ok=True)
    rows = [{"rank": a.rank, "name": a.name, "family": a.family,
             "source_weighted_priority": a.source_weighted_priority,
             "model_priority_score": a.model_priority_score,
             "evidence_strength": a.evidence_strength,
             "strongest_signal": a.strongest_signal,
             "warning_flags": ";".join(a.warning_flags),
             "missing_evidence": ";".join(a.missing_evidence),
             "next_action": a.next_action} for a in audits]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)

def run_audit_report(audit_md: str | Path = "outputs/candidate_audit_report_v7.md", audit_csv: str | Path = "outputs/candidate_audit_summary_v7.csv") -> List[CandidateAudit]:
    audits = make_audits(run_source_weighted_screening())
    write_audit_markdown(audits, audit_md)
    write_audit_csv(audits, audit_csv)
    return audits

if __name__ == "__main__":
    for audit in run_audit_report():
        print(audit.rank, audit.name, audit.strongest_signal)
