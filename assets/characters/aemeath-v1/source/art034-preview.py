from pathlib import Path
import json,base64,re
R=Path(__file__).resolve().parent
def table(folder):
 return {prefix+f.stem:'data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode() for directory,prefix in [('art029-frames','idle:'),(folder,'pose:')] for f in sorted((R/directory).glob('*.png'))}
new,old=table('art034-frames'),table('art033-frames')
for wing in ['C','H']:old['pose:transition-annoyed-'+wing]=old['pose:annoyed-annoyed-'+wing]
html=(R/'art033-demo.html').read_text(encoding='utf-8-sig')
html,n=re.subn(r'const images=.*?,oldImages=.*?,\$=id=>','const images='+json.dumps(new)+',oldImages='+json.dumps(old)+',$=id=>',html,count=1)
assert n==1
before=(R/'art033-track.js').read_text(encoding='utf-8-sig').strip()
after=(R/'art034-track.js').read_text(encoding='utf-8-sig').strip()
assert before in html
html=html.replace(before,after).replace('ART033定向返修','ART034轻嘟嘴与怒筋').replace('修改前 ART032','修改前 ART033').replace('修改后 ART033','修改后 ART034')
html=re.sub(r'(<p class="note" id="artStatus">).*?(</p>)',r'\1本轮把下弯嘴改为轻嘟嘴，并在右上头饰外透明区域加入固定暗粉红怒筋。默认新版；下方前后对照为同一时刻姿态。700毫秒前的过渡保持旧图无怒筋；恼怒循环与放下仍恼怒的帧同步更新，放下260毫秒进入舒展时移除。实际源快照保留60毫秒（含重抓入口）。仅网页候选，尚未原生接入；手形与已有入口接缝未调整。\2',html,count=1)
(R/'art034-demo.html').write_text(html,encoding='utf-8')
print('ART034 preview: 64 image keys per version; ART033 vs ART034 same-time comparison.')
