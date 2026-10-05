const fs=require('node:fs'),crypto=require('node:crypto');const fail=[];
for(const f of ['index.html','styles.css','app.js','README.md','data/chime-catalog-1.json','data/frb20180916b-analysis.json','scripts/derive_chime_catalog.py'])if(!fs.existsSync(f))fail.push(f+' missing');
const d=JSON.parse(fs.readFileSync('data/frb20180916b-analysis.json'));if(d.catalog.events!==535)fail.push('catalog record count');if(d.events.length!==535)fail.push('compact event count');if(d.sweep.length!==161)fail.push('sweep samples');if(Math.abs(d.target.dm-349.3490751229)>1e-8)fail.push('target DM');
const hash=crypto.createHash('sha256').update(fs.readFileSync('data/chime-catalog-1.json')).digest('hex');if(hash!==d.provenance.source_sha256)fail.push('catalog hash');
if(fail.length){console.error(fail.join('\n'));process.exit(1)}console.log('FRB validation passed: 535 events, verified catalog hash and 161-point dispersion curve.');
