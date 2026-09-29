const assert=require('assert'),fs=require('fs');const {InteractionPreview}=require('./art032-track.js');let checks=0;
function eq(a,b){assert.deepStrictEqual(a,b);checks++}
for(const [t,key] of [[0,'idle:C-wink-upper'],[59,'idle:C-wink-upper'],[60,'pose:left-panic-B'],[199,'pose:left-panic-B'],[200,'pose:right-panic-C'],[340,'pose:left-panic-A'],[480,'pose:right-panic-B'],[620,'pose:annoyed-annoyed-C'],[699,'pose:annoyed-annoyed-C'],[700,'pose:annoyed-annoyed-A']]){const e=new InteractionPreview();e.press(0,'idle:C-wink-upper');eq(e.sample(t).key,key);}
for(const t of [700,2099,2100,7000,60000]){const e=new InteractionPreview();e.press(0,'idle:A-open-base');const s=e.sample(t);eq(s.mode,'held');assert(s.key.startsWith('pose:annoyed-annoyed-'));checks++;}
for(const [t,captured]of [[1,'idle:C-wink-upper'],[240,'pose:right-panic-C'],[1500,'pose:annoyed-annoyed-B']]){
 const e=new InteractionPreview();e.press(0,'idle:A-open-base');e.sample(t);eq(e.release(t,captured),true);eq(e.sample(t).key,captured);eq(e.sample(t+59).key,captured);eq(e.sample(t+60).mode,'release');eq(e.sample(t+539).key,'idle:A-open-base');eq(e.sample(t+540).mode,'idle');eq(e.idleEpoch,t+540);eq(e.release(t+541,captured),false);
}
const e=new InteractionPreview();e.press(0,'idle:A-open-base');e.release(250,'pose:left-panic-B');e.press(300,'pose:left-panic-B');eq(e.sample(301).mode,'panic');eq(e.sample(301).key,'pose:left-panic-B');eq(e.sample(1000).mode,'held');
const keys=new Set([...fs.readdirSync(__dirname+'/art032-frames').filter(n=>n.endsWith('.png')).map(n=>'pose:'+n.slice(0,-4)),...fs.readdirSync(__dirname+'/art029-frames').filter(n=>n.endsWith('.png')).map(n=>'idle:'+n.slice(0,-4))]);
for(const key of keys){const x=new InteractionPreview();x.press(0,key);x.release(1,key);for(const dt of [0,60,160,260,380]){assert(keys.has(x.sample(1+dt).key),'missing release image from '+key);checks++;}}
fs.writeFileSync(__dirname+'/art032-track-check.json',JSON.stringify({status:'PASS',checks,panicMs:700,heldUntilRelease:true,releaseMs:540,capturedFrameEntry:true,repressCancelsRelease:true},null,2));console.log('PASS',checks,'targeted transition/boundary checks');
