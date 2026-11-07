# Conditional dispersion robustness (7 November 2026)

Run `cd research && python -m unittest -v test_dispersion_robustness.py` with Python 3.10+ (no third-party packages).

Using the catalogued FRB 20180916B DM = 349.349 ± 0.006 pc cm⁻³, the 400–800 MHz cold-plasma sweep is 6.793977778 s and its propagated **DM-only** 1σ uncertainty is 0.000116685 s. Frequencies are treated as exact; this excludes burst-structure, instrumental and calibration errors.

For illustration, inferred Galactic disk columns of 198.949 (NE2001) and 324.849 (YMW16) pc cm⁻³ combined with assumed halo columns of 30 and 80 pc cm⁻³ yield remaining columns of [120.4, 70.4, −5.5, −55.5] pc cm⁻³. Negative residuals flag incompatible assumptions, not negative physical plasma. The remaining column is not an IGM measurement, host DM, or redshift.

Synthetic/conditional sensitivity calculations only. AI-assisted coding; scientific interpretation and review required before merging.
