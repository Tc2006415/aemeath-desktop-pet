"""Unmodified input bytes, original timing, diagnostic candidates only."""
import base64,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
F=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
paths={'A':R/'art024-neutral-A.png'}
for pose in ['B','C']:
    for v in [1,2]:
        p=R/f'art024-{pose}-v{v}-candidate-96.png'
        if p.exists():paths[f'{pose}{v}']=p
for p in sorted((F/'frames').glob('*.png')):paths['old-'+p.stem]=p
u=lambda p:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
images={n:u(p) for n,p in paths.items()}
cards=''
for n in [k for k in paths if not k.startswith('old-')]:
    cards+=f'<h2>{n}</h2><div class="row">'+''.join('<div class="panel '+bg+'">'+bg+''.join(f'<img width="{96*s}" height="{104*s}" src="{images[n]}">' for s in [1,2,3])+'</div>' for bg in ['light','dark'])+'</div>'
crops='<h2>翼部10×原PNG对照</h2><div class="row">'
for n in [k for k in paths if not k.startswith('old-')]:
    crops+=f'<div>{n}'+''.join(f'<div class="crop"><img style="left:-{x*10}px" src="{images[n]}"></div>' for x in [8,60])+'</div>'
crops+='</div>'
old='<h2>旧16帧只读对照（其中11张非核心帧）</h2><div class="grid">'+''.join(f'<div>{n}<br><img width="192" height="208" src="{images[n]}"></div>' for n in paths if n.startswith('old-'))+'</div>'
html='''<!doctype html><meta charset="utf-8"><title>ART-024 翼部候选检查</title><style>body{font:14px system-ui;margin:12px;background:#eee}h1{font-size:22px}h2{font-size:17px}.row{display:flex;gap:8px}.panel{display:flex;gap:2px;align-items:end;padding:5px;font-size:10px}.light{background:#f0efeb}.dark{background:#1d222c;color:white}img{image-rendering:pixelated}.crop{position:relative;overflow:hidden;width:280px;height:220px;background:#1d222c}.crop img{position:absolute;width:960px;height:1040px;top:-780px;max-width:none}.grid{display:grid;grid-template-columns:repeat(5,1fr)}</style><h1>ART-024 · A固定 / 新姿态尝试</h1><p>A为用户已选v2，原始字节不变。页面为素材诊断，不是原生验收。</p>'''+crops+cards+old
manifest=json.loads((F/'manifest.json').read_bytes())
seq={n:manifest['actions'][n]['frames'] for n in ['drag-pickup','drag-hold','drag-release']}
seq.update({'entry:'+k:v for k,v in manifest['actions']['drag-release']['entrySequences'].items()})
probe='<p style="color:#a00;font-weight:bold">B两次失败，达到该姿态上限停止；C及笑脸未制作，五帧未交付。A用户选择保持。</p><h2>旧动作与A边界诊断（仅neutral显示A，其余仍旧帧）</h2><p>保持原数组时长，单次到末项停止。四个旧idle源入口只能作参考，不能替代未制作的新C→A验收。</p><select id="seq">'+''.join(f'<option>{n}</option>' for n in seq)+'</select><button id="play">原速重播</button><button id="before">末项前1ms</button><button id="end">末项起点</button><p id="status"></p><div class="row">'+''.join('<div class="panel '+bg+'">'+''.join(f'<img class="probe" width="{96*s}" height="{104*s}">' for s in [1,2,3])+'</div>' for bg in ['light','dark'])+'</div>'
probe+='''<script>const images=IMAGES,sequences=SEQUENCES;let current='drag-pickup',start=performance.now(),fixed=null;const select=document.querySelector('#seq');select.onchange=()=>{current=select.value;fixed=null;start=performance.now()};document.querySelector('#play').onclick=()=>{fixed=null;start=performance.now()};function total(){return sequences[current].reduce((s,f)=>s+f.durationMs,0)}document.querySelector('#before').onclick=()=>fixed=Math.max(0,total()-sequences[current].at(-1).durationMs-1);document.querySelector('#end').onclick=()=>fixed=total()-sequences[current].at(-1).durationMs;function tick(){let fs=sequences[current],t=fixed===null?Math.min(performance.now()-start,total()-1):fixed,r=t,i=0;while(i<fs.length-1&&r>=fs[i].durationMs)r-=fs[i++].durationMs;let n=fs[i].path.slice(7,-4),key=n==='neutral'?'A':'old-'+n;document.querySelectorAll('.probe').forEach(el=>el.src=images[key]);document.querySelector('#status').textContent=current+' '+Math.floor(t)+'ms / '+total()+'ms · '+key+' · '+(fixed===null?'原速/到末项停止':'定位');requestAnimationFrame(tick)}tick()</script>'''.replace('IMAGES',json.dumps(images)).replace('SEQUENCES',json.dumps(seq))
html=html.replace(crops,probe+crops)
(R/'art024-inspection.html').write_text(html,encoding='utf-8')
(R/'art024-preview-report.json').write_text(json.dumps({'sources':{n:{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for n,p in paths.items()},'embeddedOriginalBytes':True},indent=2)+'\n',encoding='utf-8')
print('PASS original bytes embedded')
