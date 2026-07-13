# EMK Candidate Audit Report v7

Research-prioritization audit, not empirical validation.

## 1. GST_phase_change_proxy

    Family: phase_change

    Source-weighted priority: 0.4985
    Model priority: 0.5661
    Evidence strength: 0.2845
    Evidence count: 2
    Strongest source type: model_inference
    Source-weighted label: EARLY_STAGE_OR_LOW_SUPPORT
    Model label: NONRECIPROCAL_TRANSPORT_TARGET
    Response label: NON_RECIPROCAL_ACTIVE_MATERIAL

    Strongest functional signal: nonreciprocal:0.5954

    Warning flags:
    - weak_source_weighted_evidence
- low_evidence_coverage
- high_model_gap_needs_external_support
- phase_or_switching_risk
- low_stability_score

    Missing evidence:
    - add_at_least_three_material_specific_evidence_rows
- replace_placeholder_or_model_inference_with_external_source
- add_symmetry_or_directional_transport_evidence
- add_defect_mobility_or_defect_density_evidence
- add_switching_or_phase_stability_evidence

    Suggested next action:
    Prioritize literature/data collection before upgrading claims.

## 2. oxide_ion_conductor_proxy

    Family: defective_ion_conductor

    Source-weighted priority: 0.4850
    Model priority: 0.5462
    Evidence strength: 0.2913
    Evidence count: 2
    Strongest source type: model_inference
    Source-weighted label: EARLY_STAGE_OR_LOW_SUPPORT
    Model label: DEFECT_ACTIVE_TARGET
    Response label: NON_RECIPROCAL_ACTIVE_MATERIAL

    Strongest functional signal: defect_activity:0.6414

    Warning flags:
    - weak_source_weighted_evidence
- low_evidence_coverage
- high_model_gap_needs_external_support
- phase_or_switching_risk
- defect_dominated_signal
- low_stability_score

    Missing evidence:
    - add_at_least_three_material_specific_evidence_rows
- replace_placeholder_or_model_inference_with_external_source
- add_defect_mobility_or_defect_density_evidence
- add_switching_or_phase_stability_evidence

    Suggested next action:
    Prioritize literature/data collection before upgrading claims.

## 3. WTe2_proxy

    Family: topological_nonreciprocal

    Source-weighted priority: 0.4686
    Model priority: 0.5260
    Evidence strength: 0.2868
    Evidence count: 2
    Strongest source type: candidate_csv
    Source-weighted label: EARLY_STAGE_OR_LOW_SUPPORT
    Model label: NONRECIPROCAL_TRANSPORT_TARGET
    Response label: NON_RECIPROCAL_ACTIVE_MATERIAL

    Strongest functional signal: nonreciprocal:0.6740

    Warning flags:
    - weak_source_weighted_evidence
- low_evidence_coverage
- high_model_gap_needs_external_support

    Missing evidence:
    - add_at_least_three_material_specific_evidence_rows
- add_symmetry_or_directional_transport_evidence

    Suggested next action:
    Prioritize literature/data collection before upgrading claims.

## 4. SnSe_proxy

    Family: thermoelectric_low_dimensional

    Source-weighted priority: 0.4311
    Model priority: 0.4967
    Evidence strength: 0.2231
    Evidence count: 1
    Strongest source type: placeholder
    Source-weighted label: EARLY_STAGE_OR_LOW_SUPPORT
    Model label: THERMOELECTRIC_SCREENING_TARGET
    Response label: NON_RECIPROCAL_ACTIVE_MATERIAL

    Strongest functional signal: thermoelectric:0.6551

    Warning flags:
    - weak_source_weighted_evidence
- low_evidence_coverage

    Missing evidence:
    - add_at_least_three_material_specific_evidence_rows
- replace_placeholder_or_model_inference_with_external_source
- add_heat_charge_transport_metric

    Suggested next action:
    Collect heat-charge transport evidence such as Seebeck-like or conductivity-like descriptors.

## 5. mixed_ion_electron_proxy

    Family: mixed_transport

    Source-weighted priority: 0.4238
    Model priority: 0.4967
    Evidence strength: 0.1928
    Evidence count: 1
    Strongest source type: placeholder
    Source-weighted label: EARLY_STAGE_OR_LOW_SUPPORT
    Model label: LOW_TO_MODERATE_PRIORITY
    Response label: NON_RECIPROCAL_ACTIVE_MATERIAL

    Strongest functional signal: thermoelectric:0.5526

    Warning flags:
    - weak_source_weighted_evidence
