/* ART028 preview only. No production scheduler or native drag integration. */
class WinkPreviewEngine {
 constructor(random=Math.random){this.random=random;this.dragging=false;this.winkStart=null;this.nextWink=this.delay();this.nextBlink=4000;this.lastDelay=this.nextWink;this.lastReason='initial';}
 delay(){return 50000+Math.floor(this.random()*20000);}
 schedule(t,reason){this.lastDelay=this.delay();this.nextWink=t+this.lastDelay;this.nextBlink=t+4000;this.lastReason=reason;}
 begin(t){if(this.dragging||this.winkStart!==null)return false;this.winkStart=t;this.nextWink=Infinity;this.nextBlink=Infinity;return true;}
 press(t){this.dragging=true;this.winkStart=null;this.nextWink=Infinity;this.nextBlink=Infinity;this.lastReason='drag-interrupt';}
 release(t){if(!this.dragging)return;this.dragging=false;this.schedule(t,'drag-release');}
 update(t){
  if(this.dragging)return;
  if(this.winkStart!==null&&t>=this.winkStart+1200){const end=this.winkStart+1200;this.winkStart=null;this.schedule(end,'wink-end');}
  if(this.winkStart===null&&t>=this.nextWink)this.begin(t);
  if(this.winkStart===null&&t>=this.nextBlink+240)this.nextBlink=t+4000;
 }
 sample(t){this.update(t);const w=t%1400,ends=[400,550,700,1100,1250,1400],wings=['A','B','C','C','B','A'];let pose='open',phase='等待随机wink';
  if(this.dragging)phase='模拟拖动中 · 已回正';
  else if(this.winkStart!==null){const d=t-this.winkStart;pose=d<250?'mid':d<700?'wink':d<1050?'mid':'open';phase=d<250?'进入':d<700?'wink停留':d<1050?'回正':'稳定';}
  else if(t>=this.nextBlink){const d=t-this.nextBlink;pose=d<60?'half':d<140?'closed':d<200?'half':'open';phase='自然眨眼（4秒仅演示）';}
  return{wing:wings[ends.findIndex(e=>w<e)],pose,phase,remaining:this.nextWink-t,dragging:this.dragging,winking:this.winkStart!==null};
 }
 nextBoundary(t){this.update(t);let points=[...Array.from({length:2},(_,i)=>Math.floor(t/1400)+i).flatMap(k=>[0,400,550,700,1100,1250,1400].map(d=>k*1400+d))];
  if(this.winkStart!==null)points.push(...[250,700,1050,1200].map(d=>this.winkStart+d));else if(!this.dragging)points.push(this.nextWink,...[0,60,140,200,240].map(d=>this.nextBlink+d));
  return Math.min(...points.filter(v=>Number.isFinite(v)&&v>t+0.001));
 }
}
if(typeof module!=='undefined')module.exports=WinkPreviewEngine;
