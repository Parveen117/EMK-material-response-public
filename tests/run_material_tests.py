"""
EMK Materials Regression Tests v9
=================================

No-dependency regression tests for the public v1-v9 materials stack.

Run from the repository root:

    python tests/run_material_tests.py
"""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from emk_lambda_material_response_v1 import MaterialState, evaluate_material
from emk_csv_screening_v4 import read_candidate_csv
from emk_source_weighted_evidence_v6 import run_source_weighted_screening
from emk_material_certificate_v8 import run_material_certificate_demo
from emk_verify_material_ledger_v9 import verify_ledger


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_v1_single_material_response() -> None:
    material = MaterialState(
        name="test_material",
        temperature_K=300,
        electric_field=0.05,
        temperature_gradient=0.05,
        strain=0.01,
        defect_density=0.01,
        carrier_density=0.30,
        ion_mobility=0.05,
        symmetry_breaking=0.02,
    )
    response = evaluate_material(material)
    assert_true(response.lambda_curvature >= 0.0, "lambda curvature must be non-negative")
    assert_true(response.reciprocity_gap >= 0.0, "reciprocity gap must be non-negative")
    assert_true(0.0 <= response.stability_score <= 1.0, "stability score must be in [0, 1]")
    assert_true(bool(response.response_label), "response label must be non-empty")


def test_v4_candidate_csv_loading() -> None:
    candidates = read_candidate_csv(ROOT / "data" / "candidate_materials_v4.csv")
    assert_true(len(candidates) >= 5, "expected at least five candidate materials")
    assert_true("Si_reference" in {candidate.name for candidate in candidates}, "baseline missing")


def test_v6_source_weighted_screening_runs() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "source_weighted.csv"
        results = run_source_weighted_screening(
            candidate_csv=ROOT / "data" / "candidate_materials_v4.csv",
            evidence_csv=ROOT / "data" / "material_evidence_v5.csv",
            output_csv=output,
        )
        assert_true(len(results) >= 5, "expected at least five source-weighted results")
        assert_true(output.exists(), "source-weighted output CSV was not created")
        assert_true(
            results[0].source_weighted_priority >= results[-1].source_weighted_priority,
            "results not sorted",
        )


def test_v8_certificate_finality_and_v9_verifier() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        certs_path = tmp_path / "material_certificates_v8.json"
        ledger_path = tmp_path / "material_finality_ledger_v8.jsonl"

        result = run_material_certificate_demo(
            certificates_json=certs_path,
            ledger_path=ledger_path,
        )

        assert_true(certs_path.exists(), "certificate JSON output was not created")
        assert_true(ledger_path.exists(), "ledger output was not created")
        assert_true(len(result["certificates"]) >= 5, "expected at least five certificates")
        assert_true(result["verification"]["ok"], "internal v8 verification failed")

        standalone = verify_ledger(ledger_path)
        assert_true(standalone["ok"], "standalone v9 verifier failed")
        assert_true(
            standalone["count"] == len(result["certificates"]),
            "verifier count mismatch",
        )


def run_all_tests() -> None:
    tests = [
        test_v1_single_material_response,
        test_v4_candidate_csv_loading,
        test_v6_source_weighted_screening_runs,
        test_v8_certificate_finality_and_v9_verifier,
    ]

    print("=" * 100)
    print("EMK Materials Regression Tests v9")
    print("=" * 100)

    for test in tests:
        test()
        print("PASS", test.__name__)

    print("=" * 100)
    print("ALL MATERIAL TESTS PASSED")
    print("=" * 100)


if __name__ == "__main__":
    run_all_tests()
