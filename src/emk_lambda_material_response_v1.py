from dataclasses import dataclass
from pathlib import Path
import csv
import math


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class LambdaState:
    lambda_p: float
    lambda_v: float
    lambda_s: float
    lambda_t: float


@dataclass(frozen=True)
class OnsagerMatrix:
    L_qq: float
    L_qe: float
    L_eq: float
    L_ee: float

    @property
    def reciprocity_gap(self) -> float:
        return abs(self.L_qe - self.L_eq)


@dataclass(frozen=True)
class MaterialResponse:
    name: str
    lambda_state: LambdaState
    lambda_curvature: float
    onsager_matrix: OnsagerMatrix
    reciprocity_gap: float
    stability_score: float
    response_label: str


def _validate_unit_interval(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1]; received {value!r}")


def validate_material_state(material: MaterialState) -> None:
    if material.temperature_K <= 0:
        raise ValueError("temperature_K must be positive")

    for field_name in (
        "defect_density",
        "carrier_density",
        "ion_mobility",
        "symmetry_breaking",
    ):
        _validate_unit_interval(field_name, getattr(material, field_name))


def encode_lambda_state(material: MaterialState) -> LambdaState:
    """Encode normalized material descriptors into four effective coordinates.

    Coefficients are exploratory and dimensionless. They are not fitted physical
    constants and must be recalibrated against traceable measurements before any
    empirical interpretation.
    """
    validate_material_state(material)
    temperature_scale = max(material.temperature_K, 1.0) / 300.0

    lambda_p = (
        1.0
        + 0.35 * abs(material.electric_field)
        + 0.25 * abs(material.strain)
        + 0.20 * material.symmetry_breaking
    )
    lambda_v = (
        1.0
        + 0.30 * abs(material.strain)
        + 0.25 * material.defect_density
        + 0.15 * material.ion_mobility
    )
    lambda_s = (
        1.0
        + 0.40 * math.log1p(temperature_scale)
        + 0.50 * material.defect_density
        + 0.30 * abs(material.temperature_gradient)
    )
    lambda_t = (
        1.0
        + 0.35 * material.ion_mobility
        + 0.25 * material.carrier_density
        + 0.20 * material.symmetry_breaking
    )

    return LambdaState(lambda_p, lambda_v, lambda_s, lambda_t)


def lambda_curvature(lambda_state: LambdaState, material: MaterialState) -> float:
    lp = lambda_state.lambda_p
    lv = lambda_state.lambda_v
    ls = lambda_state.lambda_s
    lt = lambda_state.lambda_t

    pv_gap = abs(lp - lv) / (lp + lv + 1e-12)
    st_gap = abs(ls - lt) / (ls + lt + 1e-12)
    cross_gap = abs(lp * ls - lv * lt) / (lp * ls + lv * lt + 1e-12)

    drive = (
        0.30 * abs(material.temperature_gradient)
        + 0.25 * abs(material.electric_field)
        + 0.35 * material.defect_density
        + 0.30 * material.symmetry_breaking
        + 0.20 * abs(material.strain)
    )

    return 0.35 * pv_gap + 0.35 * st_gap + 0.30 * cross_gap + drive


def build_onsager_matrix(
    lambda_state: LambdaState,
    curvature: float,
    material: MaterialState,
) -> OnsagerMatrix:
    lp = lambda_state.lambda_p
    ls = lambda_state.lambda_s
    lt = lambda_state.lambda_t

    L_qq = 1.0 + 0.30 * ls + 0.20 * material.ion_mobility
    L_ee = 1.0 + 0.30 * lp + 0.25 * material.carrier_density

    reciprocal_core = (
        0.50 * (material.carrier_density + material.ion_mobility)
        + 0.15 * (lp + lt) / 2.0
    )
    asymmetry = curvature * (
        0.20
        + 0.60 * material.symmetry_breaking
        + 0.30 * material.defect_density
        + 0.20 * abs(material.strain)
    )

    return OnsagerMatrix(
        L_qq=L_qq,
        L_qe=reciprocal_core + 0.5 * asymmetry,
        L_eq=reciprocal_core - 0.5 * asymmetry,
        L_ee=L_ee,
    )


