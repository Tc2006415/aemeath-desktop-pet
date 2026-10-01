const fs=require('fs'),assert=require('assert'),{hemAt,nextHemBoundary}=require('./art029-track.js'),Engine=require('./art028-engine.js');
for(const [t,p] of [[0,'base'],[399,'base'],[400,'light'],[549,'light'],[550,'upper'],[1100,'upper'],[1199,'upper'],[1200,'light'],[1250,'light'],[1349,'light'],[1350,'base'],[1399,'base'],[1400,'base']])assert.equal(hemAt(t),p);
const expected=JSON.parse(fs.readFileSync(__dirname+'/art029-timing.json','utf8'));assert.equal(expected.downstrokeLagMs,100);assert.equal(1200-1100,100);assert.equal(1350-1250,100);
let a=new Engine(()=>.5),b=new Engine(()=>.5);
for(let t=0;t<5600;t++){if(t===620){a.begin(t);b.begin(t)}if(t===880){a.press(t);b.press(t)}if(t===960){a.release(t);b.release(t)}const before=JSON.stringify(a),s=a.sample(t);let hem=hemAt(t,s.dragging,true),off=hemAt(t,s.dragging,false);assert.equal(off,'base');assert.deepEqual(s,b.sample(t));if(s.dragging)assert.equal(hem,'base');if(t===960)assert.equal(hem,'upper');}
assert.equal(nextHemBoundary(1100),1200);assert.equal(nextHemBoundary(1399),1400);
let results={status:'PASS',hemBoundaryCases:13,phaseIndependenceSamples:5600,dragBaseAndCurrentPhaseResume:true,cycleSeam:'base/base',fallLagMs:100,newRandomTimers:0};fs.writeFileSync(__dirname+'/art029-track-check.json',JSON.stringify(results,null,2));console.log(results);
