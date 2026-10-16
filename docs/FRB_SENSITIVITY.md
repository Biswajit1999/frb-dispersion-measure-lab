# Cold-plasma uncertainty and catalog selection sensitivity

Reproduce with `python scripts/analyze_frb_sensitivity.py`. The script reads the **already committed** CHIME Catalog 1 derivative, writes `results/frb_sensitivity.json`, and makes no network calls. Run tests using `python -m unittest discover -s tests -p 'test_frb_diagnostics.py' -v`.

Three independent diagnostic families are implemented:

1. **Frequency/DM uncertainty:** Δt = K DM (ν_low⁻² − ν_high⁻²) with K=4.148808×10³ s MHz² (pc cm⁻³)⁻¹. The uncertainty calculation propagates independent DM and band-edge errors by analytic derivatives. Channel smearing is the exact sweep across an assumed top-hat channel, compared against the narrow-channel approximation. It is not an observed pulse broadening measurement.
2. **Foreground assumptions:** For each catalogued Galactic-disk model, subtract an illustrative halo interval (30–80 pc cm⁻³) and optionally the pre-existing low-z `900 z` cosmic reference. Keep **negative residuals** visible; clipping would conceal model tension. These residuals cannot be interpreted as unique host or IGM DM measurements.
3. **Catalog selection:** Compute burst-level empirical DM percentiles for explicit SNR, Galactic-latitude, and repeater cuts. Report counts and Wilson intervals as descriptive sampling diagnostics. These are not selection-function-corrected population percentiles. Multiple bursts from a repeating source are not independent.

No new FRB detection, redshift, progenitor inference or statistically independent source-population claim follows from this analysis. Existing source data, browser output, and reference results remain unchanged.
