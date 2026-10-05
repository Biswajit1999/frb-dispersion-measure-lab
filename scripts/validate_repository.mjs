import fs from 'node:fs';const d=JSON.parse(fs.readFileSync('data/frb20180916b-analysis.json'));const f=[];
const delay=d.sweep[0].delay_from_800_s;if(Math.abs(delay-6.793979)>.00001)f.push('dispersion regression');if(Math.abs(d.catalog.dm_median-533.1118)>.001)f.push('catalog median');if(!(d.target.catalog_percentile>24&&d.target.catalog_percentile<25))f.push('percentile');
const spread=d.sightline.ne2001.excess_after_disk-d.sightline.ymw16.excess_after_disk;if(spread<120)f.push('foreground disagreement missing');if(!d.scope.not_inferred.includes('DM-only redshift'))f.push('claim boundary');
if(f.length){console.error(f.join('\n'));process.exit(1)}console.log('Research validation passed: law, population, foreground disagreement and claim boundary verified.');
