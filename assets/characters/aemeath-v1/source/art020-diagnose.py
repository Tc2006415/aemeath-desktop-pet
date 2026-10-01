"""Read-only inspection of formal0.4 idle-soft; raw PNG display only."""
import base64
import hashlib
import json
import re
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FORMAL=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
png=runpy.run_path(str(ROOT/'export-neutral.py'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((FORMAL/'manifest.json').read_bytes())
protected={str(p):sha(p) for p in [FORMAL/'manifest.json',*sorted((FORMAL/'frames').glob('*.png'))]}
assert manifest['packageVersion']=='0.4.0'
names=['neutral','soft-light','soft-peak']
report={'formalManifestSha256':sha(FORMAL/'manifest.json'),'idleSoft':manifest['actions']['idle-soft'],'frames':{}}
decoded={n:png['read_png'](FORMAL/f'frames/{n}.png')[2] for n in names}
def occupied(rows):return {(x,y) for y in range(104) for x in range(96) if rows[y][x*4+3]}
for name,rows in decoded.items():
    remaining=occupied(rows);components=[]
    while remaining:
        seed=remaining.pop();part={seed};pending=[seed]
        while pending:
            x,y=pending.pop()
            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    q=(x+dx,y+dy)
                    if q in remaining:remaining.remove(q);part.add(q);pending.append(q)
        components.append(part)
    small=[sorted(c) for c in components if len(c)<100 and any(y>=82 and (x<=32 or x>=63) for x,y in c)]
    entry={'sha256':sha(FORMAL/f'frames/{name}.png'),'matchesArt019':(FORMAL/f'frames/{name}.png').read_bytes()==(ROOT/f'art019-package/frames/{name}.png').read_bytes(),'smallDetachedWingComponents8Connected':small}
    if name!='neutral':
        mask=occupied(png['read_png'](ROOT/('art009-v1-soft-light-mask.png' if name=='soft-light' else 'art008-v2-mask.png'))[2])
        changes={(x,y) for y in range(104) for x in range(96) if rows[y][x*4:x*4+4]!=decoded['neutral'][y][x*4:x*4+4]}
        entry.update({'changedPixels':len(changes),'outsideHistoricalMask':sorted(changes-mask),'clearedOpaque':sorted(occupied(decoded['neutral'])-occupied(rows)),'addedOpaque':sorted(occupied(rows)-occupied(decoded['neutral']))})
    report['frames'][name]=entry
    print(name,'detached',small)
    for y in range(84,99):
        line=''
        for x in range(8,31):
            r,g,b,a=rows[y][x*4:x*4+4]
            line+=('.' if not a else 'W' if min(r,g,b)>150 else '#')
        print(f'{y:02} {line[:16]}|{line[16:]}')
images={n:'data:image/png;base64,'+base64.b64encode((FORMAL/f'frames/{n}.png').read_bytes()).decode() for n in names}
points=[(20,92),(20,93),(75,92),(75,93),(76,90),(24,91),(71,91)]
report['pixelEvidence']={n:{f'{x},{y}':list(rows[y][x*4:x*4+4]) for x,y in points} for n,rows in decoded.items()}
report['historicalReconstruction']={}
for n,donorname,maskname in [('soft-light','../frames/soft-b.png','art009-v1-soft-light-mask.png'),('soft-peak','art007-trial-v1-96.png','art008-v2-mask.png')]:
    donorpath=ROOT/donorname;donor=png['read_png'](donorpath)[2]
    mask=occupied(png['read_png'](ROOT/maskname)[2])
    assert all(decoded[n][y][x*4:x*4+4]==(donor if (x,y) in mask else decoded['neutral'])[y][x*4:x*4+4] for y in range(104) for x in range(96))
    report['historicalReconstruction'][n]={'donor':donorname,'donorSha256':sha(donorpath),'mask':maskname,'maskSha256':sha(ROOT/maskname),'exactRgbaRecipeMatches':True,'donorPixelEvidence':{f'{x},{y}':list(donor[y][x*4:x*4+4]) for x,y in points}}
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>ART-020 idle-soft只读诊断</title><style>body{font:15px system-ui;margin:16px;background:#ddd}img{image-rendering:pixelated}.row{display:flex;gap:12px}.box{background:#f0efeb;padding:8px}.dark{background:#1d222c;color:white}.big{width:288px;height:312px}.crop{width:230px;height:190px;overflow:hidden;position:relative;background:#1d222c}.crop img{position:absolute;width:960px;height:1040px;max-width:none}.boundary{position:absolute;left:160px;top:0;height:190px;border-left:1px solid #e7ae20;pointer-events:none}button{padding:8px}p{margin:6px 0}</style><h1>ART-020 · 正式0.4 idle-soft诊断</h1><p>原始PNG逐字节内嵌；仅CSS整数放大/窗口查看，未生成或改动角色像素。坐标从0开始。</p><div class="row">']
for n in names:parts.append(f'<div class="box"><b>{n}</b><br><img src="{images[n]}"><br><img class="big" src="{images[n]}"></div>')
parts.append('</div><h2>左翅尾：x8..30 y82..100，10×，金线为x24起点</h2><div class="row">')
for n in names:parts.append(f'<div><p>{n}</p><div class="crop"><img style="left:-80px;top:-820px" src="{images[n]}"><span class="boundary"></span></div></div>')
parts.append('</div><h2>右翅尾：x65..87 y82..100，10×</h2><div class="row">')
for n in names:parts.append(f'<div><p>{n}</p><div class="crop"><img style="left:-650px;top:-820px" src="{images[n]}"></div></div>')
parts.append('</div><h2>原idle-soft时序播放（网页非原生）</h2><button id="play">重播</button><button id="pause">暂停</button><p id="status"></p><div class="row"><div class="box"><img id="one"><img class="big" id="large"></div><div class="box dark"><img id="oneDark"><img class="big" id="largeDark"></div></div>')
parts.append('<script>const images='+json.dumps(images)+',frames='+json.dumps(manifest['actions']['idle-soft']['frames'])+''';let start=performance.now(),paused=false,elapsed=0;function draw(){let t=paused?elapsed:performance.now()-start,r=t%1400,i=0;while(i<frames.length-1&&r>=frames[i].durationMs)r-=frames[i++].durationMs;let n=frames[i].path.slice(7,-4);for(const id of ['one','large','oneDark','largeDark'])document.getElementById(id).src=images[n];document.getElementById('status').textContent=`${paused?'暂停':'播放'} ${Math.floor(t)}ms 项${i+1} ${n}`;requestAnimationFrame(draw)}document.getElementById('play').onclick=()=>{start=performance.now();paused=false};document.getElementById('pause').onclick=()=>{if(paused){start=performance.now()-elapsed;paused=false}else{elapsed=performance.now()-start;paused=true}};draw();</script></html>''')
(ROOT/'art020-inspection.html').write_text(''.join(parts),encoding='utf-8')
embedded=json.loads(re.search(r'const images=(.*?),frames=', ''.join(parts)).group(1))
assert all(base64.b64decode(v.split(',')[1])==(FORMAL/f'frames/{n}.png').read_bytes() for n,v in embedded.items())
assert protected=={p:sha(Path(p)) for p in protected}
report['protectedHashesUnchanged']=protected
report['embeddedRawPngBytesMatch']=True
(ROOT/'art020-pixel-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
