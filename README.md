# FRB Dispersion Measure Lab

Cold-plasma sweep, dynamic spectra and host/IGM DM decomposition.

Created and maintained by Biswajit Jana.

## Scientific Purpose

This zero-build browser laboratory puts a compact reference-data bundle in front of the simulation. The app loads `data/reference.json`, renders those published anchors first, then sends the adjustable model to `physicsWorker.js` so numerical work stays off the UI thread.

## Scientific Background

### Fast radio bursts

Fast radio bursts (FRBs) are millisecond-duration pulses of radio emission, first identified by Lorimer et al. (2007) in archival Parkes pulsar-survey data. Individual bursts release roughly the energy the Sun radiates over days to years, in a flash lasting only a few milliseconds, and the overwhelming majority of well-localized sources are extragalactic. Their physical origin is still debated; magnetars are the leading progenitor candidate for at least some FRBs, but the population is likely not fully explained by a single mechanism. Wide-field radio instruments such as CHIME (Canada) and ASKAP (Australia) now detect FRBs at a rate of many per day, building up large catalogues of burst arrival times, fluences and, crucially, dispersion measures.

### Cold-plasma dispersion

Radio waves traveling through an ionized medium (the interstellar medium of our Galaxy, the intergalactic medium, and the host galaxy of the burst) are dispersed: lower-frequency photons are delayed relative to higher-frequency photons because the group velocity of light in a cold, tenuous plasma depends on frequency. For a plasma of free-electron density `n_e`, the group delay between two observing frequencies `nu_lo` and `nu_hi` (in the standard low-frequency, non-relativistic-plasma approximation) is

```
t(nu) - t(nu_ref) = k_DM * DM * (nu^-2 - nu_ref^-2)
```

where `k_DM ≈ 4.148808e3 MHz^2 pc^-1 cm^3 s` is the standard dispersion constant, and DM is the dispersion measure — the electron column density integrated along the line of sight:

```
DM = ∫ n_e dl   [pc cm^-3]
```

The characteristic `nu^-2` scaling is the observational fingerprint that lets a real burst be distinguished from radio-frequency interference: a genuine astrophysical pulse sweeps from high to low frequency following exactly this power law, and DM is measured by fitting that sweep.

### DM as a probe of the intergalactic medium

Because DM adds along the whole line of sight, it is a sum of contributions from the Milky Way's interstellar medium, the host galaxy's interstellar medium (divided by `1+z` for cosmological redshifting), and the intergalactic medium (IGM) the burst crosses on its way to us:

```
DM_obs = DM_MW + DM_host / (1 + z) + DM_IGM(z)
```

Because most of the baryons in the universe are believed to reside in the diffuse, highly ionized IGM (rather than in stars or galaxies), `DM_IGM` grows statistically with redshift and can be used as a census of otherwise-invisible baryonic matter — the "missing baryons" problem. Macquart et al. (2020) established this DM–redshift relation observationally using a sample of localized FRBs with independently measured host-galaxy redshifts, showing that the mean `DM_IGM(z)` tracks the cosmic baryon density as expected from cosmological simulations, turning FRBs into practical tools for IGM cosmography.

### Surveys

CHIME (a stationary radio telescope in British Columbia operating at 400-800 MHz) and ASKAP (a phased-array-feed interferometer in Western Australia) are the two instruments currently producing the bulk of new, well-characterized FRB detections, including the localizations that make DM-redshift studies possible.

## How It Works

This is a client-side, zero-build simulation lab: everything runs in the browser with no server-side compute.

