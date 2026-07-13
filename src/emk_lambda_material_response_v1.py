from dataclasses import dataclass
from pathlib import Path
import math
import csv

@dataclass
class MaterialState:
    name: str
    temperature_K: float
    electric_field: float
    temperature_gradient: float
    strain: float
    defect_density: float
    carrier_density: float
    ion_mobility: float
    symmetry_breaking: float

@dataclass
class LambdaState:
    lambda_p: float
    lambda_v: float
    lambda_s: float
    lambda_t: float

@dataclass
class OnsagerMatrix:
    L_qq: float
    L_qe: float
    L_eq: float
    L_ee: float

    @property
    def reciprocity_gap(self):
        return abs(self.L_qe - self.L_eq)

@dataclass
class MaterialResponse:
    name: str
    lambda_state: LambdaState
    lambda_curvature: float
    onsager_matrix: OnsagerMatrix
    reciprocity_gap: float
    stability_score: float
    response_label: str

def encode_lambda_state(m):
    T_norm = max(m.temperature_K, 1.0) / 300.0

    lambda_p = 1.0 + 0.35*abs(m.electric_field) + 0.25*abs(m.strain) + 0.20*m.symmetry_breaking
    lambda_v = 1.0 + 0.30*abs(m.strain) + 0.25*m.defect_density + 0.15*m.ion_mobility
    lambda_s = 1.0 + 0.40*math.log1p(T_norm) + 0.50*m.defect_density + 0.30*abs(m.temperature_gradient)
    lambda_t = 1.0 + 0.35*m.ion_mobility + 0.25*m.carrier_density + 0.20*m.symmetry_breaking

    return LambdaState(lambda_p, lambda_v, lambda_s, lambda_t)

def lambda_curvature(lam, m):
    lp, lv, ls, lt = lam.lambda_p, lam.lambda_v, lam.lambda_s, lam.lambda_t

    pv_gap = abs(lp - lv) / (lp + lv + 1e-12)
    st_gap = abs(ls - lt) / (ls + lt + 1e-12)
    cross_gap = abs(lp*ls - lv*lt) / (lp*ls + lv*lt + 1e-12)

    drive = (
        0.30*abs(m.temperature_gradient)
        + 0.25*abs(m.electric_field)
        + 0.35*m.defect_density
        + 0.30*m.symmetry_breaking
        + 0.20*abs(m.strain)
    )

    return 0.35*pv_gap + 0.35*st_gap + 0.30*cross_gap + drive

def build_onsager_matrix(lam, curvature, m):
    lp, lv, ls, lt = lam.lambda_p, lam.lambda_v, lam.lambda_s, lam.lambda_t

    L_qq = 1.0 + 0.30*ls + 0.20*m.ion_mobility
    L_ee = 1.0 + 0.30*lp + 0.25*m.carrier_density

    reciprocal_core = 0.50*(m.carrier_density + m.ion_mobility) + 0.15*(lp + lt)/2.0

    asymmetry = curvature * (
        0.20
        + 0.60*m.symmetry_breaking
        + 0.30*m.defect_density
        + 0.20*abs(m.strain)
    )

    L_qe = reciprocal_core + 0.5*asymmetry
    L_eq = reciprocal_core - 0.5*asymmetry

    return OnsagerMatrix(L_qq, L_qe, L_eq, L_ee)

def classify(curvature, gap, m):
    if curvature < 0.12 and gap < 0.03:
        return "RECIPROCAL_STABLE_MATERIAL"
    if curvature < 0.30 and gap < 0.10:
        return "BOUNDED_CURVATURE_MATERIAL"
    if gap >= 0.10 and m.symmetry_breaking > 0.20:
        return "NON_RECIPROCAL_ACTIVE_MATERIAL"
    if m.defect_density > 0.25 or abs(m.strain) > 0.25:
        return "DEFECT_STRAIN_SENSITIVE_MATERIAL"
    return "OPEN_MATERIAL_RESPONSE_FIELD"

def stability_score(curvature, gap, m):
    penalty = 0.55*curvature + 0.65*gap + 0.20*m.defect_density + 0.15*abs(m.strain)
    return max(0.0, min(1.0, 1.0 - penalty))

def evaluate_material(m):
    lam = encode_lambda_state(m)
    curv = lambda_curvature(lam, m)
    L = build_onsager_matrix(lam, curv, m)
    gap = L.reciprocity_gap
    score = stability_score(curv, gap, m)
    label = classify(curv, gap, m)

    return MaterialResponse(m.name, lam, curv, L, gap, score, label)

def demo_materials():
    return [
        MaterialState("Si_reference", 300, 0.05, 0.05, 0.02, 0.01, 0.30, 0.05, 0.02),
        MaterialState("Bi2Te3_thermoelectric_proxy", 350, 0.20, 0.45, 0.08, 0.08, 0.75, 0.12, 0.18),
        MaterialState("MoS2_broken_symmetry_proxy", 300, 0.35, 0.20, 0.15, 0.06, 0.55, 0.08, 0.55),
        MaterialState("Defective_oxide_ion_conductor_proxy", 700, 0.25, 0.35, 0.18, 0.35, 0.25, 0.80, 0.25),
        MaterialState("Phase_change_material_proxy", 600, 0.30, 0.40, 0.30, 0.28, 0.60, 0.45, 0.30),
    ]

def run_demo(output_csv="outputs/material_response_v1_demo.csv"):
    responses = [evaluate_material(m) for m in demo_materials()]
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for r in responses:
        rows.append({
            "name": r.name,
            "lambda_p": r.lambda_state.lambda_p,
            "lambda_v": r.lambda_state.lambda_v,
            "lambda_s": r.lambda_state.lambda_s,
            "lambda_t": r.lambda_state.lambda_t,
            "lambda_curvature": r.lambda_curvature,
            "L_qq": r.onsager_matrix.L_qq,
            "L_qe": r.onsager_matrix.L_qe,
            "L_eq": r.onsager_matrix.L_eq,
            "L_ee": r.onsager_matrix.L_ee,
            "reciprocity_gap": r.reciprocity_gap,
            "stability_score": r.stability_score,
            "response_label": r.response_label,
        })

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return responses

if __name__ == "__main__":
    responses = run_demo()
    for r in responses:
        print(r.name, r.response_label, round(r.lambda_curvature, 4), round(r.reciprocity_gap, 4))