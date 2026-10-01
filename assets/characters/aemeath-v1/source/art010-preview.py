"""Comparison previews only; no character pixels painted."""
import runpy
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
png = runpy.run_path(str(ROOT/'export-neutral.py'))
items = {'neutral': ROOT/'art010-baseline/frames/neutral.png'}
for pose in ['pickup','hold','release']:
    version = 2 if pose == 'hold' and (ROOT/'art010-hold-v2-96.png').exists() else 1
    candidate = ROOT/f'art010-{pose}-v{version}-96.png'
    if candidate.exists():
        items[pose] = candidate
urls = {n:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for n,p in items.items()}
for theme,bg in [('light',(240,239,235,255)),('dark',(29,34,44,255))]:
    for scale in [1,4]:
        output=[]
        decoded=[png['read_png'](p)[2] for p in items.values()]
        for y in range(104):
            row=bytearray()
            for rows in decoded:
                for x in range(96):
                    pixel=rows[y][x*4:x*4+4]
                    row.extend((pixel if pixel[3] else bytes(bg))*scale)
            output.extend([row]*scale)
        png['write_png'](ROOT/f'art010-compare-{theme}-{scale}x.png',96*len(items)*scale,104*scale,output)
html='''<!doctype html><meta charset="utf-8"><title>ART-010 key poses</title>
<style>body{font:16px system-ui;background:#eee;padding:16px}img{image-rendering:pixelated}.grid{display:flex;gap:12px}.card{padding:12px;background:#f0efeb}.dark{background:#1d222c;color:white}.large{width:384px;height:416px}button{padding:12px;margin:4px}h2{margin:6px}</style>
<h1>ART-010 · 三个关键姿态 · 无正式动作时序</h1><p>头冠/头发/面部锁定；锚点 (48,94)。切换用于接缝检查，不代表最终动画。</p><nav></nav><h2 id="state">neutral</h2><div class="grid"><div class="card"><img class="large"><img></div><div class="card dark"><img class="large"><img></div></div><h2>neutral / pickup / hold / release</h2><div id="strip"></div>
<script>const images=DATA;function show(n){document.querySelector('#state').textContent=n;document.querySelectorAll('.card img').forEach(i=>i.src=images[n]);}for(const n of Object.keys(images)){const b=document.createElement('button');b.textContent=n;b.onclick=()=>show(n);document.querySelector('nav').append(b);}document.querySelector('#strip').innerHTML=Object.entries(images).map(([n,s])=>`<img title="${n}" src="${s}" width="192" height="208">`).join('');show('neutral');</script>'''
(ROOT/'art010-inspection.html').write_text(html.replace('DATA',json.dumps(urls)),encoding='utf-8')
print('Preview order:',', '.join(items))
