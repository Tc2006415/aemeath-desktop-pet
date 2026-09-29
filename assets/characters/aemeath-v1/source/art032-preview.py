from pathlib import Path
import json,base64
R=Path(__file__).resolve().parent
images={prefix+f.stem:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode() for folder,prefix in [('art029-frames','idle:'),('art032-frames','pose:')] for f in sorted((R/folder).glob('*.png'))}
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>拿起、恼怒拖拽与放下 · ART032初版</title><style>
body{font:16px 'Microsoft YaHei',sans-serif;color:#302937;background:#f4f1ee;max-width:1080px;margin:24px auto;padding:0 18px}h1{font-size:25px}button,select{font:inherit;margin:4px;padding:9px 12px;border:1px solid #b9aabb;border-radius:7px;background:white;cursor:pointer}#hold{background:#514260;color:white;touch-action:none;user-select:none}.views{display:flex;gap:16px}.stage{flex:1;min-height:360px;border:1px solid #ccc;border-radius:10px;display:flex;align-items:center;flex-direction:column;justify-content:space-between;padding:14px}.light{background:#f0efeb}.dark{background:#1d222c;color:white}img{image-rendering:pixelated}small{color:#756879}#status{min-height:28px}.note{padding:12px;background:#e9e2ee;border-radius:8px}.compare{display:flex;gap:20px}.compare figure{margin:8px;background:#ddd6d9;padding:10px}@media(max-width:650px){.views{flex-direction:column}}
</style><h1>拿起 → 持续轻恼怒 → 放下</h1><p>约700毫秒慌张，随后保持轻恼怒循环直到释放。仅按钮模拟，没有移动真实桌面窗口。</p><p class="note" id="artStatus">阶段性预览，未完成全部美术要求：交替脚姿与收尾上扬翼已有候选；抬手／微屈读感偏弱，下弯嘴角在采样中丢失，轻恼主要依靠眉眼。六次生成已用完，不能视为完整通过版。袜靴色块与局部接缝也请审看。</p>
<div><button id="hold">按住模拟拿起 / 松开即放下</button><button id="latch">拿起并保持</button><button id="release">释放放下</button><button id="reset">复位到待机（非放下）</button></div>
<div><button id="early">演示：慌张中松手</button><button id="late">演示：恼怒中松手</button><button id="pause">暂停</button><button id="prev">上一步</button><button id="next">下一帧</button><label>显示大小 <select id="scale"><option value="1">1×</option><option value="2">2×</option><option value="3" selected>3×</option></select></label></div>
<p id="status"></p><div class="views"><div class="stage light"><span>浅色背景</span><img id="light" alt="浅色交互预览"></div><div class="stage dark"><span>深色背景</span><img id="dark" alt="深色交互预览"></div></div>
<details><summary>当前姿态释放对照与已知接缝</summary><div class="compare"><figure><img id="captured" width="192" height="208"><figcaption>实际释放前显示的图</figcaption></figure><figure><img id="first" width="192" height="208"><figcaption>收尾首项（原图保留60毫秒）</figcaption></figure></div><p id="entry">尚未释放。</p><p>从闭眼或wink待机拿起，源快照60毫秒后头脸会回正；衣摆也回基础层，可能可见跳变。源快照是浏览器最近赋给图像的PNG，不是显示器呈现回执。放下中重抓会立即重开慌张，不能宣称任意入口无缝。</p></details>
<p><small>拖拽和收尾阶段禁wink。恼怒不会定时自行缓和；放下完成后才恢复已认可待机，并重新计眨眼、wink和衣摆时间。末段短眨眼用于舒展，拖拽循环没有半眯疲态。复位只是预览操作。</small></p>
<script>WINKENGINE
HEMTRACK
INTERACTION
const images=IMAGEJSON,$=id=>document.getElementById(id);let ctl=new InteractionPreview(),wink=new WinkPreviewEngine(),epoch=0,origin=performance.now(),t=0,paused=false,lastShown='idle:A-open-base',autoRelease=null,history=[];
function now(){return paused?t:performance.now()-origin}
function remember(){history.push({t:now(),ctl:JSON.stringify(ctl),autoRelease,epoch});if(history.length>80)history.shift()}
function stop(){if(!paused)t=now();paused=true;$('pause').textContent='继续'}
function run(){origin=performance.now()-t;paused=false;$('pause').textContent='暂停'}
function draw(){const time=now();if(autoRelease!==null&&time>=autoRelease){ctl.release(time,lastShown);capture();autoRelease=null;}const state=ctl.sample(time);if(ctl.idleEpoch!==epoch){epoch=ctl.idleEpoch;wink=new WinkPreviewEngine();}let key=state.key;if(state.mode==='idle'){const a=wink.sample(state.local);key='idle:'+a.wing+'-'+a.pose+'-'+hemAt(state.local,false,true);}for(const id of ['light','dark'])$(id).src=images[key];lastShown=key;const label={idle:'正常待机',panic:'慌张交替轻蹬',held:'持续轻恼怒 · 松手才结束',release:'放下收尾'}[state.mode];$('status').textContent=(paused?'已暂停':'播放中')+' · '+label+' · '+Math.floor(state.local)+'毫秒';$('release').disabled=!['panic','held'].includes(state.mode);$('prev').disabled=!history.length;}
function capture(){$('captured').src=images[ctl.source];$('first').src=images[ctl.source];$('entry').textContent='释放已立即中断原阶段；首项使用实际显示源 '+ctl.source+'，原PNG完全相同。';}
function press(){remember();ctl.press(now(),lastShown);autoRelease=null;draw()}
function release(){remember();if(ctl.release(now(),lastShown))capture();autoRelease=null;draw()}
$('hold').onpointerdown=e=>{if(e.button!==0)return;e.preventDefault();$('hold').setPointerCapture(e.pointerId);press()};$('hold').onpointerup=release;$('hold').onpointercancel=release;$('hold').onlostpointercapture=()=>{if(['panic','held'].includes(ctl.mode))release()};$('hold').onkeydown=e=>{if([' ','Enter'].includes(e.key)&&!e.repeat){e.preventDefault();press()}};$('hold').onkeyup=e=>{if([' ','Enter'].includes(e.key)){e.preventDefault();release()}};
$('latch').onclick=press;$('release').onclick=release;
$('reset').onclick=()=>{remember();ctl=new InteractionPreview();ctl.idleEpoch=now();epoch=ctl.idleEpoch;wink=new WinkPreviewEngine();autoRelease=null;draw()};
for(const [id,delay]of [['early',240],['late',1800]])$(id).onclick=()=>{if(paused)run();press();autoRelease=now()+delay};
$('pause').onclick=()=>{if(paused)run();else stop();draw()};
$('next').onclick=()=>{remember();stop();t=ctl.mode==='idle'?t+100:ctl.next(t);if(autoRelease!==null)t=Math.min(t,autoRelease);draw()};
$('prev').onclick=()=>{if(!history.length)return;stop();const h=history.pop();t=h.t;Object.assign(ctl,JSON.parse(h.ctl));autoRelease=h.autoRelease;epoch=h.epoch;wink=new WinkPreviewEngine();draw()};
$('scale').onchange=e=>{for(const id of ['light','dark']){$(id).width=96*Number(e.target.value);$(id).height=104*Number(e.target.value)}};$('scale').dispatchEvent(new Event('change'));$('captured').src=images[lastShown];$('first').src=images[lastShown];function loop(){draw();requestAnimationFrame(loop)}loop();
</script></html>'''
for token,file in [('WINKENGINE','art028-engine.js'),('HEMTRACK','art029-track.js'),('INTERACTION','art032-track.js')]:html=html.replace(token,(R/file).read_text(encoding='utf-8-sig'))
html=html.replace('IMAGEJSON',json.dumps(images));(R/'art032-demo.html').write_text(html,encoding='utf-8');print('Embedded',len(images),'actual PNGs')
