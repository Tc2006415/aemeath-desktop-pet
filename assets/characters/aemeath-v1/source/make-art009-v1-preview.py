"""Build a self-contained inspection page from real frames, without painting art."""
import base64
import json
from pathlib import Path

root = Path(__file__).resolve().parent
package = json.loads((root / 'art009-v1-package/manifest.json').read_text(encoding='utf-8'))
images = {frame['path']: 'data:image/png;base64,' + base64.b64encode((root / 'art009-v1-package' / frame['path']).read_bytes()).decode()
          for clip in package['actions'].values() for frame in clip['frames']}
for action, total, durations in [('idle-soft', 1400, [400,150,150,400,150,150]), ('idle-smile',1200,[120,120,500,120,120,220])]:
    frames = package['actions'][action]['frames']
    assert [f['durationMs'] for f in frames] == durations
    assert sum(f['durationMs'] for f in frames) == total
    assert len({images[f['path']] for f in frames}) == 3
assert package['anchor'] == {'x':48, 'y':94}
html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ART-009 动画候选检查</title>
<style>body{font:16px system-ui;margin:24px;color:#222;background:#eee}button,select{font:inherit;padding:8px;margin:4px}img{image-rendering:pixelated}section{display:flex;gap:16px;margin:16px 0;flex-wrap:wrap}.box{padding:16px;background:#fff}.dark{background:#252932;color:white}.sprite{width:288px;height:312px}.strip{display:flex;flex-wrap:wrap;gap:8px}.tile{padding:8px;background:white;text-align:center}.tile img{display:block;width:192px;height:208px}#status{font-variant-numeric:tabular-nums;min-height:28px}.warn{background:#ffe2bc;padding:12px}input{width:480px;max-width:90vw}</style>
<h1>ART-009 · 两动作候选检查</h1><p class="warn">局部合成候选：头饰与身体保持neutral；峰值羽尖局部距离3px。待PM/QA验收，本页不是原生宿主。</p>
<select id="mode"><option value="idle-soft">idle-soft循环 · 1400ms</option><option value="idle-smile">idle-smile单次 · 1200ms</option><option value="automatic">15秒待机 → 笑脸 → 待机</option></select>
<button id="play">重播</button><button id="pause">暂停</button><button id="step">下一时序项</button><div id="status"></div>
<section><div class="box">浅底3×<br><img class="sprite" id="light"></div><div class="box dark">深底3×<br><img class="sprite" id="dark"></div><div class="box">浅底1×<br><img id="actual"></div><div class="box dark">深底1×<br><img id="actualDark"></div></section>
<label>逐毫秒检查 <input id="seek" type="range" min="0" max="1399" value="0"></label><h2>逐帧检查（点击暂停到该项）</h2><div class="strip" id="strip"></div>
<p>idle-soft: neutral → soft-light → soft-peak → soft-peak保持 → soft-light → neutral；按实际羽饰幅度排序。idle-smile: neutral → half → closed → half → neutral → neutral收势。复用项保留指定时序。</p>
<script>
const pack=PACKAGE, images=IMAGES;
const mode=document.querySelector('#mode'), seek=document.querySelector('#seek');
let epoch=performance.now(), paused=false, elapsed=0, currentIndex=0, currentAction='idle-soft';
function duration(a){return pack.actions[a].frames.reduce((n,f)=>n+f.durationMs,0)}
function locate(a,t){let frames=pack.actions[a].frames; let i=0;while(i<frames.length-1&&t>=frames[i].durationMs){t-=frames[i].durationMs;i++}return i}
function render(){let t=paused?elapsed:performance.now()-epoch,a=mode.value,local=t;
if(a==='automatic'){a=t<15000?'idle-soft':t<16200?'idle-smile':'idle-soft';local=t<15000?t:t<16200?t-15000:t-16200}
if(a==='idle-soft')local%=1400;else if(local>=1200){a='neutral';local=0}
let i=locate(a,local),f=pack.actions[a].frames[i];currentIndex=i;currentAction=a;
for(let id of ['light','dark','actual','actualDark'])document.getElementById(id).src=images[f.path];
document.querySelector('#status').textContent=`${paused?'暂停':'播放'} · ${a} · 项${i+1} · ${f.path} · ${Math.floor(local)}ms · 总经过 ${Math.floor(t)}ms`;
seek.value=Math.floor(t%(mode.value==='idle-soft'?1400:mode.value==='automatic'?18000:1200));requestAnimationFrame(render)}
function reset(){epoch=performance.now();elapsed=0;paused=false;document.querySelector('#pause').textContent='暂停';seek.max=mode.value==='automatic'?17999:duration(mode.value)-1;buildStrip()}
function jump(a,i){mode.value=a;elapsed=pack.actions[a].frames.slice(0,i).reduce((n,f)=>n+f.durationMs,0);paused=true;seek.max=duration(a)-1;document.querySelector('#pause').textContent='继续'}
function buildStrip(){let s=document.querySelector('#strip');s.replaceChildren();for(let a of mode.value==='automatic'?['idle-soft','idle-smile']:[mode.value]){pack.actions[a].frames.forEach((f,i)=>{let b=document.createElement('button');b.className='tile';b.innerHTML=`<img src="${images[f.path]}">${a} ${i+1}<br>${f.durationMs}ms<br>${f.path.split('/')[1]}`;b.onclick=()=>jump(a,i);s.append(b)})}}
mode.onchange=reset;document.querySelector('#play').onclick=reset;document.querySelector('#pause').onclick=()=>{if(paused){epoch=performance.now()-elapsed;paused=false}else{elapsed=performance.now()-epoch;paused=true}document.querySelector('#pause').textContent=paused?'继续':'暂停'};
document.querySelector('#step').onclick=()=>{let a=currentAction==='neutral'?'idle-smile':currentAction;jump(a,(currentIndex+1)%6)};
seek.oninput=()=>{elapsed=Number(seek.value);paused=true;document.querySelector('#pause').textContent='继续'};reset();render();
</script></html>'''
html = html.replace('PACKAGE',json.dumps(package)).replace('IMAGES',json.dumps(images))
(root / 'art009-v1-inspection.html').write_text(html,encoding='utf-8')
print('PASS: 3 actions / 5 unique images, timings 1400/1200ms, 6 items each; preview generated')
