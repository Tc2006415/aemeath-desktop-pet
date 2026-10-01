from pathlib import Path
import json,base64
R=Path(__file__).resolve().parent
imgs={k+f.stem:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode() for folder,k in [('art029-frames','idle:'),('art030-frames','pick:')] for f in sorted((R/folder).glob('*.png'))}
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>拿起动作v2 · 待审核初版</title><style>
body{background:#f4f1ee;color:#302937;font:16px 'Microsoft YaHei',sans-serif;margin:24px auto;max-width:1080px;padding:0 18px}h1{font-size:26px}button,select{font:inherit;padding:9px 12px;background:white;border:1px solid #bcaebd;border-radius:7px;margin:4px;cursor:pointer}.views{display:flex;gap:16px}.stage{flex:1;min-height:350px;border:1px solid #ccc;border-radius:10px;display:flex;align-items:center;flex-direction:column;justify-content:space-between;padding:14px}.light{background:#f0efeb}.dark{background:#1d222c;color:white}img{image-rendering:pixelated}small{color:#716676}.compare{display:flex;gap:20px}.compare figure{margin:8px;background:#ddd6d9;padding:10px}#status{min-height:28px}@media(max-width:650px){.views{flex-direction:column}}
</style><h1>拿起动作v2 · 初版</h1><p>模拟按下立即开始360毫秒拿起。终点持握入口静止，拖动循环待下一项。</p>
<div><label>来源状态 <select id="source"><option value="live">自动待机组合</option><option value="A-open-base">基础A待机</option><option value="B-open-base">轻扇B</option><option value="C-open-base">轻扇C</option><option value="A-half-base">眨眼半闭</option><option value="A-closed-base">眨眼闭合</option><option value="C-wink-upper">wink歪头＋衣摆上扬</option><option value="B-open-light">轻扇B＋衣摆轻扬</option><option value="C-open-upper">轻扇C＋衣摆上扬</option></select></label><label>显示大小 <select id="scale"><option value="1">1×</option><option value="2">2×</option><option value="3" selected>3×</option></select></label></div>
<div><button id="take">模拟按下·拿起</button><button id="reset">复位到待机（非放下）</button><button id="pause">暂停</button><button id="prev">上一帧</button><button id="next">下一帧</button></div><p id="status"></p>
<div class="views"><div class="stage light"><span>浅色背景</span><img id="light" alt="浅色拿起候选"></div><div class="stage dark"><span>深色背景</span><img id="dark" alt="深色拿起候选"></div></div>
<details open><summary>入口接缝对照（按下时源图 → 首项A）</summary><div class="compare"><figure><img id="captured" width="192" height="208"><figcaption>实际按下前显示的源图</figcaption></figure><figure><img id="first" width="192" height="208"><figcaption>立即进入首项 neutral80</figcaption></figure></div><p id="risk">尚未触发拿起。</p></details>
<p><small>四项：neutral80 → 松腿惊讶80 → 收腿惊讶100 → 新持握入口100毫秒。B/C翼、闭眼、wink歪头或衣摆上扬切回A可能可见跳变，尚未实现专用入口衔接；本页没有等待原动作播完。复位仅演示操作，不代表放下动画。自动背景沿用已认可眨眼/wink/衣摆，仅网页模拟，未接入正式桌宠。</small></p>
<script>ENGINE
TRACK
PICKUP
const images=IMAGES;
const $=id=>document.getElementById(id),engine=new WinkPreviewEngine();let origin=performance.now(),paused=false,t=0,pickStart=null,lastShown='idle:A-open-base';
function now(){return paused?t:performance.now()-origin}
function idleKey(time){if($('source').value!=='live')return 'idle:'+$('source').value;const s=engine.sample(time);return 'idle:'+s.wing+'-'+s.pose+'-'+hemAt(time,false,true)}
function render(){const time=now();let key;if(pickStart===null){key=idleKey(time);$('status').textContent=(paused?'已暂停':'播放中')+' · 待机来源 · '+Math.floor(time)+'毫秒';}else{const elapsed=Math.max(0,time-pickStart),s=pickupAt(elapsed);key='pick:'+pickupFrames[s.index];$('status').textContent=s.done?'拿起结束 · 持握入口静止 · 拖动循环待下一项':(paused?'已暂停':'播放中')+' · 拿起第'+(s.index+1)+'项 · '+Math.floor(elapsed)+' / 360毫秒';}for(const id of ['light','dark'])$(id).src=images[key];lastShown=key;$('take').disabled=pickStart!==null;$('prev').disabled=pickStart===null;$('next').disabled=pickStart===null;requestAnimationFrame(render)}
$('take').onclick=()=>{const captured=lastShown;$('captured').src=images[captured];$('first').src=images['pick:neutral'];$('risk').textContent=captured==='idle:A-open-base'?'本来源与首项A原PNG一致。':'当前源 '+captured.slice(5)+' 立即切到A：存在回正/收翼/表情或衣摆复位接缝，待用户判断。';pickStart=now();};
$('reset').onclick=()=>{pickStart=null};$('source').onchange=()=>{pickStart=null};
function stop(){if(!paused)t=now();paused=true;$('pause').textContent='继续'}
$('pause').onclick=()=>{if(paused){origin=performance.now()-t;paused=false;$('pause').textContent='暂停'}else stop()};
$('next').onclick=()=>{stop();const e=t-pickStart;t=pickStart+([80,160,260,360].find(x=>x>e+.001)??360)};
$('prev').onclick=()=>{stop();const e=t-pickStart;t=pickStart+([0,80,160,260].filter(x=>x<e-.001).at(-1)??0)};
$('scale').onchange=e=>{for(const id of ['light','dark']){$(id).width=96*Number(e.target.value);$(id).height=104*Number(e.target.value)}};$('scale').dispatchEvent(new Event('change'));$('captured').src=images['idle:A-open-base'];$('first').src=images['pick:neutral'];render();
</script></html>'''.replace('ENGINE',(R/'art028-engine.js').read_text(encoding='utf-8-sig')).replace('TRACK',(R/'art029-track.js').read_text(encoding='utf-8-sig')).replace('PICKUP',(R/'art030-track.js').read_text(encoding='utf-8-sig')).replace('IMAGES',json.dumps(imgs))
(R/'art030-demo.html').write_text(html,encoding='utf-8');print('49 actual PNGs embedded; 360ms finite pickup; captured source comparison')
