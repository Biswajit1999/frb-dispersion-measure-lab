# FRB 20180916B: cold-plasma and foreground sensitivity audit (2026-10-31)

Run `python scripts/run_dm_sensitivity.py --output /tmp/frb-dm-audit.json` from the repository root. This uses the existing, pinned `data/frb20180916b-analysis.json`; no catalogue is downloaded or modified. Tests: `python -m pytest -q tests/test_dm_sensitivity.py`.

Three distinct checks: (1) analytic first-order propagation of the fitted DM uncertainty and two **alternative** frequency-edge calibration models into delay, (2) reference-frequency invariance and the rank-one cross-band covariance caused by the same fitted DM, and (3) algebraic foreground-model and halo-range sensitivity. The dispersion constant is 4.148808 × 10³ s MHz² (pc cm⁻³)⁻¹; delay is K·DM·(ν_low⁻² − ν_high⁻²). The shared-DM covariance is σ_DM²·g·gᵀ, not diagonal. The illustrative 0.1 MHz edge uncertainty is **not** a measured CHIME calibration error.

The foreground budget subtracts the catalogue's NE2001 or YMW16 disk estimate, an **assumed** 30–80 pc cm⁻³ halo, and the purely illustrative low-z mean-IGM proxy 900z. Negative algebraic leftovers are model inconsistency flags, not negative physical host contributions. This exercise does not infer a unique IGM, host, redshift, scattering model, or progenitor. Its uncertainties omit covariance in the fitted DM and frequency calibration, foreground-model systematic uncertainty, host inclination, and cosmic variance.

Primary provenance remains the CHIME/FRB Catalog 1 SHA-256 recorded in the existing JSON, with the original source and Marcote et al. (2020) cited in the repository README. This research module is intentionally separate from the public interface and does not change the published headline.
