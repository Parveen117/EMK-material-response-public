"""
EMK CSV Screening v4
====================

v4 turns the material screening engine into an editable CSV workflow.

Instead of hardcoding candidate materials inside Python, the user edits:

    data/candidate_materials_v4.csv

Then runs:

    python src/emk_csv_screening_v4.py

Output:

    outputs/material_screening_v4_from_csv.csv

This is the first practical screening workflow. A humble CSV, because apparently
civilization still runs on comma-separated offerings to the machine spirit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import csv

try:
    from emk_material_screening_v3 import (
        CandidateMaterial,
        ScreeningResult,
        screen_candidates,
        write_screening_csv,
    )
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parent))
    from emk_material_screening_v3 import (
        CandidateMaterial,
        ScreeningResult,
        screen_candidates,
        write_screening_csv,
    )

REQUIRED_COLUMNS = [
    "name", "family", "temperature_K", "electric_field",
    "temperature_gradient", "strain", "defect_density",
    "carrier_density", "ion_mobility", "symmetry_breaking", "notes",
]

NUMERIC_COLUMNS = [
    "temperature_K", "electric_field", "temperature_gradient", "strain",
    "defect_density", "carrier_density", "ion_mobility", "symmetry_breaking",
]

def _as_float(row: Dict[str, str], key: str) -> float:
    value = row.get(key, "")
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid numeric value for {key!r}: {value!r} in row {row}") from exc

def validate_columns(fieldnames: List[str] | None) -> None:
    if fieldnames is None:
        raise ValueError("CSV has no header row.")
    missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")

def read_candidate_csv(path: str | Path) -> List[CandidateMaterial]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Candidate CSV not found: {csv_path}")
    candidates: List[CandidateMaterial] = []
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        validate_columns(reader.fieldnames)
        for row in reader:
            if not row.get("name", "").strip():
                continue
            candidates.append(CandidateMaterial(
                name=row["name"].strip(), family=row["family"].strip(),
                temperature_K=_as_float(row, "temperature_K"),
                electric_field=_as_float(row, "electric_field"),
                temperature_gradient=_as_float(row, "temperature_gradient"),
                strain=_as_float(row, "strain"),
                defect_density=_as_float(row, "defect_density"),
                carrier_density=_as_float(row, "carrier_density"),
                ion_mobility=_as_float(row, "ion_mobility"),
                symmetry_breaking=_as_float(row, "symmetry_breaking"),
                notes=row.get("notes", "").strip(),
            ))
    return candidates

def run_csv_screening(
    input_csv: str | Path = "data/candidate_materials_v4.csv",
    output_csv: str | Path = "outputs/material_screening_v4_from_csv.csv",
) -> List[ScreeningResult]:
    candidates = read_candidate_csv(input_csv)
    if not candidates:
        raise ValueError(f"No candidate rows found in {input_csv}")
    results = screen_candidates(candidates)
    write_screening_csv(results, str(output_csv))
    return results

def print_results(results: List[ScreeningResult]) -> None:
    print("=" * 112)
    print("EMK CSV Screening v4")
    print("=" * 112)
    print("Ranked candidate materials from editable CSV")
    print("-" * 112)
    for i, r in enumerate(results, start=1):
        print(
            f"{i:02d}. {r.name:30s} | {r.family:26s} | "
            f"priority={r.research_priority_score:.4f} | "
            f"nonrecip={r.nonreciprocal_score:.4f} | "
            f"thermo={r.thermoelectric_score:.4f} | "
            f"defect={r.defect_activity_score:.4f} | "
            f"phase={r.phase_risk_score:.4f} | {r.rank_label}"
        )

def main() -> None:
    results = run_csv_screening()
    print_results(results)
    print("\nSaved: outputs/material_screening_v4_from_csv.csv")

if __name__ == "__main__":
    main()