- low_evidence_coverage

    Missing evidence:
    - add_at_least_three_material_specific_evidence_rows
- replace_placeholder_or_model_inference_with_external_source
- add_heat_charge_transport_metric

    Suggested next action:
    Collect heat-charge transport evidence such as Seebeck-like or conductivity-like descriptors.

## 6. MoS2_monolayer_proxy

    Family: broken_symmetry_2D

    Source-weighted priority: 0.4177
    Model priority: 0.4831
    Evidence strength: 0.2105
    Evidence count: 1
    Strongest source type: placeholder
    Source-weighted label: EARLY_STAGE_OR_LOW_SUPPORT
    Model label: NONRECIPROCAL_TRANSPORT_TARGET
    Response label: NON_RECIPROCAL_ACTIVE_MATERIAL

    Strongest functional signal: nonreciprocal:0.5843

    Warning flags:
    - weak_source_weighted_evidence
- low_evidence_coverage
- high_model_gap_needs_external_support

    Missing evidence:
    - add_at_least_three_material_specific_evidence_rows
- replace_placeholder_or_model_inference_with_external_source
- add_symmetry_or_directional_transport_evidence

    Suggested next action:
    Search for directional transport, symmetry-breaking, or nonreciprocal response evidence.

## 7. ferroelectric_proxy

    Family: ferroelectric

    Source-weighted priority: 0.4042
    Model priority: 0.4630
    Evidence strength: 0.2180
    Evidence count: 1
    Strongest source type: placeholder
    Source-weighted label: EARLY_STAGE_OR_LOW_SUPPORT
    Model label: LOW_TO_MODERATE_PRIORITY
    Response label: NON_RECIPROCAL_ACTIVE_MATERIAL

    Strongest functional signal: nonreciprocal:0.5418

    Warning flags:
    - weak_source_weighted_evidence
- low_evidence_coverage

    Missing evidence:
    - add_at_least_three_material_specific_evidence_rows
- replace_placeholder_or_model_inference_with_external_source

    Suggested next action:
    Search for directional transport, symmetry-breaking, or nonreciprocal response evidence.

## 8. Bi2Te3_proxy

    Family: thermoelectric

    Source-weighted priority: 0.3944
    Model priority: 0.4469
    Evidence strength: 0.2281
    Evidence count: 1
    Strongest source type: placeholder
    Source-weighted label: EARLY_STAGE_OR_LOW_SUPPORT
    Model label: THERMOELECTRIC_SCREENING_TARGET
    Response label: OPEN_MATERIAL_RESPONSE_FIELD

    Strongest functional signal: thermoelectric:0.7106

    Warning flags:
    - weak_source_weighted_evidence
- low_evidence_coverage

    Missing evidence:
    - add_at_least_three_material_specific_evidence_rows
- replace_placeholder_or_model_inference_with_external_source
- add_heat_charge_transport_metric

    Suggested next action:
    Collect heat-charge transport evidence such as Seebeck-like or conductivity-like descriptors.

## 9. strained_SiGe_proxy

    Family: strained_semiconductor

    Source-weighted priority: 0.3259
    Model priority: 0.3663
    Evidence strength: 0.1979
    Evidence count: 1
    Strongest source type: placeholder
    Source-weighted label: EARLY_STAGE_OR_LOW_SUPPORT
    Model label: LOW_TO_MODERATE_PRIORITY
    Response label: DEFECT_STRAIN_SENSITIVE_MATERIAL

    Strongest functional signal: thermoelectric:0.5038

    Warning flags:
    - weak_source_weighted_evidence
- low_evidence_coverage

    Missing evidence:
    - add_at_least_three_material_specific_evidence_rows
- replace_placeholder_or_model_inference_with_external_source

    Suggested next action:
    Collect heat-charge transport evidence such as Seebeck-like or conductivity-like descriptors.

## 10. Si_reference

Family: semiconductor_reference

Source-weighted priority: 0.2855
Model priority: 0.2191
Evidence strength: 0.4959
Evidence count: 1
Strongest source type: control
Source-weighted label: EARLY_STAGE_OR_LOW_SUPPORT
Model label: LOW_TO_MODERATE_PRIORITY
Response label: RECIPROCAL_STABLE_MATERIAL

Strongest functional signal: thermoelectric:0.4133

Warning flags:
- low_evidence_coverage

Missing evidence:
- add_at_least_three_material_specific_evidence_rows

Suggested next action:
Collect heat-charge transport evidence such as Seebeck-like or conductivity-like descriptors.
