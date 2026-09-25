import json,base64
from pathlib import Path
R=Path(__file__).resolve().parent
images={f.stem:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode() for f in sorted((R/'art028-frames').glob('*.png'))}
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Wink与轻歪头 · 待审核初版</title><style>
body{background:#f4f1ee;color:#302937;font:16px 'Microsoft YaHei',sans-serif;margin:24px auto;max-width:1080px;padding:0 18px}h1{font-size:26px}button,select{font:inherit;padding:9px 14px;background:white;border:1px solid #bcaebd;border-radius:7px;margin:4px;cursor:pointer}button:disabled{opacity:.45;cursor:default}.views{display:flex;gap:16px}.stage{flex:1;min-height:355px;border:1px solid #ccc;border-radius:10px;display:flex;align-items:center;flex-direction:column;justify-content:space-between;padding:14px}.light{background:#f0efeb}.dark{background:#1d222c;color:white}img{image-rendering:pixelated}small{color:#716676}#status,#countdown{min-height:24px}#drag{touch-action:none;user-select:none}#drag[aria-pressed=true]{background:#65416a;color:white}@media(max-width:650px){.views{flex-direction:column}}
</style><h1>Wink与轻歪头 · 初版</h1><p>画面左眼wink，头部向同侧轻歪，轻扇持续。待用户审核。</p>
<div><button id="now">立即演示</button><button id="drag" aria-pressed="false">模拟拖动（按住）</button><label>显示大小 <select id="scale"><option value="1">1×</option><option value="2">2×</option><option value="3" selected>3×</option></select></label></div>
<div><button id="pause">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button></div><p id="countdown"></p><p id="status"></p>
<div class="views"><div class="stage light"><span>浅色背景</span><img id="light" alt="浅色背景wink候选"></div><div class="stage dark"><span>深色背景</span><img id="dark" alt="深色背景wink候选"></div></div>
<p><small>真实等待50–70秒随机触发，每次完成或模拟拖动释放后重新计时。进入250 / 停留450 / 回正350 / 稳定150毫秒。普通眨眼4秒仅供预览，wink期间互斥。按住模拟拖动会中断wink并回正，期间立即演示也不可用；这是网页模拟，非原生拖动。逐帧回退仅回看已记录状态，再次继续会恢复原时间点。B/C原透明点保留。正式桌宠尚未接入。</small></p>
<script>ENGINE
const images=IMAGES;
const engine=new WinkPreviewEngine();let paused=false,elapsed=0,origin=performance.now(),review=null,history=[],lastKey='';
const $=id=>document.getElementById(id);function now(){return paused?elapsed:performance.now()-origin}
function freeze(){if(!paused)elapsed=now();paused=true;$('pause').textContent='继续';}
function paint(){let t=now(),s=engine.sample(t),key=s.wing+'-'+s.pose+'-'+s.phase;if(key!==lastKey){history.push({t,s:{...s}});if(history.length>200)history.shift();lastKey=key;}if(review!==null&&history[review]){s=history[review].s;t=history[review].t;}
 for(let id of ['light','dark'])$(id).src=images[s.wing+'-'+s.pose];
 $('status').textContent=(review!==null?'回看':paused?'已暂停':'播放中')+' · '+s.phase+' · '+s.wing+'翼 · '+Math.floor(t)+'毫秒';
 $('countdown').textContent=engine.dragging?'模拟拖动中：wink已屏蔽，释放后重新随机等待':engine.winkStart!==null?'wink进行中，完成后重新随机等待':'下次wink约 '+Math.max(0,s.remaining/1000).toFixed(1)+' 秒（本轮 '+(engine.lastDelay/1000).toFixed(1)+' 秒）';
 $('now').disabled=engine.dragging||engine.winkStart!==null;$('prev').disabled=engine.dragging||history.length<2;$('next').disabled=engine.dragging;requestAnimationFrame(paint);}
$('now').onclick=()=>{review=null;engine.begin(now());};
$('pause').onclick=()=>{review=null;if(paused){origin=performance.now()-elapsed;paused=false;$('pause').textContent='暂停'}else freeze()};
$('prev').onclick=()=>{freeze();review=Math.max(0,(review===null?history.length-1:review)-1)};
$('next').onclick=()=>{freeze();if(review!==null){review++;if(review>=history.length-1)review=null;}else elapsed=engine.nextBoundary(elapsed);};
function down(){review=null;engine.press(now());$('drag').setAttribute('aria-pressed','true');}
function up(){engine.release(now());$('drag').setAttribute('aria-pressed','false');}
$('drag').onpointerdown=e=>{e.preventDefault();$('drag').setPointerCapture(e.pointerId);down()};$('drag').onpointerup=up;$('drag').onpointercancel=up;$('drag').onlostpointercapture=up;
$('drag').onkeydown=e=>{if((e.key===' '||e.key==='Enter')&&!e.repeat){e.preventDefault();down()}};$('drag').onkeyup=e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();up()}};window.addEventListener('blur',up);
$('scale').onchange=e=>{for(let id of ['light','dark']){$(id).width=96*Number(e.target.value);$(id).height=104*Number(e.target.value)}};$('scale').dispatchEvent(new Event('change'));paint();
</script></html>'''.replace('ENGINE',(R/'art028-engine.js').read_text(encoding='utf-8-sig')).replace('IMAGES',json.dumps(images))
(R/'art028-demo.html').write_text(html,encoding='utf-8');print('15 actual PNGs embedded; standalone demo')
