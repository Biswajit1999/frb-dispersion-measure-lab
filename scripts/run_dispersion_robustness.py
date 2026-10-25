"""Run independent FRB robustness calculations against retained CHIME payload."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from science.dispersion_robustness import (
    cold_plasma_delay_s, dispersion_delay_sigma_s, intrachannel_smearing_ms,
    conditional_host_dm_interval,
)

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=ROOT/'data/frb20180916b-analysis.json')
    parser.add_argument('--output',type=Path,default=None)
    args = parser.parse_args()
    payload=json.loads(args.input.read_text(encoding='utf-8'))
    dm=float(payload['target']['dm'])
    dm_sigma=float(payload['target']['dm_error'])
    sight=payload['sightline']
    report={
        'provenance':{'catalog':payload['catalog']['name'],
            'source_sha256':payload.get('provenance',{}).get('source_sha256'),
            'input_path':str(args.input)},
        'target':payload['target']['name'],
        'measured_dm_pc_cm3':dm,
        'measured_dm_sigma_pc_cm3':dm_sigma,
        'delay_400_to_800_s':float(cold_plasma_delay_s(dm,400.)),
        'delay_400_to_800_sigma_dm_only_s':float(dispersion_delay_sigma_s(dm,dm_sigma,400.)),
        'channel_smearing_at_600_mhz_ms':{
            str(width):float(intrachannel_smearing_ms(dm,600.,width))
            for width in (0.1,0.4,1.0)
        },
        'foreground_assumptions':{'halo_dm_pc_cm3':[30,80],
            'igm_dm_pc_cm3':[0,40], 'source':'illustrative, not observations'},
        'conditional_host_observer_frame_dm_pc_cm3':{},
        'scope':'cold-plasma conditional diagnostics, not DM-only redshift or unique host DM',
    }
    for model in ('ne2001','ymw16'):
        disk=float(sight[model]['milky_way_disk'])
        result=conditional_host_dm_interval(dm,disk,(30,80),(0,40))
        report['conditional_host_observer_frame_dm_pc_cm3'][model]={
            'disk_dm':disk,'raw_range':[result.raw_host_min,result.raw_host_max],
            'nonnegative_range':result.feasible_host_interval,
            'assumptions_feasible':result.physical_overlap}
    text=json.dumps(report,indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(text+'\n',encoding='utf-8')
    print(text)

if __name__=='__main__':
    main()
