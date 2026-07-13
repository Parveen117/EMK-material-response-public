# Assumptions and limitations

## Model status

This release is an exploratory computational model. It is intended to expose a falsifiable structure, not to certify a new physical law.

## Main assumptions

1. The input descriptors are normalized summaries rather than raw instrument observables.
2. The four lambda coordinates are effective variables, not directly measured thermodynamic state functions in this release.
3. The coefficient values are heuristic and dimensionless.
4. The Onsager-style matrix is a screening construction. It is not derived here from a microscopic Hamiltonian, Green-Kubo relation, or measured transport tensor.
5. Classification thresholds are provisional and must not be transferred to real materials without calibration.
6. Demonstration material names label synthetic proxies only.

## Known limitations

- No uncertainty propagation is yet included.
- No held-out experimental benchmark is included.
- No baseline comparison is included.
- No dimensional-analysis layer converts laboratory units into the normalized inputs.
- No causal claim follows from a correlation between the candidate curvature score and a measured reciprocity gap.
- Device architecture and fabrication parameters are intentionally excluded.

## Minimum validation programme

A credible empirical test should include:

1. a preregistered mapping from instrument channels to normalized descriptors;
2. calibration on one subset of samples;
3. frozen parameters and thresholds;
4. held-out evaluation on distinct samples or material families;
5. comparison against simpler statistical and physics-informed baselines;
6. uncertainty intervals and sensitivity analysis;
7. negative controls, leakage checks, and repeatability analysis;
8. publication of raw or traceably hashed measurement exports where lawful and practical.

## Interpretation rule

A numerical output from this repository is a model output. It becomes evidence about matter only after the measurement chain, calibration procedure, and independent comparison are specified.