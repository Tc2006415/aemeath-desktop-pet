"""Pinned ART036 byte-copy packaging and focused ADR0005 validation. No imaging APIs."""
from pathlib import Path
import subprocess,json,hashlib,re,sys
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent/'art036-package'
ART='2c31b27c99550f9002662cfb6f55181bd9fc0deb'
HANDOFF='651c7d0dd32fec9d3c31a4f5ec6aea20291410e8'
PM='15b2c32'
def blob(commit,path):return subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)
def digest(data):return hashlib.sha256(data).hexdigest()
def unique(pairs):
 result={}
 for k,v in pairs:
  assert k not in result,('duplicate JSON key',k)
  result[k]=v
 return result
def parse(data):return json.loads(data,object_pairs_hook=unique)
handoff=parse(blob(HANDOFF,'assets/characters/aemeath-v1/source/art035-handoff.json'))
base=parse(blob(PM,'assets/characters/aemeath-v1/manifest.json'))
def path(key):return 'frames/'+key.replace(':','-').lower()+'.png'
def track(values,durations,field='value'):return [{field:v,'durationMs':d} for v,d in zip(values,durations)]
images={r['key']:{'path':path(r['key']),'sha256':r['sha256']} for r in handoff['assets']}
wing=track(['A','B','C','C','B','A'],[400,150,150,400,150,150])
hem=track(['base','light','upper','light','base'],[400,150,650,150,50])
blink=track(['half','closed','half','open'],[60,80,60,40])
wink=track(['mid','wink','mid','open'],[250,450,350,150])
pickup=track(['pose:left-panic-B','pose:right-panic-C','pose:left-panic-A','pose:right-panic-B','pose:transition-annoyed-C'],[140,140,140,140,80],'key')
hold=track(['pose:annoyed-annoyed-'+w for w in ['A','B','C','B','A']],[400,150,550,150,150],'key')
tails={}
for name,body,face in [('normal','normal','normal'),('left-panic','left','panic'),('right-panic','right','panic'),('annoyed','annoyed','annoyed'),('transition','transition','annoyed')]:
 tails[name]=track([f'pose:{body}-{face}-H',f'pose:{body}-{face}-C','pose:normal-half-B','idle:A-open-base'],[100,100,120,160],'key')
routes={}
for key,seq in handoff['interaction']['releaseByCapturedKey'].items():
 matching=[name for name,tail in tails.items() if tail==seq[1:]]
 assert len(matching)==1
 routes[key]=matching[0]
neutral='idle:A-open-base'
actions={}
manual={
 'neutral':[{'key':neutral,'durationMs':base['actions']['neutral']['frames'][0]['durationMs']}],
 'idle-soft':[{'key':f"idle:{x['value']}-open-base",'durationMs':x['durationMs']} for x in wing],
 'idle-smile':[{'key':f"idle:A-{x['value']}-base",'durationMs':x['durationMs']} for x in wink],
 'drag-pickup':[{'key':neutral,'durationMs':60}]+pickup,
 'drag-hold':hold,
 'drag-release':[{'key':neutral,'durationMs':60}]+tails['normal']}
for name,seq in manual.items():
 actions[name]={'origin':base['actions'][name]['origin'],'playback':'loop' if name in ['neutral','idle-soft','drag-hold'] else 'once','frames':[{'path':images[x['key']]['path'],'durationMs':x['durationMs']} for x in seq]}
manifest={k:v for k,v in base.items() if k!='actions'}
manifest.update(schemaVersion=3,packageVersion='0.5.0',actions=actions)
manifest['behavior']={
 'profile':'layered-idle-drag-v1','images':images,'neutralKey':neutral,
 'idle':{'combinations':[{'wing':r['semantic']['wing'],'eyeHead':r['semantic']['eyeHead'],'hem':r['semantic']['hem'],'key':r['key']} for r in handoff['assets'] if r['key'].startswith('idle:')],
 'wing':wing,'hem':hem,'blink':{'waitMinMs':4000,'waitMaxMs':7000,'track':blink},'wink':{'waitMinMs':50000,'waitMaxMs':69999,'track':wink}},
 'interaction':{'pickup':{'sourceDurationMs':60,'tail':pickup},'hold':hold,'release':{'sourceDurationMs':60,'routes':routes,'tails':tails}}}
if '--check' not in sys.argv:
 (OUT/'frames').mkdir(parents=True,exist_ok=True)
 for r in handoff['assets']:
  data=blob(ART,r['path']);assert digest(data)==r['sha256'] and len(data)==r['bytes']
  (OUT/path(r['key'])).write_bytes(data)
 (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
actual=parse((OUT/'manifest.json').read_bytes());assert actual==manifest
assert len(images)==len(set(x['path'] for x in images.values()))==64
assert len(routes)==64 and len(tails)==5
assert set(routes)==set(images)
assert {p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file()}=={'manifest.json'}|{x['path'] for x in images.values()}
total=0
for r in handoff['assets']:
 key=r['key'];p=images[key]['path'];assert re.fullmatch(r'frames/[a-z0-9][a-z0-9_-]{0,63}\.png',p)
 assert re.fullmatch(r'[A-Za-z0-9:_-]{1,64}',key)
 data=(OUT/p).read_bytes();assert data==blob(ART,r['path']) and digest(data)==r['sha256']
 assert len(data)<=256*1024;total+=len(data)
comb=actual['behavior']['idle']['combinations']
assert {(x['wing'],x['eyeHead'],x['hem']) for x in comb}=={(w,e,h) for w in ['A','B','C'] for e in ['open','half','closed','mid','wink'] for h in ['base','light','upper']}
assert len(comb)==45 and all(x['key'] in images for x in comb)
for key,tail in routes.items():
 bound=[{'key':key,'durationMs':60}]+tails[tail]
 assert bound==handoff['interaction']['releaseByCapturedKey'][key]
 assert sum(x['durationMs'] for x in bound)==540
sequences=[wing,hem,blink,wink,pickup,hold,*tails.values(),*[a['frames'] for a in actions.values()]]
for seq in sequences:
 assert len(seq)<=64 and sum(x['durationMs'] for x in seq)<=60000
 assert all(1<=x['durationMs']<=10000 for x in seq)
 for x in seq:
  if 'key' in x:assert x['key'] in images
  if 'path' in x:assert sum(i['path']==x['path'] for i in images.values())==1
assert [sum(x['durationMs'] for x in s) for s in [wing,hem,blink,wink,pickup,hold]]==[1400,1400,240,1200,640,1400]
assert actions['neutral']['frames'][0]['path']==images[neutral]['path']
def depth(x):return 1+max((depth(v) for v in (x.values() if isinstance(x,dict) else x)),default=0) if isinstance(x,(dict,list)) else 0
size=(OUT/'manifest.json').stat().st_size;items=sum(map(len,sequences))+2
assert size<=65536 and total<=8*1024*1024 and depth(actual)<=8 and items<=256
assert items==78
print(json.dumps({'result':'PASS','pngFiles':64,'uniquePngSHA':len({r['sha256'] for r in handoff['assets']}),'pngBytes':total,'manifestBytes':size,'manifestSHA256':digest((OUT/'manifest.json').read_bytes()),'jsonContainerDepth':depth(actual),'idleCombinations':45,'releaseRoutes':64,'releaseTails':5,'behaviorTimingItems':51,'manualTimingItems':27,'totalTimingItems':items},indent=2))