1. `app.js` defines the lab's control set (DM, reference frequency, intrinsic pulse width, scattering index), builds the slider UI, and on load fetches `data/reference.json` — a small bundle of published DM anchor points (see below) — which are drawn on the plot as fixed reference markers.
2. Whenever a control changes, `app.js` posts the current parameters to `physicsWorker.js`, a dedicated Web Worker, so the numerical model runs off the main UI thread and the interface stays responsive.
3. Inside the worker, the `frb(p)` function evaluates the cold-plasma dispersion law `t(nu) = k_DM * DM * (nu^-2 - nu_ref^-2)` across a 500-point frequency sweep from 350-1800 MHz, using the exact dispersion constant `4.148808e3`. It also computes a small set of summary metrics (delay at 400 MHz, delay at 800 MHz, intrinsic width) and a 96x96 heatmap approximating a frequency-time dynamic spectrum sweep, shaped by the intrinsic pulse width parameter.
4. The worker posts the resulting series, metrics and heatmap back to the main thread, where `app.js` renders the dispersion curve against the published reference anchors on a Canvas plot, colors the heatmap panel, and updates the telemetry readout.
5. `research-overlay.js` adds a lightweight, non-invasive status panel reflecting the validation/quality checks described in `RESEARCH_QUALITY.md`.

Note: `physicsWorker.js` is a shared worker module that also implements simulation kernels for several other unrelated labs (CMB spectrum, supernova cosmology, microlensing, galaxy rotation curves, asteroseismology, weak lensing, spectrograph precision, clustering, exoplanet atmospheres). Only the `frb` function is used by this app; the rest of the file is inert here and is inherited from a shared multi-lab worker template.

## Usage

```bash
python -m http.server 8080
```

Open `http://localhost:8080` and use the sliders to adjust DM, reference frequency, intrinsic pulse width and scattering index. The dispersion curve and heatmap update live; the four yellow markers are the published DM=557 pc cm^-3 reference anchors loaded from `data/reference.json`.

## Validate

```bash
npm run check
```

The validation script (`scripts/validate.js`) checks required files, JSON reference data, worker syntax, citations and absence of unfinished scaffold tokens.

```bash
npm run validate:research
```

Runs `scripts/validate_repository.mjs` against `data/research-reference.json`, a separate small set of benchmark anchors used purely for repository-quality checks (see `RESEARCH_QUALITY.md`).

## Architecture

- `index.html`: mission-control interface.
- `styles.css`: dense dark scientific dashboard.
- `app.js`: UI state, Canvas rendering and worker orchestration.
- `physicsWorker.js`: numerical model and heatmap generation.
- `data/reference.json`: small auditable reference-data bundle (published DM anchors).
- `data/research-reference.json`: benchmark anchors used by the repository-quality validator.
- `scripts/validate.js`: no-dependency repository validation.
- `scripts/validate_repository.mjs`: research-quality/reference-anchor validator.
- `research-overlay.js`: non-invasive quality/status panel.

## Reference Data

Small browser bundle of published FRB discovery DMs used as validation anchors for the cold-plasma law: four points at DM = 557 pc cm^-3, giving the predicted delay at 400, 600, 800 and 1200 MHz relative to a 1600 MHz reference frequency, computed from the same `k_DM * DM * (nu^-2 - nu_ref^-2)` law implemented in the worker.

## Math Appendix

Dispersion delay between two frequencies:

```
Δt = k_DM * DM * (ν_lo^-2 - ν_hi^-2)
k_DM = 4.148808e3   MHz^2 pc^-1 cm^3 s
```

Total observed dispersion measure as a sum of Galactic, host and intergalactic contributions:

```
DM_obs = DM_MW + DM_host / (1 + z) + DM_IGM(z)
```

Dispersion measure as an electron-density line integral:

```
DM = ∫ n_e dl      [pc cm^-3]
```

## References

- Lorimer, D.R. et al., 2007. A bright millisecond radio burst of extragalactic origin. Science, 318(5851), pp.777-780.
- Petroff, E., Hessels, J.W.T. and Lorimer, D.R., 2019. Fast radio bursts. Astronomy and Astrophysics Review, 27(1), p.4.
- Macquart, J.-P. et al., 2020. A census of baryons in the Universe from localized fast radio bursts. Nature, 581, pp.391-395.

## Research Quality Upgrade

See [RESEARCH_QUALITY.md](RESEARCH_QUALITY.md) for the validation layer, reference anchors, equations and research boundaries added to this repository.
