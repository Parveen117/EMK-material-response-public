"""
EMK Lattice Onsager Response v2
===============================

This module extends the v1 single-material response engine into a lattice
coupling layer.

Important honesty boundary
--------------------------
This is not DFT, not molecular dynamics, and not a validated transport solver.
It is a geometric screening engine for research direction and hypothesis testing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import csv
import math

try:
    from emk_lambda_material_response_v1 import MaterialState, MaterialResponse, evaluate_material
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from emk_lambda_material_response_v1 import MaterialState, MaterialResponse, evaluate_material


@dataclass
class MaterialSite:
    site_id: str
    state: MaterialState
    position: Tuple[float, float, float]
    role: str = "bulk"


@dataclass
class LatticeBond:
    a: str
    b: str
    distance: float
    coupling_strength: float
    bond_type: str = "generic"


@dataclass
class BondResponse:
    a: str
    b: str
    bond_type: str
    lambda_mismatch: float
    curvature_mismatch: float
    gap_mismatch: float
    directional_bias: float
    bond_activity: float
    label: str


@dataclass
class LatticeResponse:
    name: str
    site_responses: Dict[str, MaterialResponse]
    bond_responses: List[BondResponse]
    mean_curvature: float
    max_curvature: float
    mean_reciprocity_gap: float
    max_reciprocity_gap: float
    lattice_directionality: float
    lattice_activity: float
    lattice_label: str


def _distance(p: Tuple[float, float, float], q: Tuple[float, float, float]) -> float:
    return math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(p, q)))


def lambda_mismatch(left: MaterialResponse, right: MaterialResponse) -> float:
    L = left.lambda_state
    R = right.lambda_state
    diffs = [L.lambda_p - R.lambda_p, L.lambda_v - R.lambda_v, L.lambda_s - R.lambda_s, L.lambda_t - R.lambda_t]
    return float(math.sqrt(sum(x * x for x in diffs)))


def infer_bonds(sites: Iterable[MaterialSite], cutoff: float = 1.55) -> List[LatticeBond]:
    nodes = list(sites)
    bonds: List[LatticeBond] = []
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            d = _distance(a.position, b.position)
            if d <= cutoff:
                strength = 1.0 / (1.0 + d * d)
                if a.role != b.role:
                    bond_type = "interface_or_defect"
                    strength *= 1.15
                else:
                    bond_type = "bulk"
                bonds.append(LatticeBond(a.site_id, b.site_id, d, strength, bond_type))
    return bonds


def evaluate_bond(bond: LatticeBond, responses: Dict[str, MaterialResponse], sites: Dict[str, MaterialSite]) -> BondResponse:
    left = responses[bond.a]
    right = responses[bond.b]
    site_a = sites[bond.a]
    site_b = sites[bond.b]

    lm = lambda_mismatch(left, right)
    cm = abs(left.lambda_curvature - right.lambda_curvature)
    gm = abs(left.reciprocity_gap - right.reciprocity_gap)

    symmetry_drive = 0.5 * (site_a.state.symmetry_breaking + site_b.state.symmetry_breaking)
    defect_drive = 0.5 * (site_a.state.defect_density + site_b.state.defect_density)
    strain_drive = 0.5 * (abs(site_a.state.strain) + abs(site_b.state.strain))

    directional_bias = bond.coupling_strength * (0.35 * lm + 0.30 * cm + 0.35 * gm) * (1.0 + symmetry_drive + 0.5 * strain_drive)
    bond_activity = bond.coupling_strength * (0.40 * lm + 0.30 * cm + 0.20 * gm + 0.10 * defect_drive)

    if bond_activity < 0.06 and directional_bias < 0.04:
        label = "QUIET_RECIPROCAL_BOND"
    elif directional_bias > 0.12 and symmetry_drive > 0.20:
        label = "DIRECTIONAL_NONRECIPROCAL_BOND"
    elif defect_drive > 0.20 or bond.bond_type == "interface_or_defect":
        label = "DEFECT_INTERFACE_ACTIVE_BOND"
    else:
        label = "BOUNDED_LATTICE_CURVATURE_BOND"

    return BondResponse(bond.a, bond.b, bond.bond_type, lm, cm, gm, float(directional_bias), float(bond_activity), label)


def classify_lattice(mean_curvature: float, max_curvature: float, mean_gap: float, max_gap: float, directionality: float, activity: float) -> str:
    if mean_curvature < 0.18 and mean_gap < 0.05 and directionality < 0.05:
        return "RECIPROCAL_STABLE_LATTICE"
    if directionality > 0.12 and max_gap > 0.10:
        return "NONRECIPROCAL_ACTIVE_LATTICE"
    if max_curvature > 0.55 or activity > 0.20:
        return "DEFECT_PHASE_RISK_LATTICE"
    return "BOUNDED_CURVATURE_LATTICE"


def evaluate_lattice(name: str, sites: List[MaterialSite], bonds: List[LatticeBond] | None = None, cutoff: float = 1.55) -> LatticeResponse:
    site_map = {s.site_id: s for s in sites}
    site_responses = {s.site_id: evaluate_material(s.state) for s in sites}
    if bonds is None:
        bonds = infer_bonds(sites, cutoff=cutoff)
    bond_responses = [evaluate_bond(b, site_responses, site_map) for b in bonds]

    curvatures = [r.lambda_curvature for r in site_responses.values()]
    gaps = [r.reciprocity_gap for r in site_responses.values()]
    mean_curvature = float(sum(curvatures) / len(curvatures)) if curvatures else 0.0
    max_curvature = float(max(curvatures)) if curvatures else 0.0
    mean_gap = float(sum(gaps) / len(gaps)) if gaps else 0.0
    max_gap = float(max(gaps)) if gaps else 0.0
    directionality = float(sum(b.directional_bias for b in bond_responses) / len(bond_responses)) if bond_responses else 0.0
    activity = float(sum(b.bond_activity for b in bond_responses) / len(bond_responses)) if bond_responses else 0.0
    label = classify_lattice(mean_curvature, max_curvature, mean_gap, max_gap, directionality, activity)

    return LatticeResponse(name, site_responses, bond_responses, mean_curvature, max_curvature, mean_gap, max_gap, directionality, activity, label)


def demo_lattice_sites() -> List[MaterialSite]:
    return [
        MaterialSite("A0", MaterialState("Si_bulk_A0", 300, 0.04, 0.04, 0.01, 0.01, 0.30, 0.04, 0.02), (0.0, 0.0, 0.0), "bulk"),
        MaterialSite("A1", MaterialState("Si_bulk_A1", 300, 0.05, 0.05, 0.02, 0.015, 0.31, 0.05, 0.02), (1.0, 0.0, 0.0), "bulk"),
        MaterialSite("B0", MaterialState("MoS2_interface_B0", 320, 0.28, 0.18, 0.14, 0.05, 0.55, 0.08, 0.50), (0.0, 1.0, 0.0), "interface"),
        MaterialSite("D0", MaterialState("oxide_defect_D0", 650, 0.22, 0.32, 0.18, 0.35, 0.25, 0.75, 0.25), (1.0, 1.0, 0.0), "defect"),
    ]


def run_lattice_demo(output_csv: str = "outputs/lattice_onsager_v2_demo.csv") -> LatticeResponse:
    response = evaluate_lattice("demo_mixed_lattice", demo_lattice_sites())
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for site_id, r in response.site_responses.items():
        rows.append({"kind": "site", "id": site_id, "pair": "", "label": r.response_label, "lambda_curvature": r.lambda_curvature, "reciprocity_gap": r.reciprocity_gap, "stability_score": r.stability_score, "directional_bias": "", "bond_activity": ""})
    for b in response.bond_responses:
        rows.append({"kind": "bond", "id": "", "pair": f"{b.a}-{b.b}", "label": b.label, "lambda_curvature": b.curvature_mismatch, "reciprocity_gap": b.gap_mismatch, "stability_score": "", "directional_bias": b.directional_bias, "bond_activity": b.bond_activity})
    rows.append({"kind": "lattice", "id": response.name, "pair": "", "label": response.lattice_label, "lambda_curvature": response.mean_curvature, "reciprocity_gap": response.mean_reciprocity_gap, "stability_score": "", "directional_bias": response.lattice_directionality, "bond_activity": response.lattice_activity})
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return response


if __name__ == "__main__":
    result = run_lattice_demo()
    print("=" * 100)
    print("EMK Lattice Onsager Response v2")
    print("=" * 100)
    print("Lattice:", result.name)
    print("Label:", result.lattice_label)
    print("Mean curvature:", round(result.mean_curvature, 5))
    print("Mean reciprocity gap:", round(result.mean_reciprocity_gap, 5))
    print("Directionality:", round(result.lattice_directionality, 5))
    print("Activity:", round(result.lattice_activity, 5))
    print("\nBond responses:")
    for b in result.bond_responses:
        print(f"  {b.a}-{b.b}: {b.label}, bias={b.directional_bias:.5f}, activity={b.bond_activity:.5f}")
    print("\nSaved: outputs/lattice_onsager_v2_demo.csv")