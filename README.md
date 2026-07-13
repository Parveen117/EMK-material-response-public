# EMK Material Response Public

A curated, reproducible research snapshot for testing a candidate lambda-geometric description of non-equilibrium material response.

## Status

This repository contains an exploratory computational framework. It does **not** establish a validated physical law, a certified material predictor, or a fabrication-ready device design. The current equations and thresholds are hypotheses implemented as transparent code so they can be inspected, reproduced, challenged, and replaced by experimental calibration.

## Research question

Can a compact lambda-state representation help organize departures from near-equilibrium reciprocal transport in driven materials?

The framework tracks four effective response coordinates,

```text
lambda_p, lambda_v, lambda_s, lambda_t
```

and computes a bounded candidate curvature score together with an Onsager-style cross-response gap,

```text
ReciprocityGap = |L_qe - L_eq|.
```

Near equilibrium, the working expectation is that both quantities remain small. Under stronger drive, symmetry breaking, strain, or defect loading, the model permits a larger gap. This is a screening hypothesis, not an experimental conclusion.

## Public-release boundary

Included here:

- transparent reference equations;
- synthetic demonstration inputs;
- deterministic outputs;
- reproducibility tests;
- explicit assumptions and falsification conditions.

Excluded from this public snapshot:

- fabrication dimensions and device architecture;
- unpublished laboratory mappings;
- patent drafting material;
- private evidence ledgers;
- proprietary calibration data.

## Quick start

```bash
python -m src.emk_lambda_material_response_v1
python -m unittest discover -s tests -v
```

The demo writes:

```text
outputs/material_response_v1_demo.csv
```

## Interpretation discipline

The included material names are proxies used to exercise the code path. Their scores must not be interpreted as measured properties of real samples. A public claim becomes scientifically meaningful only after preregistered calibration and held-out comparison against traceable measurements.

## Falsification criteria

The candidate framework should be rejected or materially revised if, after calibration:

1. the curvature score does not improve held-out prediction over simpler baselines;
2. the reciprocity-gap estimate fails to track independently measured cross-response asymmetry;
3. classifications are unstable under reasonable uncertainty in the inputs;
4. apparent performance disappears under control subtraction or leakage correction;
5. model thresholds require material-by-material tuning without transferable structure.

## Repository map

```text
src/      reference implementation
tests/    deterministic unit tests
docs/     assumptions, limitations, and release notes
outputs/  generated demonstration artifacts
```

## Relationship to the wider research programme

This repository is the public materials-response layer. It is intentionally separated from private device engineering and patent repositories. Its purpose is narrower: expose a falsifiable computational object that independent readers can run and criticize.

## Citation

See `CITATION.cff`. Until a versioned archival release is issued, cite the repository URL and exact commit hash used.

## Rights and reuse

No open-source license has yet been granted. The repository is publicly inspectable, but reuse rights remain reserved until an explicit license file is added.