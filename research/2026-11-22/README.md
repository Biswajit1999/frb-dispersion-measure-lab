# Conditional DM bandpass and foreground sensitivity — 2026-11-22

Run: `python research/2026-11-22/conditional_dm.py`.

Three diagnostics: cold-plasma differential delay between supplied MHz band edges, first-order propagation of reported DM uncertainty into that delay, and a conservative envelope over multiple Galactic disk models and a user-supplied halo-DM interval. The dispersion constant is 4.148808e-3 seconds GHz² per pc cm⁻³. Band edges are assumed exact, the cold-plasma ν⁻² approximation is used, and reported DM uncertainty is not an independent estimate of foreground-model uncertainty. The halo interval is an assumption, not measured from this sightline. The remainder includes host, IGM and other contributions and can be negative under incompatible assumptions; it is not an IGM or host measurement.

Scientific interpretation and tests were prepared with AI coding assistance; Biswajit Jana is the requested sole authenticated Git author. The CHIME catalogue and existing results remain unchanged.
