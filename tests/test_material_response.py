import tempfile
import unittest
from pathlib import Path

from src.emk_lambda_material_response_v1 import (
    MaterialState,
    demo_materials,
    evaluate_material,
    run_demo,
)


class MaterialResponseTests(unittest.TestCase):
    def test_demo_is_deterministic(self) -> None:
        first = [evaluate_material(item) for item in demo_materials()]
        second = [evaluate_material(item) for item in demo_materials()]
        self.assertEqual(first, second)

    def test_reciprocity_gap_matches_matrix_difference(self) -> None:
        response = evaluate_material(demo_materials()[0])
        expected = abs(response.onsager_matrix.L_qe - response.onsager_matrix.L_eq)
        self.assertAlmostEqual(response.reciprocity_gap, expected)

    def test_stability_score_is_bounded(self) -> None:
        for material in demo_materials():
            response = evaluate_material(material)
            self.assertGreaterEqual(response.stability_score, 0.0)
            self.assertLessEqual(response.stability_score, 1.0)

    def test_invalid_fractional_descriptor_is_rejected(self) -> None:
        invalid = MaterialState(
            "invalid",
            300,
            0.0,
            0.0,
            0.0,
            1.2,
            0.2,
            0.2,
            0.2,
        )
        with self.assertRaises(ValueError):
            evaluate_material(invalid)

    def test_demo_writes_csv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "demo.csv"
            responses = run_demo(str(output))
            self.assertTrue(output.exists())
            self.assertEqual(len(responses), len(demo_materials()))
            self.assertIn("reciprocity_gap", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
