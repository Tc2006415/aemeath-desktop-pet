"""Bounded ART-009 candidate package; copies existing art, never draws character pixels."""
import base64
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('api', ROOT/'check-art007.py')
api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api);png=api.png
PACKAGE=ROOT/'art009-v1-package'


def load(path):
    w,h,r=png.read_png(path);assert (w,h)==(96,104);return r


def eye_mask(base):
    # Conservative eye-only scanline windows; pink hair/cheek baseline pixels excluded.
    spans={56:(33,41),57:(33,43),58:(32,44),59:(32,44),60:(32,44),61:(32,44),62:(32,44),63:(34,43),64:(35,42)}
    mask=set()
    for y,(lo,hi) in spans.items():
        for x0 in range(lo,hi+1):
            for x in (x0,95-x0):
                r,g,b,a=base[y][x*4:x*4+4]
                pink=r>130 and r>g*1.2 and b>g*1.12
                if a==255 and not pink:mask.add((x,y))
    mask.update((x,y) for y in range(65,68) for x in range(45,51))
    return mask


def feather_mask(base,donor):
    domain=set()
    for y in range(83,99):
        lo=15 if y<=84 else 12 if y<=87 else 8
        for x in range(lo,24):domain.update(((x,y),(95-x,y)))
    union=(api.occupied(base)|api.occupied(donor))&domain
    return {(x,y) for x,y in domain if any((x+dx,y+dy) in union for dx in (-1,0,1) for dy in (-1,0,1))}


