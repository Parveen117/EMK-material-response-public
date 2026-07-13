# Public Release Boundary: EMK Materials v1-v9

## Included layers

This public snapshot contains the complete materials-only computational chain through ledger verification:

1. single-material lambda response
2. lattice Onsager response
3. candidate screening
4. editable CSV screening
5. evidence-weighted screening
6. source-weighted evidence
7. candidate audit reporting
8. material certificates and append-only finality ledger
9. standalone ledger verification

## Evidence discipline

Evidence rows may be marked as `primary_paper`, `database`, `review_paper`, `benchmark`, `control`, `candidate_csv`, `proxy`, `model_inference`, `placeholder`, `manual_note`, or `unknown`.

The source-weighting layer deliberately assigns lower authority to proxy, model-inference, placeholder, manual-note, and unknown rows. A high computational score cannot silently turn weak evidence into an empirical result.

## Certificate boundary

A v8 certificate proves that a computational record was serialized, hashed, classified, and chained into a verifiable ledger. It does not prove that the underlying material claim is experimentally true.

The certificate therefore carries an explicit claim boundary. Materials with insufficient evidence remain labeled as computational screening records only.

## Excluded layers

The following private development is not part of this public release:

- finality orchestration beyond the v9 verifier
- device-material bridges
- device-role mapping
- experiment planning
- one-device measurement closure
- thermodynamic and NRT-cycle kernels after the public boundary
- measurement-loop imports and instrument closure
- controlled experiment packets
- operator learning and calibration
- RG and phase-flow layers
- fabrication details, dimensions, hardware architecture, and patent drafting material

## Reproducibility

Run the complete no-dependency regression suite from the repository root:

```bash
python tests/run_material_tests.py
```

GitHub Actions runs the suite on Python 3.10, 3.11, and 3.12 and generates demonstration outputs on Python 3.12.

## Scientific status

This repository is exploratory computational theory and screening infrastructure. It is not DFT, molecular dynamics, a validated transport solver, or experimental confirmation of a new material effect.
