"""Validate the authorized delta and bytes actually embedded in the final probe."""
import base64
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
old=json.loads((ROOT/'art016-build-report.json').read_text())
new=json.loads((ROOT/'art018-build-report.json').read_text())
html=(ROOT/'art018-inspection.html').read_text(encoding='utf-8')
data=json.loads(re.search(r'const data=(.*?),images=',html).group(1))
images=json.loads(re.search(r',images=(.*?),mode=',html).group(1))
assert data==new['timing']
changed=[i for i,(a,b) in enumerate(zip(old['timing']['hold'],data['hold'])) if a!=b]
assert changed==[8,9,18,19]
assert [data['hold'][i][1] for i in changed]==[100,140,100,140]
assert len(data['hold'])==20 and sum(x[1] for x in data['hold'])==1440
assert [i for i,x in enumerate(data['hold']) if x[0]=='closed']==[18]
assert all(data[k]==old['timing'][k] for k in ['pickup','release','routes'])
assert new['sources']['b7']['path']=='art017-v1-96.png'
assert [k for k in new['sources'] if new['sources'][k]!=old['sources'][k]]==['b7']
for k,v in new['sources'].items():
    blob=(ROOT/v['path']).read_bytes()
    assert base64.b64decode(images[k].split(',')[1])==blob
    assert hashlib.sha256(blob).hexdigest()==v['sha256']
assert 'art015-b7-v1' not in html
result={'passed':True,'changedHoldItemIndicesZeroBased':changed,'onlyChangedImageBinding':'b7 -> art017-v1-96.png','embeddedImages':len(images),'holdDurationMs':1440,'closedDurationMs':100,'routeArraysUnchanged':True,'nativeSourceRoutingImplemented':False,'sha256':hashlib.sha256(html.encode()).hexdigest()}
(ROOT/'art018-check-report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
