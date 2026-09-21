"""Self-contained scenario/step preview of candidate bytes. Web simulation only."""
import base64
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
package=ROOT/'art011-package'
manifest=json.loads((package/'manifest.json').read_bytes())
images={str(p.relative_to(package)).replace('\\','/'):'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for p in (package/'frames').glob('*.png')}
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ART-011 drag candidate</title>
<style>body{font:16px system-ui;background:#eee;color:#222;margin:18px}button,select{padding:9px;margin:3px;font:inherit}img{image-rendering:pixelated}.stage{display:flex;gap:12px;align-items:flex-start}.box{padding:10px;background:#f0efeb}.dark{background:#1d222c;color:white}.big{width:288px;height:312px}.strip{display:flex;flex-wrap:wrap;gap:5px}.tile{background:white;font-size:12px}.tile img{display:block;width:96px;height:104px}input{width:600px;max-width:90vw}#status{font-variant-numeric:tabular-nums;background:#fff;padding:8px}p{margin:8px 0}</style>
<h1>ART-011 · 0.4.0 表情拖动候选</h1><p>网页情境模拟，不代表原生鼠标拖动验收。拿起轻惊讶 → 悬停眯眼微笑/眨眼 → 落稳闭眼笑 → neutral；头饰固定。</p>
<select id="mode" aria-label="动作或情境"><option value="normal">情境：按下→保持→松手</option><option value="quick">情境：40ms快速松手</option><option value="mid">情境：pickup中途松手</option><option value="regrab">情境：release中再次抓取</option><option value="interactive">手动按下/松手</option></select>
<button id="replay">重播</button><button id="pause">暂停</button><button id="step">下一时序项</button><button id="down">按下</button><button id="up">松手</button>
<p id="status"></p><label>时间 <input id="seek" type="range" min="0" max="4200" value="0"></label>
<div class="stage"><div class="box">浅底3×<br><img class="big" id="light"></div><div class="box dark">深底3×<br><img class="big" id="dark"></div><div class="box">浅底1×<br><img id="one"></div><div class="box dark">深底1×<br><img id="oneDark"></div></div>
<p id="events"></p><h2>逐项检查（点击暂停）</h2><div class="strip" id="strip"></div><p>pickup：neutral80 → 松腿惊讶80 → 收腿惊讶100 → 松腿微笑100；hold：微笑 / 羽饰轻+微笑 / 羽饰峰+闭眼 / 羽饰轻+微笑，各180ms；release：松腿微笑80 → 落稳闭眼100 → 落稳半睁眼120 → neutral160。</p>
<script>
const pack=PACKAGE,images=IMAGES,mode=document.querySelector('#mode'),seek=document.querySelector('#seek');
const scenarios={normal:[[400,'down'],[2500,'up']],quick:[[400,'down'],[440,'up']],mid:[[400,'down'],[600,'up']],regrab:[[400,'down'],[650,'up'],[730,'down'],[1300,'up']]};
for(const a of Object.keys(pack.actions)){let o=document.createElement('option');o.value=a;o.textContent=a;mode.append(o)}
let epoch=performance.now(),elapsed=0,paused=false,liveEvents=[],current={a:'idle-soft',i:0};
function duration(a){return pack.actions[a].frames.reduce((s,f)=>s+f.durationMs,0)}
function resolve(t){let a='idle-soft',start=0,held=false,j=0,ev=scenarios[mode.value]||liveEvents;
 if(pack.actions[mode.value]){a=mode.value;if(pack.actions[a].playback==='once'&&t>=duration(a)){start=duration(a);a='idle-soft'}}
 else {for(let guard=0;guard<40;guard++){let e=ev[j],end=pack.actions[a].playback==='once'?start+duration(a):Infinity,next=Math.min(e?e[0]:Infinity,end);if(next>t||next===Infinity)break;if(e&&e[0]<=end){held=e[1]==='down';a=held?'drag-pickup':'drag-release';start=e[0];j++}else{a=a==='drag-pickup'&&held?'drag-hold':'idle-soft';start=end}}}
 let local=Math.max(0,t-start);if(pack.actions[a].playback==='loop')local%=duration(a);let i=0,remaining=local;while(i<pack.actions[a].frames.length-1&&remaining>=pack.actions[a].frames[i].durationMs){remaining-=pack.actions[a].frames[i++].durationMs}return {a,i,local,held};}
function render(){let t=paused?elapsed:performance.now()-epoch;current=resolve(t);let f=pack.actions[current.a].frames[current.i];for(const id of ['light','dark','one','oneDark'])document.getElementById(id).src=images[f.path];document.querySelector('#status').textContent=`${paused?'暂停':'播放'} · ${current.a} · 项${current.i+1} · ${f.path} · 情境时间 ${Math.floor(t)}ms · 局部 ${Math.floor(current.local)}ms`;seek.value=Math.floor(t);requestAnimationFrame(render)}
function jump(a,i){mode.value=a;paused=true;elapsed=pack.actions[a].frames.slice(0,i).reduce((s,f)=>s+f.durationMs,0);seek.max=duration(a);document.querySelector('#pause').textContent='继续';buildStrip()}
function buildStrip(){let strip=document.querySelector('#strip');strip.replaceChildren();let names=pack.actions[mode.value]?[mode.value]:['drag-pickup','drag-hold','drag-release'];for(const a of names)pack.actions[a].frames.forEach((f,i)=>{let b=document.createElement('button');b.className='tile';b.innerHTML=`<img src="${images[f.path]}">${a} #${i+1}<br>${f.durationMs}ms`;b.onclick=()=>jump(a,i);strip.append(b)});document.querySelector('#events').textContent='情境事件：'+JSON.stringify(scenarios[mode.value]||liveEvents)}
function reset(){epoch=performance.now();elapsed=0;paused=false;liveEvents=[];seek.max=pack.actions[mode.value]?duration(mode.value):4200;document.querySelector('#pause').textContent='暂停';buildStrip()}
mode.onchange=reset;document.querySelector('#replay').onclick=reset;document.querySelector('#pause').onclick=()=>{if(paused){epoch=performance.now()-elapsed;paused=false}else{elapsed=performance.now()-epoch;paused=true}document.querySelector('#pause').textContent=paused?'继续':'暂停'};
document.querySelector('#step').onclick=()=>jump(current.a,(current.i+1)%pack.actions[current.a].frames.length);
seek.oninput=()=>{elapsed=Number(seek.value);paused=true;document.querySelector('#pause').textContent='继续'};
for(const e of ['down','up'])document.getElementById(e).onclick=()=>{if(mode.value!=='interactive'){mode.value='interactive';reset()}let t=paused?elapsed:performance.now()-epoch;liveEvents.push([t,e]);buildStrip()};reset();render();
</script></html>'''
(ROOT/'art011-inspection.html').write_text(html.replace('PACKAGE',json.dumps(manifest)).replace('IMAGES',json.dumps(images)),encoding='utf-8')
print('Preview: embedded 12 images; 6 actions; normal/quick/mid/regrab/manual scenarios')
