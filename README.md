# FRB Dispersion Measure Lab

Cold-plasma sweep, dynamic spectra and host/IGM DM decomposition.

Created and maintained by Biswajit Jana.

## Scientific Purpose

This zero-build browser laboratory puts a compact reference-data bundle in front of the simulation. The app loads `data/reference.json`, renders those published anchors first, then sends the adjustable model to `physicsWorker.js` so numerical work stays off the UI thread.

## Architecture

- `index.html`: mission-control interface.
- `styles.css`: dense dark scientific dashboard.
- `app.js`: UI state, Canvas rendering and worker orchestration.
- `physicsWorker.js`: numerical model and heatmap generation.
- `data/reference.json`: small auditable reference-data bundle.
- `scripts/validate.js`: no-dependency repository validation.

## Run

```bash
python -m http.server 8080
```

Open `http://localhost:8080`.

## Validate

```bash
npm run check
```

The validation script checks required files, JSON reference data, worker syntax, citations and absence of unfinished scaffold tokens.

## Reference Data

Small browser bundle of published FRB discovery DMs used as validation anchors for the cold-plasma law.

## References

- Lorimer, D.R. et al., 2007. A bright millisecond radio burst of extragalactic origin. Science, 318(5851), pp.777-780.
- Petroff, E., Hessels, J.W.T. and Lorimer, D.R., 2019. Fast radio bursts. Astronomy and Astrophysics Review, 27(1), p.4.
