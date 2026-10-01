const fs=require('fs'),assert=require('assert'),{pickupAt,pickupFrames}=require('./art030-track.js');
for(const [t,index,done] of [[0,0,false],[79,0,false],[80,1,false],[159,1,false],[160,2,false],[259,2,false],[260,3,false],[359,3,false],[360,3,true],[10000,3,true]])assert.deepEqual(pickupAt(t),{index,done});
const timing=JSON.parse(fs.readFileSync(__dirname+'/art030-timing.json','utf8'));assert.deepEqual(timing.map(x=>x.durationMs),[80,80,100,100]);assert.equal(timing.reduce((s,f)=>s+f.durationMs,0),360);assert.equal(pickupFrames[3],'hold-entry');
fs.writeFileSync(__dirname+'/art030-track-check.json',JSON.stringify({status:'PASS',boundaryCases:10,durationMs:360,holdsNewEndpoint:true},null,2));console.log('PASS10 boundaries,360ms,terminal static new hold-entry');
