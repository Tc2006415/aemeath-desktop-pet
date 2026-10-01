"""Freeze input and explicit semantic edit mask; does not paint character pixels."""
import hashlib,json,runpy
from pathlib import Path
R=Path(__file__).resolve().parent
F=Path('C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1')
p=runpy.run_path(str(R/'export-neutral.py'))
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
protected={str(f):sha(f) for f in [F/'manifest.json',*sorted((F/'frames').glob('*.png'))]}
for n in ['neutral','smile-closed','hold-half','release-half']:
    (R/f'art023-original-{n}.png').write_bytes((F/f'frames/{n}.png').read_bytes())
assert sha(R/'art023-original-neutral.png')=='5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d'
# Row staircase follows the exposed wing below hair. Inner clothing starts beyond x30.
# Fixed root cuff is not copied from the generator. Mirrored right cuff also stays original.
limits={78:19,79:20,80:21,81:22,82:23,83:25,84:27,85:28,86:29,87:30,88:30,89:30,90:30,91:30,92:30,93:30,94:29,95:28,96:27,97:26,98:25,99:24}
roots={(x,y) for y in range(82,86) for x in range(24,28)}
roots|={(95-x,y) for x,y in list(roots)}
mask={(x,y) for y,end in limits.items() for x in range(8,end+1)}
mask|={(95-x,y) for x,y in list(mask)}
mask-=roots
rows=[bytearray(384) for _ in range(104)]
for x,y in mask:rows[y][4*x:4*x+4]=bytes([255]*4)
p['write_png'](R/'art023-mask-v1.png',96,104,rows)
data={'formalProtectedSHA':protected,'maskVersion':1,'maskCoordinatesXY':sorted(mask),'fixedRootCoordinatesXY':sorted(roots),'leftRowMaxX':limits,'rightMirrorsX95MinusX':True,'rootDescription':'original dark cuff under hair, left x24..27/y82..85 and mirror; protected even where transparent','protectedNonWing':'all outside mask, especially hair/sleeves/body x31..64 and stepped hair border','candidateRegistration':'none; format conversion only; no translation/rotation/warp','maskSHA':sha(R/'art023-mask-v1.png')}
(R/'art023-mask-definition.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print('Frozen original and mask v1; '+str(len(mask))+' editable samples; roots protected')
