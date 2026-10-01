const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync(__dirname+'/art027-demo.html','utf8');
const logic=html.slice(html.indexOf('const wingEnds='),html.indexOf('let combined=false'));
const c={};vm.createContext(c);vm.runInContext(logic+'\nthis.sample=sample;this.boundary=boundary;',c);
const cases=[[759,'open'],[760,'half'],[819,'half'],[820,'closed'],[899,'closed'],[900,'half'],[959,'half'],[960,'open'],[999,'open'],[1000,'open']];
for(let k=0;k<7;k++)for(const [t,eye]of cases)assert.equal(c.sample(t+k*4000,true).eye,eye);
const timing=JSON.parse(fs.readFileSync(__dirname+'/art026-timing.json','utf8'))['idle-soft'];
for(let t=0;t<28000;t++){let r=t%1400,f;for(f of timing){if(r<f.durationMs)break;r-=f.durationMs;}const wing={'frames/neutral.png':'A','frames/soft-light.png':'B','frames/soft-peak.png':'C'}[f.path];assert.equal(c.sample(t,true).wing,wing);assert.equal(c.sample(t,false).wing,'A');}
assert.equal(c.boundary(760,1,true),820);assert.equal(c.boundary(820,-1,true),760);assert.equal(c.boundary(0,-1,true),0);
const result={status:'PASS',independentWingSamples:28000,blinkBoundaryCases:70,stepChecks:3,cycleMs:240,startIntervalMs:4000};fs.writeFileSync(__dirname+'/art027-timing-check.json',JSON.stringify(result,null,2));console.log(result);
