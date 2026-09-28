from pathlib import Path
import re,json,base64
R=Path(__file__).resolve().parent
s=(R/'art028-demo.html').read_text(encoding='utf-8');images={f.stem:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode() for f in sorted((R/'art029-frames').glob('*.png'))}
s=re.sub(r'const images=.*;' ,lambda m:'const images='+json.dumps(images)+';',s,count=1)
s=s.replace('Wink与轻歪头 · 初版','衣摆配合轻扇 · 初版').replace('Wink与轻歪头 · 待审核初版','衣摆配合轻扇 · 待审核初版').replace('画面左眼wink，头部向同侧轻歪，轻扇持续。待用户审核。','仅衣摆末端轻扬，回落比翼部晚100毫秒。待用户审核。')
s=s.replace('<div><button id="now">','<div><label><input type="checkbox" id="hem" checked>衣摆摆动（关闭作对照）</label><label><input type="checkbox" id="combo">叠加已认可眨眼与wink</label></div><div><button id="now">')
s=s.replace('<script>','<script>'+(R/'art029-track.js').read_text(encoding='utf-8-sig')+'\n',1)
s=s.replace("s=engine.sample(t),key=s.wing+'-'+s.pose+'-'+s.phase;","s=engine.sample(t);s.hem=hemAt(t,s.dragging,$('hem').checked);if(!$('combo').checked){s.pose='open';s.phase='轻扇与衣摆'}let key=s.wing+'-'+s.pose+'-'+s.phase+'-'+s.hem;")
s=s.replace("images[s.wing+'-'+s.pose]","images[s.wing+'-'+s.pose+'-'+s.hem]")
s=s.replace("' · '+s.wing+'翼 · '","' · '+s.wing+'翼 · 衣摆'+s.hem+' · '")
s=s.replace("review=null;engine.begin(now());","review=null;$('combo').checked=true;engine.begin(now());")
s=s.replace('elapsed=engine.nextBoundary(elapsed)','elapsed=Math.min(engine.nextBoundary(elapsed),nextHemBoundary(elapsed))')
s=s.replace("$('scale').onchange=","for(let id of ['hem','combo'])$(id).onchange=()=>{review=null};\n$('scale').onchange=")
s=s.replace('真实等待50–70秒随机触发，每次完成或模拟拖动释放后重新计时。','衣摆随同一1400毫秒翼时间轴，无独立随机触发。模拟拖动期间衣摆恢复基础，释放按当前翼相位恢复。wink仍真实等待50–70秒随机触发，每次完成或模拟拖动释放后重新计时。')
s=s.replace("+s.hem+' · '","+({base:'基础',light:'轻扬',upper:'上扬'}[s.hem])+' · '").replace('>立即演示<','>立即wink<').replace('背景wink候选','背景衣摆候选')
(R/'art029-demo.html').write_text(s,encoding='utf-8');print('45 PNGs embedded; ART028 engine copied unchanged; new hem track and controls')
