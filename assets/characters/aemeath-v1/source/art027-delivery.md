# ART027 自然眨眼初版 · 待用户审核

只制作自然眨眼，嘴部中性不变。交付自包含 `art027-demo.html` 和实际使用的 `art027-frames/` 9张PNG（A/B/C翼各睁开、半闭、闭合）；默认单独眨眼，可切换叠加已认可轻扇。完成后停止，等用户审核，不进入下一动作。

## 来源和合成

半闭眼复用imagegen来源的ART009 smile-half眼像素（来源SHA见build-report）；其嘴部未采用。旧闭眼为上弯笑眼，因此使用内置image_gen生成中性下弯闭眼1次（上限2），提示词在art027-closed-prompt.txt，原始生成图已复制为art027-closed-source-v1.png。未用CLI或程序绘眼。半闭/闭合各1版局部合成，3翼组合均复用同一眼姿。

生成前固定A的逻辑矩形[24,40,72,88)，精确24倍1152方形参考，保留原像素坐标。生成返回1254×1254方形；全格像素中心近邻采样48×48，放回(24,40)，alpha128，额外偏移0，无bbox重裁或变形。源中发线、嘴和衣领仍位于相应固定区域；只取204像素显式眼mask，粉发/脸颊排除，嘴部不在mask内。全部非眼区用原ART026相应翼帧，实际差分为0；没有改动已认可的ART026原文件。

## 实际验证

- `python assets/characters/aemeath-v1/source/art027-build.py`：退出0，半闭201/闭合204像素变化，全在mask内，眼区没有透明孔。
- `python assets/characters/aemeath-v1/source/art027-preview.py`：退出0，嵌入9张实际PNG。
- `python assets/characters/aemeath-v1/source/art027-check.py`：退出0，9图CRC、96×104 RGBA8、二值alpha、非眼区RGBA差0、A/B/C睁开精确字节、ART026保护SHA、HTML实际嵌入原PNG通过。
- `node assets/characters/aemeath-v1/source/art027-check-timing.cjs`：退出0。直接提取HTML实际纯时序函数，与ART026原时序对比完整28秒/28000个毫秒采样，翼轨道无重置；70个眨眼边界与3个逐帧边界检查通过。
- CUA浏览器实际打开：默认自动播放；3倍自然闭合深浅背景、1倍半闭、2倍叠加查看；逐帧到820ms闭合仍为C翼、回到760ms半闭仍为C翼、继续到1023ms睁开仍为C翼。暂停、上下帧、继续及两模式已核对。截图采样不是逐帧视频或原生桌宠验收。
- `git diff --cached --check` 提交前执行，变更仅art027系列及本人进度。

## 时序与限制

半闭60/闭合80/半闭60/睁开40ms，眨眼总240ms；首个眨眼从预览760ms开始，后续每4000ms起始一次。轻扇独立1400ms原时序，眼和翼按同一时间分别取样，再选择对应已保存PNG。4000ms间隔仅为演示，不代表生产调度；正式包、manifest及程序未修改。

闭合眼睫比旧笑眼更平、中央向下，初版自然程度由用户判断。B/C原已披露单像素透明点逐字节保留，未借机修翼。未重审A/B/C形状，未跑旧11帧/16入口或原生全套验证；不声称正式接入或零缺陷。所有SHA见build/check报告。请PM展示给用户后等待审核，自动跟进继续暂停。
