"""Read-only ART036/ART035 and DEV retained evidence verification. Starts no app."""
import hashlib, json, sys, xml.etree.ElementTree as ET
from pathlib import Path

candidate, reference, dev, output = map(Path, sys.argv[1:5])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((candidate/'manifest.json').read_bytes())
assert sha(candidate/'manifest.json')=='95cf8f8102f9631d0a02ae40a46fa497f61d9d423ff350191a399104a0a4b182'
b=manifest['behavior']; handoff=json.loads(reference.read_bytes()); images=b['images']
assert set(images)=={a['key'] for a in handoff['assets']} and len(images)==64
assert len({v['path'] for v in images.values()})==64
for a in handoff['assets']:
    entry=images[a['key']]; file=candidate/entry['path']
    assert file.stat().st_size==a['bytes'] and sha(file)==a['sha256']==entry['sha256']
for key,sequence in handoff['interaction']['releaseByCapturedKey'].items():
    actual=[{'key':key,'durationMs':b['interaction']['release']['sourceDurationMs']}]+b['interaction']['release']['tails'][b['interaction']['release']['routes'][key]]
    assert actual==sequence
fingerprints={
    'Aemeath.Host.exe':'9c266d8e594d5cd1d63af8c81252302c2fe2efbf85aa332946a4bed9b78208de',
    'Aemeath.Host.dll':'c33f8e0cb167b466a7f660705f9b622a7b2a606edc5cd00ba2dd44994dbc7610',
    'Aemeath.Presentation.dll':'6872a2184688b30d47edbb4dd5f375e5f04c7cea27ef1df395145ea902c1d385'}
for name,expected in fingerprints.items():assert sha(dev/'artifacts/native-v2-win-x64'/name)==expected
logs={}
for name,pid,action,count in [('automatic',17244,None,0),('manual-wink',56248,'idle-smile',4),('manual-release',54016,'drag-release',5)]:
    file=dev/f'artifacts/smoke-v2-{name}.jsonl'; events=[json.loads(line) for line in file.read_text(encoding='utf-8-sig').splitlines()]
    assert events[0]['kind']=='startup' and events[0]['data']['pid']==pid
    loaded=[e for e in events if e['kind']=='package-loaded']; assert len(loaded)==1
    package=loaded[0]['data']; assert package['SchemaVersion']==3 and package['Version']=='0.5.0' and package['ManifestSha256'].lower()==sha(candidate/'manifest.json') and not package['disabled']
    assert package['profile']=='layered-idle-drag-v1'
    inventory=[e['data'] for e in events if e['kind']=='behavior-inventory']; assert inventory==[{'keys':64,'combinations':45,'routes':64,'tails':5}]
    frames=[e['data'] for e in events if e['kind']=='frame']; assert frames
    submissions=[f['submission'] for f in frames]; assert submissions==sorted(set(submissions)) and min(submissions)>0
    for frame in frames: assert images[frame['FrameKey']]['path']==frame['path'] and frame['packageEpoch']==package['packageEpoch']
    phases=sorted({f['BehaviorPhase'] for f in frames})
    completed=[e['data']['completed'] for e in events if e['kind']=='natural-end']
    assert len(completed)==len(set(completed))
    if action:
        selected=[f for f in frames if f['Action']==action]
        assert sorted({f['FrameIndex'] for f in selected})==list(range(count)) and len(completed)==1
        for f in selected: assert f['path']==manifest['actions'][action]['frames'][f['FrameIndex']]['path']
    else: assert set(phases)=={'idle','blink'}
    kinds={e['kind'] for e in events}; assert {'render-callback','pet-stopped','shutdown'}<=kinds
    assert not {'package-rejected','position-error'}&kinds
    logs[name]={'pid':pid,'sha256':sha(file),'frames':len(frames),'phases':phases,'naturalEnds':len(completed),'shutdownLogged':True,'exitCodeEvidence':'DEV documented 0; not a QA-observed process wait'}
trx=dev/'tests/Aemeath.Presentation.Tests/TestResults/bigxi_SENJO_2026-09-29_17_29_31_net10.0.trx'
tree=ET.parse(trx); ns={'t':'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
counters=tree.find('.//t:Counters',ns).attrib
assert counters['total']==counters['executed']==counters['passed']=='48' and counters['failed']==counters['notExecuted']=='0'
cases=tree.findall('.//t:UnitTestResult',ns); assert len(cases)==48 and all(c.attrib['outcome']=='Passed' for c in cases)
report={'manifestBytes':(candidate/'manifest.json').stat().st_size,'keys':64,'uniquePngHashes':len({i['sha256'] for i in images.values()}),'compressedPngBytes':sum((candidate/i['path']).stat().st_size for i in images.values()),'art035RoutesMatched':64,'fingerprints':fingerprints,'logs':logs,'trx':{'sha256':sha(trx),'counters':counters},'evidenceLimit':'Retained DEV test/process evidence, not independently rerun; no native mouse or visual acceptance'}
output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,indent=2))
