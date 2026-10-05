"""Derive the browser payload from the public CHIME/FRB Catalog 1 JSON."""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data'/'chime-catalog-1.json'
OUTPUT=ROOT/'data'/'frb20180916b-analysis.json'
K_DM_SECONDS=4.148808e3

def scalar(value):
    if isinstance(value,list): return value[0] if value else None
    return value

def main():
    rows=json.loads(SOURCE.read_text(encoding='utf-8'))
    compact=[]
    for r in rows:
        dm=float(r['fitburst_dm'])
        compact.append({'name':r['tns_name'],'dm':round(dm,4),'snr':round(float(r['fitburst_snr']),2),'repeater':bool(r.get('repeater_of')),'galactic_latitude':round(float(r['gb']),3)})
    target=next(r for r in rows if r['tns_name']=='FRB20180916B')
    dm=float(target['fitburst_dm']); dm_error=float(target['fitburst_dm_error'])
    dms=np.array([r['dm'] for r in compact])
    bins=np.linspace(100,3100,31); counts,edges=np.histogram(dms,bins=bins)
    frequencies=np.linspace(400,800,161)
    delays=K_DM_SECONDS*dm*(frequencies**-2-800**-2)
    excess_ne=float(target['dm_excess_ne2001']); excess_ymw=float(target['dm_excess_ymw16'])
    z=0.0337; cosmic_mean=900*z
    payload={
      'schema_version':'2.0.0',
      'catalog':{'name':'CHIME/FRB Catalog 1','events':len(rows),'dm_min':float(dms.min()),'dm_median':float(np.median(dms)),'dm_max':float(dms.max()),'repeater_bursts':sum(r['repeater'] for r in compact),'paper_doi':'10.3847/1538-4365/ac33ab'},
      'target':{'name':'FRB 20180916B','dm':dm,'dm_error':dm_error,'snr':float(target['fitburst_snr']),'pulse_width_ms':1000*float(scalar(target['pulse_width_ms'])),'scattering_time_ms':1000*float(target['scattering_time_ms']),'peak_frequency_mhz':float(scalar(target['peak_frequency'])),'ra_deg':float(target['ra']),'dec_deg':float(target['dec']),'galactic_l_deg':float(target['gl']),'galactic_b_deg':float(target['gb']),'host_redshift':z,'activity_period_days':16.35,'catalog_percentile':float(100*np.mean(dms<=dm))},
      'sweep':[{'frequency_mhz':round(float(f),2),'delay_from_800_s':round(float(t),6)} for f,t in zip(frequencies,delays)],
      'histogram':[{'lo':float(edges[i]),'hi':float(edges[i+1]),'count':int(counts[i])} for i in range(len(counts))],
      'events':compact,
      'sightline':{
        'observed_dm':dm,
        'ne2001':{'milky_way_disk':dm-excess_ne,'excess_after_disk':excess_ne},
        'ymw16':{'milky_way_disk':dm-excess_ymw,'excess_after_disk':excess_ymw},
        'illustrative_halo_range':[30,80],
        'low_z_cosmic_mean_900z':cosmic_mean,
        'warning':'NE2001 and YMW16 produce very different foreground estimates at Galactic latitude +3.73 degrees. A unique host or IGM DM is not inferred.'},
      'provenance':{'catalog_url':'https://raw.githubusercontent.com/FRBs/FRB/main/frb/data/FRBs/CHIME_catalog-2021-1-27.json','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'retrieved_utc':'2026-10-05','host_source':'Marcote et al. 2020, Nature 577, 190-194, doi:10.1038/s41586-019-1866-z'},
      'scope':{'measured':['total DM','DM uncertainty','sky position','burst S/N and profile quantities'],'derived':['cold-plasma delay curve','catalog percentile','two catalogued Galactic-model foregrounds'],'not_inferred':['unique IGM column','unique host contribution','DM-only redshift','progenitor mechanism']}
    }
    OUTPUT.write_text(json.dumps(payload,indent=2),encoding='utf-8')
    print(json.dumps({'events':len(rows),'median_dm':float(np.median(dms)),'target_percentile':payload['target']['catalog_percentile'],'delay_400_to_800_s':float(delays[0]),'NE2001_excess':excess_ne,'YMW16_excess':excess_ymw},indent=2))
if __name__=='__main__':main()
