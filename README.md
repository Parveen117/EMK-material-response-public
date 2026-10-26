# EMK Materials Response

> **Research record:** [Dated snapshot, content hashes and archive links](RESEARCH_PROVENANCE.md) · [Canonical repository governance](GOVERNANCE.md). Cite the exact version used.


> **Patent status.** This repository is associated with inventor-controlled patent filings and related intellectual-property rights. Publication does not grant any patent license. See [`PATENT_NOTICE.md`](PATENT_NOTICE.md).
>
> **Copyright and license boundary.** This is a controlled public technical inspection and citation release, not an unrestricted open-source grant. All rights are reserved unless a separate written license states otherwise. See [`LICENSE`](LICENSE) and [`COPYRIGHT_NOTICE.md`](COPYRIGHT_NOTICE.md).
>
> **Public release boundary.** This repository is a bounded public materials-response release and does not reproduce the complete private filing, device, laboratory, hardware, calibration, or internal development record. See [`docs/PUBLIC_RELEASE_BOUNDARY.md`](docs/PUBLIC_RELEASE_BOUNDARY.md).

## Public research snapshot

This repository is the bounded public release of the existing private `EMK-Materials-Response` research stack.

It contains the materials-response chain from v1 through v9:

1. single-material lambda response
2. lattice Onsager response
3. editable material screening
4. CSV-driven screening
5. evidence-weighted screening
6. source-weighted evidence
7. candidate audit reporting
8. material certificates and append-only finality records
9. material-ledger verification

## Working research question

Can a compact lambda-geometric state help organize departures from near-equilibrium reciprocal transport in driven materials?

The framework tracks four effective coordinates:

```text
lambda_p, lambda_v, lambda_s, lambda_t
```

and evaluates a candidate lambda-curvature together with an Onsager-style reciprocity gap:

```text
ReciprocityGap = |L_qe - L_eq|
```

Near equilibrium, the working expectation is that both quantities remain small. Under stronger drive, symmetry breaking, strain, defect loading, or lattice mismatch, the framework permits larger bounded response indicators.

These are screening hypotheses implemented as transparent code. They are not experimentally established material laws.

## Included public stack

```text
src/emk_lambda_material_response_v1.py
src/emk_lattice_onsager_v2.py
src/emk_material_screening_v3.py
src/emk_csv_screening_v4.py
src/emk_evidence_weighted_screening_v5.py
src/emk_source_weighted_evidence_v6.py
src/emk_audit_report_v7.py
src/emk_material_certificate_v8.py
src/emk_verify_material_ledger_v9.py
```

The corresponding documentation, public input tables, notebooks, demonstration outputs, audit summaries, certificates, and ledger records are added as part of this bounded release.

## Explicit exclusion boundary

This snapshot deliberately excludes later private layers involving:

- device-material bridges
- device-role assignment
- experiment planning
- one-device closure loops
- fabrication or hardware-specific mappings
- instrument-control and instrument-grade closure
- unpublished laboratory mappings
- patent drafting material
- proprietary calibration records

The cutoff is intentional: public materials science through v9, private device-facing development from v10 onward.

## Scientific honesty boundary

This repository is not:

- density-functional theory
- molecular dynamics
- a validated transport solver
- a substitute for traceable laboratory measurements
- proof of a new material or device effect

Material names in demonstration files may be proxies used to exercise the computational pipeline. Scores, labels, certificates, and ledger states should be treated as reproducible computational outputs, not measured properties of real samples.

## Run from the repository root

```bash
python src/emk_lambda_material_response_v1.py
python src/emk_lattice_onsager_v2.py
python src/emk_material_screening_v3.py
python src/emk_csv_screening_v4.py
python src/emk_evidence_weighted_screening_v5.py
python src/emk_source_weighted_evidence_v6.py
python src/emk_audit_report_v7.py
python src/emk_material_certificate_v8.py
python src/emk_verify_material_ledger_v9.py
python tests/run_material_tests.py
```

## Falsification discipline

The framework should be rejected or materially revised if calibrated, held-out testing shows that:

1. lambda-curvature does not improve prediction over simpler baselines;
2. reciprocity-gap estimates do not track independently measured cross-response asymmetry;
3. classifications are unstable under realistic input uncertainty;
4. apparent performance disappears after control subtraction or leakage correction;
5. thresholds require material-by-material tuning without transferable structure.

## Documentation

- [`docs/PUBLIC_RELEASE_BOUNDARY.md`](docs/PUBLIC_RELEASE_BOUNDARY.md) — public/private release boundary.
- [`PATENT_NOTICE.md`](PATENT_NOTICE.md) — patent-rights notice.
- [`COPYRIGHT_NOTICE.md`](COPYRIGHT_NOTICE.md) — copyright ownership and restriction notice.
- [`LICENSE`](LICENSE) — controlled inspection and citation license boundary.
- [`CITATION.cff`](CITATION.cff) — citation metadata.

## Citation

Dabas, M. (2026). *EMK Materials Response: Lambda-Geometric Screening, Evidence Weighting, and Material Finality* (Version 0.1.0-rc1). GitHub repository. Cite the exact release tag or commit used.

## Rights and reuse

Public visibility permits inspection and citation only under the repository notices. It does not grant patent, commercial, redistribution, modification, sublicensing, or production-use rights.
