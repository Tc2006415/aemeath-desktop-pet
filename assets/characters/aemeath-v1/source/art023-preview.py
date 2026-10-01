import base64,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
names=['original-neutral','v1-candidate-96']
if (R/'art023-v2-candidate-96.png').exists(): names+=['v2-candidate-96']
names+=['original-smile-closed','original-hold-half','original-release-half']
data={n:(R/f'art023-{n}.png').read_bytes() for n in names}
uri=lambda b:'data:image/png;base64,'+base64.b64encode(b).decode()
sections=''
for n,b in data.items():
    panels=''.join('<div class="panel '+bg+'">'+bg+' '+''.join(f'<img alt="{n}-{bg}-{s}x" width="{96*s}" height="{104*s}" src="{uri(b)}">' for s in [1,2,3])+'</div>' for bg in ['light','dark'])
    sections+=f'<section><h2>{n}</h2><div class="row">{panels}</div></section>'
html='''<!doctype html><meta charset="utf-8"><title>ART-023 A单帧对照</title><style>body{font:14px system-ui;background:#eee;margin:12px}h1{font-size:22px}h2{font-size:17px;margin:10px 0}.row{display:flex;gap:8px}.panel{display:flex;align-items:end;gap:2px;padding:5px;font-size:10px}.light{background:#f0efeb}.dark{background:#1d222c;color:white}img{image-rendering:pixelated}section{margin-bottom:18px}</style><h1>ART-023 · A单帧候选对照</h1><p>原PNG字节，浅深1×/2×/3×。仅A造型门槛，未制B/C；旧拖动衔接不代表无缝。</p>'''+sections
gallery='<h2>并列2×：基准 / A / 笑脸 / hold / release</h2><div class="row">'+''.join(f'<div>{n}<br><img width="192" height="208" src="{uri(b)}"></div>' for n,b in data.items())+'</div>'
crops='<h2>根部与语义遮罩10×（原图 / donor / 合成）</h2><div class="row">'
for n in (['original-neutral','v2-donor-96','v2-candidate-96','v1-candidate-96'] if 'v2-candidate-96' in data else ['original-neutral','v1-donor-96','v1-candidate-96']):
    b=(R/f'art023-{n}.png').read_bytes()
    crops+=f'<div>{n}'+''.join(f'<div style="position:relative;width:280px;height:220px;overflow:hidden;background:#1d222c"><img style="position:absolute;max-width:none;left:-{x*10}px;top:-780px;width:960px;height:1040px" src="{uri(b)}"></div>' for x in [8,60])+'</div>'
crops+='</div><p>mask白色可改；黑/透明保护，含两侧原翼根袖口。mask并非角色图。</p><img width="384" height="416" class="dark" src="'+uri((R/'art023-mask-v1.png').read_bytes())+'">'
html=html.replace(sections,gallery+crops+sections)
html=html.replace('<h1>', '<p style="color:#a00;font-weight:bold">两版均未通过A造型门槛，仅保留失败证据，禁止集成。生成2次/合成2版，已停止。</p><h1>',1)
(R/'art023-inspection.html').write_text(html,encoding='utf-8')
(R/'art023-preview-report.json').write_text(json.dumps({'images':{n:hashlib.sha256(b).hexdigest() for n,b in data.items()},'bytesEmbeddedUnchanged':True,'scales':[1,2,3],'backgrounds':['light','dark'],'nativeAcceptance':False},indent=2)+'\n',encoding='utf-8')
assert all(base64.b64decode(uri(b).split(',')[1])==b for b in data.values())
print('PASS embedded original PNG bytes')
