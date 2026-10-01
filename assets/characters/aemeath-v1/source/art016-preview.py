"""Self-contained ART-016 timing probe. Never creates or changes sprite pixels."""
import base64
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
names={'mid':'art013-package/frames/hold-half.png','b2':'art015-b2-v1-96.png','b4':'art014-v1-96.png','b7':'art015-b7-v1-96.png','up':'art013-package/frames/hold-up-half.png','down':'art013-package/frames/hold-down-half.png','closed':'art013-package/frames/hold-mid-closed.png','neutral':'art013-package/frames/neutral.png','surprise':'art013-package/frames/hold-surprise.png','pickup':'art013-package/frames/pickup-surprise.png','rclosed':'art013-package/frames/release-closed.png','rhalf':'art013-package/frames/release-half.png'}
images={k:'data:image/png;base64,'+base64.b64encode((ROOT/v).read_bytes()).decode() for k,v in names.items()}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
evidence={'sources':{k:{'path':v,'sha256':sha(ROOT/v)} for k,v in names.items()},'imagegenCalls':0,'pixelEdits':0,'nativeRoutingImplemented':False,'timingStatus':'PM-authorized probe, not frozen contract'}
protected=[ROOT.parent/'manifest.json',*sorted((ROOT.parent/'frames').glob('*.png')),*sorted(ROOT.glob('art014-*')),*sorted(ROOT.glob('art015-*')),*sorted((ROOT/'art013-package').rglob('*.*'))]
before={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
cycle=[['mid',80],['b2',50],['b4',50],['b7',50],['up',100],['b7',50],['b4',50],['b2',50],['mid',60],['down',180]]
hold=cycle+[x[:] for x in cycle];hold[18]=['closed',60]
release=[['mid',80],['rclosed',100],['rhalf',120],['neutral',160]]
pickup=[['neutral',80],['surprise',80],['pickup',100],['mid',100]]
routes={k:[[k,40]]+[[b,40] for b in remaining]+release for k,remaining in {'up':['b7','b4','b2'],'b7':['b4','b2'],'b4':['b2'],'b2':[],'down':[],'mid':[]}.items()}
data={'hold':hold,'release':release,'pickup':pickup,'routes':routes}
assert sum(x[1] for x in cycle)==720 and sum(x[1] for x in hold)==1440 and sum(x[1] for x in release)==460
assert [i for i,x in enumerate(hold) if x[0]=='closed']==[18]
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ART-016 动态探针 · 网页模拟</title>
<style>body{font:15px system-ui;margin:16px;background:#eee;color:#202630}button,select,input{font:inherit;padding:6px;margin:3px}img{image-rendering:pixelated}h1{font-size:22px;margin:8px 0}.stage{display:flex;gap:10px;align-items:flex-start}.box{background:#f0efeb;padding:8px}.dark{background:#1d222c;color:white}.big{width:288px;height:312px}#status,#events{background:white;padding:8px;font-variant-numeric:tabular-nums}.strip{display:flex;gap:4px;flex-wrap:wrap}.tile{font-size:12px}.tile img{width:48px;height:52px;display:block}p{margin:7px 0}</style>
<h1>ART-016 · 往返与收翼动态探针</h1>
<p>仅网页模拟，真实宿主按源帧选路尚未实现。固定图片位置、无插值/淡化/位移；位置冻结只用坐标数值模拟。时序尚未冻结。</p>
<select id="mode" aria-label="探针情境"><option value="hold">连续扇翼 · 两周期一次眨眼</option><option value="up">上扬松手</option><option value="b7">B7松手</option><option value="b4">B4松手</option><option value="b2">B2松手</option><option value="down">下压松手</option><option value="mid">中位松手</option><option value="quick">40ms快松手 · 固定R回退</option><option value="regrab">上扬松手后80ms重抓</option><option value="manual">手动输入模拟</option></select>
<button id="replay">重播</button><button id="pause">暂停</button><button id="step">下一项</button><button id="press">按下</button><button id="release">松手</button>
<p><label>定位时间ms <input id="time" type="number" value="0" min="0" max="10000"></label><button id="seek">定位并暂停</button><span id="count"></span></p>
<p id="status"></p><div class="stage"><div class="box">浅底3×<br><img id="light" class="big"></div><div class="box dark">深底3×<br><img id="dark" class="big"></div><div class="box">浅底1×<br><img id="one"></div><div class="box dark">深底1×<br><img id="oneDark"></div></div>
<p id="events"></p><p>源翼40ms → 剩余B级各40ms → 既有R460ms；下压/中位源40ms后直接R。快松手pickup源帧选路未实现，明确用既有R回退。重抓立即重新pickup。</p>
<p>暂停项检查（点击任一项）；hold的20项合1440ms，第19项闭眼60ms。</p><div id="strip" class="strip"></div>
<script>
const data=DATA,images=IMAGES,mode=document.querySelector('#mode');
let paused=false,elapsed=0,epoch=performance.now(),manual=[],trace=[],lastKey='',nowState;
const sum=a=>a.reduce((s,x)=>s+x[1],0);
function at(seq,t,loop=false){let local=loop?t%sum(seq):t,start=0;for(let i=0;i<seq.length;i++){if(local<start+seq[i][1])return {frame:seq[i][0],index:i,local,start,duration:seq[i][1]};start+=seq[i][1]}return {frame:'neutral',index:seq.length,local,start,duration:1000};}
function resolve(t){let m=mode.value,phase='hold',seq=data.hold,start=0,held=true,freeze=null;
 if(m==='hold')return {...at(seq,t,true),phase,seq,start,held,freeze,cycles:Math.floor(t/720)};
 if(m==='manual'){
  phase='idle';seq=[['neutral',1000]];held=false;
  for(const event of manual){if(event.t>t)break;
   if(event.type==='down'){phase='pickup';seq=data.pickup;start=event.t;held=true;freeze=null}
   else {let source=phase==='pickup'&&event.t-start>=360?at(data.hold,event.t-start-360,true).frame:at(seq,event.t-start,phase==='hold').frame;phase=data.routes[source]?'release':'release-fallback';seq=data.routes[source]||data.release;start=event.t;held=false;freeze=event.t;}
  }
  if(phase==='pickup'&&t-start>=360){start+=360;phase='hold';seq=data.hold;}
 }else if(m==='quick'){
  if(t<400){phase='idle';seq=[['neutral',400]];held=false}
  else if(t<440){phase='pickup';seq=data.pickup;start=400}
  else{phase='release-fallback';seq=data.release;start=440;held=false;freeze=440}
 }else{
  const source=m==='regrab'?'up':m;
  if(t<400){phase='source';seq=[[source,400]]}
  else if(m==='regrab'&&t>=480){phase='pickup';seq=data.pickup;start=480;if(t>=840){phase='hold';seq=data.hold;start=840}}
  else{phase='release';seq=data.routes[source];start=400;held=false;freeze=400}
 }
 let result=at(seq,Math.max(0,t-start),phase==='hold'||phase==='idle');
 if(!held&&phase!=='idle'&&t-start>=sum(seq))phase='idle-after-release';
 return {...result,phase,seq,start,held,freeze,cycles:phase==='hold'?Math.floor((t-start)/720):0};
}
function clock(){return paused?elapsed:performance.now()-epoch}
function draw(){const t=clock(),s=resolve(t);nowState=s;for(const id of ['light','dark','one','oneDark'])document.getElementById(id).src=images[s.frame];
 const p=s.freeze===null?t:s.freeze;document.querySelector('#status').textContent=`${paused?'暂停':'播放'} · 时间 ${Math.floor(t)}ms · ${s.phase} · ${s.frame} · 项${s.index+1} · 完整翼周期 ${s.cycles} · 位置${s.freeze===null?'数值模拟移动':'已冻结'} (${Math.floor(100+p/10)},200)`;
 document.querySelector('#count').textContent=`已完成 ${s.cycles} 个翼周期`;
 const key=mode.value+':'+s.phase+':'+s.frame+':'+s.index+':'+s.cycles;if(key!==lastKey){trace.push({time:Math.floor(t),mode:mode.value,phase:s.phase,frame:s.frame,index:s.index,cycles:s.cycles,freeze:s.freeze});lastKey=key;window.art016Trace=trace;}
 requestAnimationFrame(draw);
}
function jump(t){paused=true;elapsed=t;document.querySelector('#time').value=t;document.querySelector('#pause').textContent='继续';}
function strip(){const box=document.querySelector('#strip');box.replaceChildren();let seq=mode.value==='hold'?data.hold:mode.value==='quick'?data.release:mode.value==='regrab'?data.routes.up:mode.value==='manual'?data.hold:data.routes[mode.value];let start=mode.value==='hold'||mode.value==='manual'?0:mode.value==='quick'?440:400;for(const [i,x] of seq.entries()){let atTime=start;const b=document.createElement('button');b.className='tile';b.innerHTML=`<img src="${images[x[0]]}">#${i+1} ${x[0]} ${x[1]}ms`;b.onclick=()=>jump(atTime);box.append(b);start+=x[1];}document.querySelector('#events').textContent=mode.value==='hold'?'翼720ms，眨眼1440ms；至少观察到完整翼周期5。':mode.value==='quick'?'400ms按下，440ms松手；位置立即冻结，源帧路由未实现：固定R回退。':mode.value==='regrab'?'400ms上扬松手，480ms重抓，立即重新pickup。':mode.value==='manual'?'按下/松手只驱动本网页状态；不是原生鼠标捕获。':'400ms松手，冻结坐标数值并进入该源图收翼序列。';}
function reset(){epoch=performance.now();elapsed=0;paused=false;manual=[];trace=[];lastKey='';document.querySelector('#pause').textContent='暂停';strip();}
mode.onchange=reset;document.querySelector('#replay').onclick=reset;
document.querySelector('#pause').onclick=()=>{if(paused){epoch=performance.now()-elapsed;paused=false}else{elapsed=clock();paused=true}document.querySelector('#pause').textContent=paused?'继续':'暂停'};
document.querySelector('#seek').onclick=()=>jump(Number(document.querySelector('#time').value));
document.querySelector('#step').onclick=()=>{const s=resolve(clock());let cycle=s.phase==='hold'?Math.floor((clock()-s.start)/sum(s.seq))*sum(s.seq):0;jump(s.start+cycle+s.seq.slice(0,s.index+1).reduce((n,x)=>n+x[1],0));};
for(const [id,type] of [['press','down'],['release','up']])document.getElementById(id).onclick=()=>{if(mode.value!=='manual'){mode.value='manual';reset()}manual.push({t:clock(),type});};
window.art016Resolve=resolve;reset();draw();
</script></html>'''
html=html.replace('DATA',json.dumps(data)).replace('IMAGES',json.dumps(images))
dest=ROOT/'art016-inspection.html';dest.write_text(html,encoding='utf-8')
embedded=json.loads(re.search(r'images=(\{.*?\}),mode=',html).group(1))
assert all(base64.b64decode(embedded[k].split(',')[1])==(ROOT/v).read_bytes() for k,v in names.items())
assert before=={str(p.relative_to(ROOT.parent)):sha(p) for p in protected}
evidence.update({'timing':data,'routeDurations':{k:sum(x[1] for x in v) for k,v in routes.items()},'embeddedBytesMatch':True,'protectedHashesUnchanged':before,'htmlSha256':sha(dest)})
(ROOT/'art016-build-report.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
print('PASS: 12 unchanged embedded PNGs, hold1440ms/20items, R460ms, six routes, protected hashes unchanged')
