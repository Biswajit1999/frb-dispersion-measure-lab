# Dispersion and sightline sensitivity (25 October 2026)

The independent NumPy module `science/dispersion_robustness.py` adds three calculations without changing the existing CHIME Catalog 1 source JSON or browser presentation:

1. **Cold-plasma dispersion with propagated measurement/calibration errors.** The group-delay law uses `4.148808e3 s MHz² / (pc cm⁻³)` and propagates independent DM and frequency errors by a first-order Jacobian. Shared channel/reference oscillator errors require a covariance model and are **not** represented by the independent-error calculation. A seeded Gaussian Monte Carlo test checks the local approximation.
2. **Exact finite-channel dispersive smearing.** Uses both channel edges instead of a centre-frequency approximation. The input DM is the uncorrected dispersion measure, or the magnitude of the residual DM after imperfect dedispersion. No instrumental channelization is assumed or inferred.
3. **Foreground-model conditional budgets.** Computes the observer-frame residual DM given explicit disk, halo and IGM assumptions; intersects the result with nonnegative host DM. An infeasible interval is evidence of incompatible assumptions, not a negative physical host column. The host contribution is not measured and no DM-only redshift is claimed.

## Reproduce

From repository root, with NumPy and pytest installed:

```bash
python -m pytest -q tests/test_dispersion_robustness.py
python -m scripts.run_dispersion_robustness --output outputs/frb_robustness.json
```

Catalog input values for FRB 20180916B (CHIME/FRB Catalog 1 retained analysis JSON): DM = 349.3490751229 ± 0.005841100306592 pc cm⁻³; reported disk-subtracted excesses are approximately 150.4 (NE2001) and 24.5 (YMW16) pc cm⁻³. Foreground intervals used in the tests are illustrative priors, **not** catalog measurements. A source-frame host contribution would require an independently established redshift and the factor (1+z).

This analysis is conditional on the cold-plasma approximation; scattering, profile evolution, covariant channel calibration and catalogue selection are outside scope. Do not use synthetic test outputs as astronomical detections.
