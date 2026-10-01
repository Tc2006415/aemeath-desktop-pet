import json,base64
from pathlib import Path
R=Path(__file__).resolve().parent
images={f.stem:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode() for f in sorted((R/'art027-frames').glob('*.png'))}
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>自然眨眼 · 待用户审核</title><style>
body{background:#f4f1ee;color:#302937;font:16px 'Microsoft YaHei',sans-serif;margin:24px auto;max-width:1080px;padding:0 18px}h1{font-size:26px}button,select{font:inherit;padding:9px 14px;background:white;border:1px solid #bcaebd;border-radius:7px;margin:4px;cursor:pointer}.views{display:flex;gap:16px}.stage{flex:1;min-height:355px;border:1px solid #ccc;border-radius:10px;display:flex;align-items:center;flex-direction:column;justify-content:space-between;padding:14px}.light{background:#f0efeb}.dark{background:#1d222c;color:white}img{image-rendering:pixelated}small{color:#716676}#status{min-height:26px}@media(max-width:650px){.views{flex-direction:column}}
</style><h1>自然眨眼 · 初版</h1><p>待用户审核。中性嘴部保持不变，沿用已认可的第二版外观。</p>
<div><button id="solo">单独眨眼（A翼）</button><button id="combined">眨眼叠加轻扇</button><label>显示大小 <select id="scale"><option value="1">1×</option><option value="2">2×</option><option value="3" selected>3×</option></select></label></div>
<div><button id="pause">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button><button id="restart">从头播放</button></div><p id="status"></p>
<div class="views"><div class="stage light"><span>浅色背景</span><img id="light" alt="眨眼候选浅色背景"></div><div class="stage dark"><span>深色背景</span><img id="dark" alt="眨眼候选深色背景"></div></div>
<p>关键眼姿：<button data-eye="open">睁开</button><button data-eye="half">半闭</button><button data-eye="closed">自然闭合</button></p>
<p><small>半闭60 → 闭合80 → 半闭60 → 睁开40毫秒。眨眼起始间隔约4秒，仅供预览；轻扇保留原1400毫秒周期。逐帧按钮按两种动作的共同切换点前进。B/C翼部原有单像素透明点保持原样。本页尚未接入正式桌宠。</small></p>
<script>
const images=IMAGES;
const wingEnds=[400,550,700,1100,1250,1400],wingNames=['A','B','C','C','B','A'];
function sample(t,combined){let w=t%1400,b=(t-760+4000)%4000;return {wing:combined?wingNames[wingEnds.findIndex(e=>w<e)]:'A',eye:b<60?'half':b<140?'closed':b<200?'half':'open',blinkMs:b};}
function boundary(t,dir,combined){let points=new Set([0]);for(let k=Math.max(0,Math.floor(t/4000)-1);k<=Math.floor(t/4000)+1;k++)for(let d of [0,60,140,200,240])points.add(k*4000+760+d);if(combined)for(let k=Math.max(0,Math.floor(t/1400)-1);k<=Math.floor(t/1400)+1;k++)for(let d of [0,400,550,700,1100,1250,1400])points.add(k*1400+d);let q=[...points].filter(p=>dir>0?p>t+0.01:p<t-0.01).sort((a,b)=>a-b);return dir>0?q[0]:(q.at(-1)??0);}
let combined=false,paused=false,time=0,origin=performance.now(),override=null;
const names={open:'睁开',half:'半闭',closed:'自然闭合'};
function now(){return paused?time:performance.now()-origin}
function paint(){let t=now(),s=sample(t,combined);if(override)s.eye=override;for(let id of ['light','dark'])document.getElementById(id).src=images[s.wing+'-'+s.eye];document.getElementById('status').textContent=(paused?'已暂停':'播放中')+' · '+(combined?'眨眼叠加轻扇':'单独眨眼')+' · '+names[s.eye]+' · '+s.wing+'翼 · '+Math.floor(t)+'毫秒';requestAnimationFrame(paint)}
function stop(){time=now();paused=true;document.getElementById('pause').textContent='继续'}
function start(){time=0;origin=performance.now();paused=false;override=null;document.getElementById('pause').textContent='暂停'}
document.getElementById('solo').onclick=()=>{combined=false;start()};document.getElementById('combined').onclick=()=>{combined=true;start()};document.getElementById('restart').onclick=start;
document.getElementById('pause').onclick=()=>{if(paused){override=null;origin=performance.now()-time;paused=false;document.getElementById('pause').textContent='暂停'}else stop()};
for(let [id,dir] of [['prev',-1],['next',1]])document.getElementById(id).onclick=()=>{stop();override=null;time=boundary(time,dir,combined)};
document.querySelectorAll('[data-eye]').forEach(b=>b.onclick=()=>{stop();override=b.dataset.eye});
document.getElementById('scale').onchange=e=>{for(let id of ['light','dark']){document.getElementById(id).width=96*Number(e.target.value);document.getElementById(id).height=104*Number(e.target.value)}};
document.getElementById('scale').dispatchEvent(new Event('change'));paint();
</script></html>'''.replace('IMAGES',json.dumps(images))
(R/'art027-demo.html').write_text(html,encoding='utf-8');print('9 original PNGs embedded')
