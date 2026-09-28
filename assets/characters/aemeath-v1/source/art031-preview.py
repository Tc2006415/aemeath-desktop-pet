from pathlib import Path
R=Path(__file__).resolve().parent
text=(R/'art030-preview.py').read_text(encoding='utf-8-sig').replace('art030','art031')
text=text.replace('拿起动作v2','拿起 A+B 返修').replace('拿起动作v2','拿起 A+B 返修')
text=text.replace("pickStart=null,lastShown", "pickStart=null,pickVariant='A-base',lastShown")
text=text.replace("key='pick:'+pickupFrames[s.index]", "key='pick:'+pickVariant+'-'+pickupFrames[s.index]")
text=text.replace("const captured=lastShown;$('captured')", "const captured=lastShown;const [wing,pose,hem]=captured.slice(5).split('-');pickVariant=wing+'-'+hem;$('captured')")
text=text.replace("images['pick:neutral']", "images['pick:'+pickVariant+'-neutral']")
text=text.replace("captured==='idle:A-open-base'", "pose==='open'")
text=text.replace('本来源与首项A原PNG一致。','正常睁眼来源与首项原PNG一致；保留当前翼姿和衣摆层。')
text=text.replace('立即切到A：存在回正/收翼/表情或衣摆复位接缝，待用户判断。','立即恢复正常头脸：闭眼或wink回正仍可能跳变；翼姿和衣摆层保留。')
text=text.replace('首项A','首项正常头脸').replace('四项：neutral80 → 松腿惊讶80 → 收腿惊讶100 → 新持握入口100毫秒。B/C翼、闭眼、wink歪头或衣摆上扬切回A可能可见跳变，尚未实现专用入口衔接；本页没有等待原动作播完。','四项：基础80 → 轻张嘴80 → 足尖轻收100 → 同姿保持100毫秒。自然睁眼，原身体不变。翼从当前A→B、B→C、C保持，衣摆固定按下层；闭眼/wink回正仍可能跳变。本页不等待原动作播完。')
text=text.replace('49 actual PNGs embedded','81 actual PNGs embedded').replace('captured source comparison','captured source comparison; current wing and hem retained')
text=text.replace('模拟按下立即开始360毫秒拿起。', '本轮B轻收脚未通过视觉门槛：v1主要是足部色块变化，v2构图失败未采用。当前显示v1失败候选用于审看正常模型与A表情，不是通过版。模拟按下立即开始360毫秒拿起。')
text=text.replace('足尖轻收100', '足部尝试（未达标）100')
text=text.replace('正常睁眼来源与首项原PNG一致；保留当前翼姿和衣摆层。', '正常睁眼来源与首项原PNG一致；保留当前翼姿和衣摆层。B足部效果未达标。')
# Generate only new task preview; old generator and demo stay untouched.
exec(compile(text,str(R/'art031-preview.py'),'exec'))
