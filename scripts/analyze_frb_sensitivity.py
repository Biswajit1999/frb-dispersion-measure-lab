"""Run observationally conditional FRB diagnostics on the frozen catalog derivative.

Usage: python scripts/analyze_frb_sensitivity.py [--input data/frb20180916b-analysis.json]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research_analysis.frb_diagnostics import (  # noqa: E402
    delay_with_uncertainty, channel_smearing, foreground_sensitivity,
    stratified_percentile)


def analyze(payload: dict) -> dict:
    target, sightline = payload['target'], payload['sightline']
    dm = float(target['dm'])
    events = payload['events']
    cuts = [
        ('all_bursts', 0, 0, None),
        ('snr_ge_15', 15, 0, None),
        ('abs_b_ge_15', 0, 15, None),
        ('non_repeaters', 0, 0, False),
        ('repeaters', 0, 0, True),
    ]
    return {
        'source_sha256': payload['provenance']['source_sha256'],
        'n_catalog_events': len(events),
        'dispersion': {
            'band_400_800': delay_with_uncertainty(dm, target['dm_error'], 400, 800),
            'channel_400mhz_0p390625mhz': channel_smearing(dm, 400, .390625),
            'channel_800mhz_0p390625mhz': channel_smearing(dm, 800, .390625),
        },
        'foreground': foreground_sensitivity(
            dm,
            {'NE2001': sightline['ne2001']['milky_way_disk'],
             'YMW16': sightline['ymw16']['milky_way_disk']},
            tuple(sightline['illustrative_halo_range']),
            sightline['low_z_cosmic_mean_900z']),
        'selection_strata': {
            name: stratified_percentile(events, dm, min_snr=snr,
                                        min_abs_lat=lat, repeater=rep)
            for name, snr, lat, rep in cuts},
        'limitations': [
            'burst-level counts are not independent source counts',
            'selection strata do not correct CHIME detection efficiency',
            'Wilson bounds assume binomial sampling, not a survey selection function',
            'foreground/halo/cosmic decomposition is model-dependent',
            'channel-smearing formula assumes a top-hat frequency channel',
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=ROOT/'data/frb20180916b-analysis.json')
    parser.add_argument('--output', type=Path, default=ROOT/'results/frb_sensitivity.json')
    args = parser.parse_args()
    result = analyze(json.loads(args.input.read_text(encoding='utf-8')))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(f"wrote {args.output} using {result['n_catalog_events']} catalog bursts")

if __name__ == '__main__': main()
