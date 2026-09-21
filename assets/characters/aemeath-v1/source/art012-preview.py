"""Key pose comparison only, no animation timings or package modifications."""
import base64
import json
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
png=runpy.run_path(str(ROOT/'export-neutral.py'))
items={'reference-hold':ROOT/'art011-package/frames/hold-half.png','wing-up':ROOT/'art012-up-v2-96.png','wing-down':ROOT/'art012-down-v1-96.png'}
decoded=[png['read_png'](p)[2] for p in items.values()]
for theme,bg in [('light',(240,239,235,255)),('dark',(29,34,44,255))]:
    for scale in [1,3]:
        out=[]
        for y in range(104):
            row=bytearray()
            for picture in decoded:
                for x in range(96):
                    p=picture[y][x*4:x*4+4]
                    row.extend((p if p[3] else bytes(bg))*scale)
            out.extend([row]*scale)
        png['write_png'](ROOT/f'art012-compare-{theme}-{scale}x.png',288*scale,104*scale,out)
urls={n:'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for n,p in items.items()}
html='''<!doctype html><meta charset="utf-8"><title>ART-012 wing key poses</title><style>body{font:16px system-ui;background:#eee}img{image-rendering:pixelated}.card{display:inline-block;padding:14px;background:#f0efeb}.dark{background:#1d222c}.large{width:288px;height:312px}button{padding:12px;margin:5px}</style><h1>ART-012 · 翼部两端试样</h1><p>reference-hold / wing-up / wing-down。只有关键姿态，没有完整扇动时序。头部、身体、表情锁定。</p><nav></nav><h2 id="state"></h2><div class="card"><img class="large"><img></div><div class="card dark"><img class="large"><img></div><h2>并排3×</h2><div id="strip"></div><script>const images=DATA;function show(n){document.querySelector('#state').textContent=n;document.querySelectorAll('.card img').forEach(i=>i.src=images[n]);}for(const n of Object.keys(images)){let b=document.createElement('button');b.textContent=n;b.onclick=()=>show(n);document.querySelector('nav').append(b);}document.querySelector('#strip').innerHTML=Object.entries(images).map(([n,s])=>`<img title="${n}" class="large" src="${s}">`).join('');show('reference-hold');</script>'''
(ROOT/'art012-inspection.html').write_text(html.replace('DATA',json.dumps(urls)),encoding='utf-8')
print('PASS: key-pose comparison only, reference/up/down, light/dark 1x/3x')