def classify(curvature: float, gap: float, material: MaterialState) -> str:
    if curvature < 0.12 and gap < 0.03:
        return "RECIPROCAL_STABLE_MATERIAL"
    if curvature < 0.30 and gap < 0.10:
        return "BOUNDED_CURVATURE_MATERIAL"
    if gap >= 0.10 and material.symmetry_breaking > 0.20:
        return "NON_RECIPROCAL_ACTIVE_MATERIAL"
    if material.defect_density > 0.25 or abs(material.strain) > 0.25:
        return "DEFECT_STRAIN_SENSITIVE_MATERIAL"
    return "OPEN_MATERIAL_RESPONSE_FIELD"


def stability_score(curvature: float, gap: float, material: MaterialState) -> float:
    penalty = (
        0.55 * curvature
        + 0.65 * gap
        + 0.20 * material.defect_density
        + 0.15 * abs(material.strain)
    )
    return max(0.0, min(1.0, 1.0 - penalty))


def evaluate_material(material: MaterialState) -> MaterialResponse:
    lambda_state = encode_lambda_state(material)
    curvature = lambda_curvature(lambda_state, material)
    onsager_matrix = build_onsager_matrix(lambda_state, curvature, material)
    gap = onsager_matrix.reciprocity_gap

    return MaterialResponse(
        name=material.name,
        lambda_state=lambda_state,
        lambda_curvature=curvature,
        onsager_matrix=onsager_matrix,
        reciprocity_gap=gap,
        stability_score=stability_score(curvature, gap, material),
        response_label=classify(curvature, gap, material),
    )


def demo_materials() -> list[MaterialState]:
    """Return synthetic proxies used only for software demonstration."""
    return [
        MaterialState("Si_reference", 300, 0.05, 0.05, 0.02, 0.01, 0.30, 0.05, 0.02),
        MaterialState("Bi2Te3_thermoelectric_proxy", 350, 0.20, 0.45, 0.08, 0.08, 0.75, 0.12, 0.18),
        MaterialState("MoS2_broken_symmetry_proxy", 300, 0.35, 0.20, 0.15, 0.06, 0.55, 0.08, 0.55),
        MaterialState("Defective_oxide_ion_conductor_proxy", 700, 0.25, 0.35, 0.18, 0.35, 0.25, 0.80, 0.25),
        MaterialState("Phase_change_material_proxy", 600, 0.30, 0.40, 0.30, 0.28, 0.60, 0.45, 0.30),
    ]


def run_demo(output_csv: str = "outputs/material_response_v1_demo.csv") -> list[MaterialResponse]:
    responses = [evaluate_material(material) for material in demo_materials()]
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [
        {
            "name": response.name,
            "lambda_p": response.lambda_state.lambda_p,
            "lambda_v": response.lambda_state.lambda_v,
            "lambda_s": response.lambda_state.lambda_s,
            "lambda_t": response.lambda_state.lambda_t,
            "lambda_curvature": response.lambda_curvature,
            "L_qq": response.onsager_matrix.L_qq,
            "L_qe": response.onsager_matrix.L_qe,
            "L_eq": response.onsager_matrix.L_eq,
            "L_ee": response.onsager_matrix.L_ee,
            "reciprocity_gap": response.reciprocity_gap,
            "stability_score": response.stability_score,
            "response_label": response.response_label,
        }
        for response in responses
    ]

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    return responses


if __name__ == "__main__":
    for response in run_demo():
        print(
            response.name,
            response.response_label,
            round(response.lambda_curvature, 4),
            round(response.reciprocity_gap, 4),
        )
