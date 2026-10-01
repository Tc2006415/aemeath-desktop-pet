/* ART034 source-only interaction contract; captured last-rendered PNG is authoritative. */
const PANIC_ENDS=[60,200,340,480,620,700],RELEASE_ENDS=[60,160,260,380,540];
const WING_ENDS=[400,550,1100,1250,1400],WINGS=['A','B','C','B','A'];
class InteractionPreview {
 constructor(){this.mode='idle';this.start=0;this.source='idle:A-open-base';this.idleEpoch=0;this.releaseBody='normal';this.releaseFace='normal';}
 press(t,lastRendered){this.mode='panic';this.start=t;this.source=lastRendered;}
 release(t,lastRendered){if(!['panic','held'].includes(this.mode))return false;this.mode='release';this.start=t;this.source=lastRendered;const parts=lastRendered.startsWith('pose:')?lastRendered.slice(5).split('-'):['normal','normal','A'];this.releaseBody=parts[0];this.releaseFace=parts[1]==='half'?'normal':parts[1];return true;}
 sample(t){
  let d=Math.max(0,t-this.start);
  if(this.mode==='panic'&&d>=700){this.mode='held';this.start+=700;d=t-this.start;}
  if(this.mode==='release'&&d>=540){this.mode='idle';this.idleEpoch=this.start+540;}
  if(this.mode==='idle')return {mode:'idle',key:null,local:t-this.idleEpoch};
  if(this.mode==='panic'){const i=PANIC_ENDS.findIndex(e=>d<e);return {mode:'panic',key:[this.source,'pose:left-panic-B','pose:right-panic-C','pose:left-panic-A','pose:right-panic-B','pose:transition-annoyed-C'][i],index:i,local:d};}
  if(this.mode==='held'){const p=d%1400;const i=WING_ENDS.findIndex(e=>p<e);return {mode:'held',key:'pose:annoyed-annoyed-'+WINGS[i],index:i,local:d};}
  const i=RELEASE_ENDS.findIndex(e=>d<e);return {mode:'release',key:[this.source,`pose:${this.releaseBody}-${this.releaseFace}-H`,`pose:${this.releaseBody}-${this.releaseFace}-C`,'pose:normal-half-B','idle:A-open-base'][i],index:i,local:d};
 }
 next(t){const s=this.sample(t);if(s.mode==='idle')return t+100;if(s.mode==='held'){const base=this.start+Math.floor(s.local/1400)*1400;return base+WING_ENDS.find(e=>base+e>t+.001);}return this.start+(s.mode==='panic'?PANIC_ENDS:RELEASE_ENDS).find(e=>this.start+e>t+.001);}
}
if(typeof module!=='undefined')module.exports={InteractionPreview,PANIC_ENDS,RELEASE_ENDS};
