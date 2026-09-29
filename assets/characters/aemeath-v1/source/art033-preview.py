from pathlib import Path
import json,base64
R=Path(__file__).resolve().parent
before={prefix+f.stem:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode() for folder,prefix in [('art029-frames','idle:'),('art032-frames','pose:')] for f in sorted((R/folder).glob('*.png'))}
s=(R/'art032-preview.py').read_text(encoding='utf-8-sig').replace('art032','art033').replace('ART032初版','ART033定向返修')
s=s.replace('阶段性预览，未完成全部美术要求：交替脚姿与收尾上扬翼已有候选；抬手／微屈读感偏弱，下弯嘴角在采样中丢失，轻恼主要依靠眉眼。六次生成已用完，不能视为完整通过版。袜靴色块与局部接缝也请审看。','本轮只返修轻恼嘴角与交替脚的袜靴色块，主视图默认新版；腿轮廓、幅度、手形、翼和时序保持。下方修改前／后对照取同一时刻同一姿态，可暂停逐帧比较。手部读感与已有回正接缝未在本轮修改，尚未原生接入。')
s=s.replace('<details><summary>', '<section><h2>修改前／修改后 · 同时间状态</h2><div class="compare"><figure><img id="before" alt="修改前同状态" width="288" height="312"><figcaption>修改前 ART032</figcaption></figure><figure><img id="after" alt="修改后同状态" width="288" height="312"><figcaption>修改后 ART033（主视图）</figcaption></figure></div></section><details><summary>',1)
s=s.replace('const images=IMAGEJSON,$=','const images=IMAGEJSON,oldImages=BEFOREJSON,$=')
s=s.replace('lastShown=key;',"lastShown=key;$('before').src=oldImages[key];$('after').src=images[key];")
s=s.replace("for(const id of ['light','dark']){$(id).width", "for(const id of ['light','dark','before','after']){$(id).width")
s=s.replace("html=html.replace('IMAGEJSON',json.dumps(images));", "html=html.replace('IMAGEJSON',json.dumps(images)).replace('BEFOREJSON',json.dumps(before));")
exec(compile(s,str(R/'art033-preview.py'),'exec'))
