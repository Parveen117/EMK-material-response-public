# CSV Screening v4

## Purpose

v4 makes the material screening workflow editable.

Instead of modifying Python code, candidate materials are stored in:

```text
data/candidate_materials_v4.csv
```

Run:

```bash
python src/emk_csv_screening_v4.py
```

Output:

```text
outputs/material_screening_v4_from_csv.csv
```

## Required CSV columns

```text
name
family
temperature_K
electric_field
temperature_gradient
strain
def_density
carrier_density
ion_mobility
symmetry_breaking
notes
```

The implementation expects `defect_density`; the abbreviated `def_density` form above is not accepted. This explicit note exists because CSV headers enjoy causing failures disproportionate to their intellectual importance.

## Descriptor boundary

The numerical descriptors are normalized screening proxies. They are not measured constants unless a row is replaced with traceable, unit-consistent, externally sourced data.

The output ranks candidates using thermoelectric, nonreciprocal, defect-activity, phase-risk, stability, and combined research-priority scores.
