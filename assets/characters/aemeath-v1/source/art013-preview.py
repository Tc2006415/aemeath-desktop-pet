"""Reuse inspected ART-011 web simulator with final ART-013 package and new scenarios."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent
text=(ROOT/'art011-preview.py').read_text(encoding='utf-8').replace('art011','art013').replace('ART-011','ART-013')
text=text.replace('embedded 12 images','embedded 13 images').replace('4200','6000')
text=text.replace("normal:[[400,'down'],[2500,'up']]", "normal:[[400,'down'],[4000,'up']],wingup:[[400,'down'],[1040,'up']],wingdown:[[400,'down'],[1400,'up']]")
text=text.replace('<option value="quick">','<option value="wingup">情境：上扬时松手</option><option value="wingdown">情境：下压时松手</option><option value="quick">')
text=text.replace('情境：按下→保持→松手','情境：长按至少3循环→松手')
text=text.replace('hold：微笑 / 羽饰轻+微笑 / 羽饰峰+闭眼 / 羽饰轻+微笑，各180ms','hold：中位微笑 / 上扬微笑 / 中位闭眼 / 下压微笑，各180ms')
text=text.replace('拿起轻惊讶 → 悬停眯眼微笑/眨眼 → 落稳闭眼笑 → neutral；头饰固定。','中幅扇翼：中位→上扬→中位→下压，720ms；拿起惊讶，悬停微笑/眨眼，落稳笑后恢复。网页非原生验收。')
exec(compile(text,str(ROOT/'art013-preview.py'),'exec'),{'__file__':str(ROOT/'art013-preview.py'),'__name__':'__main__'})
