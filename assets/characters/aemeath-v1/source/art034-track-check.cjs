const assert=require('node:assert/strict');
const {InteractionPreview:C,PANIC_ENDS,RELEASE_ENDS}=require('./art034-track.js');
assert.deepEqual(PANIC_ENDS,[60,200,340,480,620,700]);assert.deepEqual(RELEASE_ENDS,[60,160,260,380,540]);
for(const time of [0,60,199,200,339,340,479,480,619,620,699,700,1099,1100,1249,1250,1799,1800,1949,1950,2100]){
 const c=new C();c.press(0,'idle:A-open-base');const before=c.sample(time);
 if(time<700)assert(!before.key.startsWith('pose:annoyed-'));
 else assert(before.key.startsWith('pose:annoyed-'));
 assert(c.release(time,before.key));assert.equal(c.sample(time).key,before.key);assert.equal(c.sample(time+59).key,before.key);
 for(const dt of [60,159,160,259]){
  const key=c.sample(time+dt).key;
  if(time>=700)assert(key.startsWith('pose:annoyed-'));else assert(!key.startsWith('pose:annoyed-'));
  assert(require('node:fs').existsSync(__dirname+'/art034-frames/'+key.slice(5)+'.png'));
 }
 assert.equal(c.sample(time+260).key,'pose:normal-half-B');assert.equal(c.sample(time+380).key,'idle:A-open-base');assert.equal(c.sample(time+540).mode,'idle');
}
const c=new C();c.press(0,'idle:A-open-base');const held=c.sample(700).key;c.release(700,held);c.press(720,c.sample(720).key);assert.equal(c.sample(720).key,held);assert.equal(c.sample(780).key,'pose:left-panic-B');
console.log('PASS: panic has no newly introduced glyph; held/release consistency; captured first60ms; neutral cleanup; unchanged timing; actual-source regrab.');