def main():
    protected=[ROOT.parent/'manifest.json',*sorted((ROOT.parent/'frames').glob('*.png'))]
    hashes={str(p.relative_to(ROOT.parent)):api.sha(p) for p in protected}
    neutral=ROOT.parent/'frames/neutral.png';base=load(neutral)
    assert api.sha(neutral)=='5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d'
    (PACKAGE/'frames').mkdir(parents=True,exist_ok=True)
    (PACKAGE/'frames/neutral.png').write_bytes(neutral.read_bytes())
    reports=[]; pictures={'neutral':base}
    for name,source,kind in [('soft-light',ROOT.parent/'frames/soft-b.png','feather'),
                             ('soft-peak',ROOT/'art008-v2-96.png','accepted'),
                             ('smile-half',ROOT.parent/'frames/smile-half.png','face'),
                             ('smile-closed',ROOT.parent/'frames/smile-closed.png','face')]:
        donor=load(source)
        if kind=='accepted':
            mask=api.occupied(load(ROOT/'art008-v2-mask.png'))
        else:mask=eye_mask(base) if kind=='face' else feather_mask(base,donor)
        out=[bytearray(r) for r in base]
        maskrows=[bytearray(384) for _ in range(104)]
        for x,y in mask:
            if kind=='face':assert donor[y][x*4+3]==base[y][x*4+3]==255
            out[y][x*4:x*4+4]=donor[y][x*4:x*4+4]
            maskrows[y][x*4:x*4+4]=b'\xff\xff\xff\xff'
        dest=PACKAGE/'frames'/f'{name}.png'
        if kind=='accepted':dest.write_bytes(source.read_bytes());assert load(dest)==out
        else:png.write_png(dest,96,104,out)
        out=load(dest);pictures[name]=out
        png.write_png(ROOT/f'art009-v1-{name}-mask.png',96,104,maskrows)
        changed={(x,y) for y in range(104) for x in range(96) if out[y][x*4:x*4+4]!=base[y][x*4:x*4+4]}
        before,after=api.occupied(base),api.occupied(out)
        bounds=api.bounds(after);feet=api.bounds(api.occupied(out,(38,80,57,103)))[3]
        assert not changed-mask and bounds[1]==22 and feet==93
        assert {r[i] for r in out for i in range(3,384,4)}=={0,255} and dest.stat().st_size<=262144
        assert 4<=bounds[0] and bounds[2]<=91 and bounds[3]<=99
        if kind=='face':assert before==after and all(32<=x<=63 and 56<=y<=67 for x,y in changed)
        else:assert all(y>=83 and (x<=23 or x>=72) for x,y in changed)
        report={'frame':name,'sourceRelativeToCharacter':str(source.relative_to(ROOT.parent)), 'sourceSha256':api.sha(source),
                'frameSha256':api.sha(dest),'bytes':dest.stat().st_size,'bounds':bounds,'feetBottomY':feet,
                'maskVersion':2 if kind=='accepted' else 1,'maskOrigin':'ART-008 accepted' if kind=='accepted' else 'ART-009',
                'maskPixels':len(mask),'maskCoordinatesXY':sorted(mask,key=lambda p:(p[1],p[0])),
                'outsideMaskRgbaChanges':len(changed-mask),'rgbaChanges':len(changed),'alphaChanges':len(before^after),
                'clearedOldOpaque':len(before-after),'addedOpaque':len(after-before)}
        if kind!='face':
            report['feathers']={}
            for side,box in [('left',(0,82,33,103)),('right',(62,82,95,103))]:
                a,b=api.occupied(base,box),api.occupied(out,box);ba,bb=api.bounds(a),api.bounds(b)
                distance=max(max((min(max(abs(x-xx),abs(y-yy)) for xx,yy in b) for x,y in a-b),default=0),
                             max((min(max(abs(x-xx),abs(y-yy)) for xx,yy in a) for x,y in b-a),default=0))
                report['feathers'][side]={'inward':bb[0]-ba[0] if side=='left' else ba[2]-bb[2],
                                          'opaqueDistance':distance,'alphaChanges':len(a^b),'bounds':bb}
        reports.append(report)
        for bgname,bg in [('light',(245,245,245)),('dark',(35,39,47))]:
            for scale in (1,3):
                preview=[]
                for y in range(104):
                    row=base[y]+out[y]
                    pixels=[row[i:i+4] if row[i+3] else bytes((*bg,255)) for i in range(0,len(row),4)]
                    rr=bytearray(b''.join(p*scale for p in pixels));preview.extend([rr]*scale)
                png.write_png(ROOT/f'art009-v1-{name}-{bgname}-{scale}x.png',192*scale,104*scale,preview)
    assert pictures['soft-light']!=pictures['soft-peak']
    manifest={'schemaVersion':1,'packageId':'aemeath-v1','packageVersion':'0.3.0','packageKind':'character','sourceScale':1,
              'frameSize':{'width':96,'height':104},'anchor':{'x':48,'y':94},'fallbackAction':'neutral','actions':{}}
    def clip(name,origin,playback,names,times):
        manifest['actions'][name]={'origin':origin,'playback':playback,'frames':[{'path':f'frames/{n}.png','durationMs':t} for n,t in zip(names,times)]}
    clip('neutral','original','loop',['neutral'],[1000])
    clip('idle-soft','original','loop',['neutral','soft-light','soft-peak','soft-peak','soft-light','neutral'],[400,150,150,400,150,150])
    clip('idle-smile','adaptation','once',['neutral','smile-half','smile-closed','smile-half','neutral','neutral'],[120,120,500,120,120,220])
    (PACKAGE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    for action,total in [('idle-soft',1400),('idle-smile',1200)]:
        assert len(manifest['actions'][action]['frames'])==6
        assert sum(f['durationMs'] for f in manifest['actions'][action]['frames'])==total
    assert hashes=={str(p.relative_to(ROOT.parent)):api.sha(p) for p in protected}
    report={'neutralSha256':api.sha(neutral),'protectedHashes':hashes,'candidateManifestSha256':api.sha(PACKAGE/'manifest.json'),
            'frameReports':reports,'formatAndMaskChecks':'PASS; visual checks separate',
            'eyeMaskRule':'listed scanline windows mirrored x->95-x; exclude baseline pink hair/cheek: R>130 and R>1.2G and B>1.12G; mouth x45..50,y65..67',
            'eyeScanlines':{'56':[33,41],'57':[33,43],'58to62':[32,44],'63':[34,43],'64':[35,42]}}
    (ROOT/'art009-v1-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v for k,v in r.items() if k!='maskCoordinatesXY'} for r in reports],indent=2))


if __name__=='__main__':main()
