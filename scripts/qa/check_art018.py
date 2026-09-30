"""Independent read-only checks of the ART-018 visual probe, not a host package."""
import base64
import hashlib
import json
import subprocess
from pathlib import Path
from png_readonly import png

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'artifacts/qa008-art-5a61f0e/assets/characters/aemeath-v1/source'
LIVE=Path('C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source')
raw=(SOURCE/'art018-inspection.html').read_bytes()
assert raw==(LIVE/'art018-inspection.html').read_bytes()
sha=hashlib.sha256(raw).hexdigest()
assert sha=='9b4232ebd6c6d170f1c24bc63c2e4280f5170672d77ce3f271bfb09c4936486a'
git_blob=subprocess.run(['git','show','5a61f0e096441caed5a2d0fff017b6dfbc337bfc:assets/characters/aemeath-v1/source/art018-inspection.html'],cwd=ROOT,check=True,capture_output=True).stdout
assert raw.replace(b'\r\n',b'\n')==git_blob
assert hashlib.sha256(git_blob).hexdigest()=='f53b38a87ff642842638a01621ac06de74fb9383da69ec106453b5d2a4c8f4a2'
html=raw.decode('utf-8')
data,_=json.JSONDecoder().raw_decode(html.split('const data=',1)[1])
images,_=json.JSONDecoder().raw_decode(html.split(',images=',1)[1])
build=json.loads((SOURCE/'art018-build-report.json').read_bytes())
prior=json.loads((SOURCE/'art016-build-report.json').read_bytes())
assert data==build['timing'] and len(images)==12
assert set(images)==set(build['sources'])
assert [key for key in build['sources'] if build['sources'][key]!=prior['sources'][key]]==['b7']
assert build['sources']['b7']['path']=='art017-v1-96.png'
assert [i for i,(a,b) in enumerate(zip(data['hold'],prior['timing']['hold'])) if a!=b]==[8,9,18,19]
assert [data['hold'][i][1] for i in [8,9,18,19]]==[100,140,100,140]
assert len(data['hold'])==20 and sum(item[1] for item in data['hold'])==1440
assert [(i,t) for i,(f,t) in enumerate(data['hold']) if f=='closed']==[(18,100)]
for key in ['pickup','release','routes']: assert data[key]==prior['timing'][key]
read=lambda path: png(path)[2]
pictures={}
entries={}
for key,meta in build['sources'].items():
    path=SOURCE/meta['path']; blob=path.read_bytes()
    assert blob==(LIVE/meta['path']).read_bytes()
    assert base64.b64decode(images[key].split(',',1)[1])==blob
    assert hashlib.sha256(blob).hexdigest()==meta['sha256']
    pixels=read(path); pictures[key]=pixels
    points=[(i%96,i//96) for i,p in enumerate(pixels) if p[3]]
    bounds=[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)]
    assert bounds[0]>0 and bounds[1]==22 and bounds[2]<95 and bounds[3]<103
    entries[key]={'source':meta['path'],'sha256':meta['sha256'],'bytes':len(blob),'bounds':bounds}
neutral=pictures['neutral']; mid=pictures['mid']
face={i for i,p in enumerate(read(SOURCE/'art011-face-mask.png')) if p[3]}
wing={i for i,p in enumerate(read(SOURCE/'art012-wing-mask-v1.png')) if p[3]}
for key,pixels in pictures.items():
    upper_changed=[i for i,p in enumerate(pixels) if i//96<75 and i not in face and p!=neutral[i]]
    assert not upper_changed
    entries[key]['upperProtectedChanges']=len(upper_changed)
for key in ['b2','b4','b7','up','down']:
    outside=[i for i,p in enumerate(pictures[key]) if i not in wing and p!=mid[i]]
    assert not outside
    entries[key]['outsideWingChanges']=0
mask={i for i,p in enumerate(read(SOURCE/'art017-mask-v1.png')) if p[3]}
expected_mask={i for i in wing if i%96<=23 or (i%96<=26 and i//96>=93) or i%96>=72 or (i%96>=69 and i//96>=93)}
assert mask==expected_mask
old=read(SOURCE/'art015-b7-v1-96.png'); donor=read(SOURCE/'art017-v1-donor.png'); b7=pictures['b7']
assert all(p==(donor[i] if i in mask else old[i]) for i,p in enumerate(b7))
changes={i for i,p in enumerate(b7) if p!=old[i]}
assert changes and not changes-mask
result={'fixedCommit':'5a61f0e096441caed5a2d0fff017b6dfbc337bfc','actualHtmlSha256':sha,'taskCardHtmlSha256':'f53b38a87ff642842638a01621ac06de74fb9383da69ec106453b5d2a4c8f4a2','liveEqualsCommit':True,'formatAndSources':'PASS','images':entries,'newB7Changes':len(changes),'newB7MaskPixels':len(mask),'newB7OutsideMask':0,'holdItems':20,'holdMs':1440,'closedItems':[[18,100]],'routesUnchanged':True,'notNativeAcceptance':True}
result.update(rawBytes=len(raw),gitBlobBytes=len(git_blob),hashDifference='CRLF vs LF only; verified against actual git blob')
(ROOT/'artifacts/qa008-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
