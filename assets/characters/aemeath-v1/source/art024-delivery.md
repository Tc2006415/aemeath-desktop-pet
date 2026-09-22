# ART-024 · A固定，B制作失败，按单姿态上限停止

**本轮未交成五张核心候选。A保持用户认可；B两次尝试均失败，C和两张笑脸没有制作。** 不将A的已接受内羽/根尖造型重新判失败，也不以旧neutral/v1翼替换A。B已用完2次生成、2版合成，故停止依赖此过渡的C及核心组扩展；总imagegen2/4，C0/2。这不是用B次数挪给C或另开版本续试。

## 固定输入、来源及参数

art024-neutral-A.png为用户选中的ART023-v2精确字节副本，SHA `e2f90c5dc97a24b9dc7714776d575fafe56791b9dc568e03f152b111badbe6c8`。不重画、不重新编码A。既有A外观选择覆盖ART023先前主观FAIL，历史记录不改写。

沿用已标定整翼语义mask：art024-wing-mask-v1.png，SHA `d73ca172573f5f5c43b75a8d2561ab8e79ed5d026b38651de48ba311aa34404a`，共838可动样本；不是矩形包络全填。固定翼根左x24..27/y82..85、右镜像x68..71/y82..85不动；所有mask外RGBA保持A，包括衣袖/发尾/头饰/脸身脚及anchor(48,94)。mask-definition保存逐点坐标、阶梯边界和正式17文件SHA。两尝试共用此mask，没有扩大保护区来接纳偏位生成图。

每次返回1205×1305，仅执行像素中心最近邻至96×104、alpha阈值128及显式mask局部RGBA合成。无平移/旋转/扭曲、无羽片程序绘制、无整角色变换、无历史+5配准。生成源的非翼区域发生重绘，不能采用；合成只保留许可翼部样本，原A非翼全部原样。

|尝试|源图SHA|合成SHA|RGBA差分/可动区实心像素|
|---|---|---|---|
|B v1|5e7036c98c547993d3dca482dc6a46429c14674aa6f5b27cb67f57db1303a7fd|bbe5d8308529aa78f7227289d8acb2f0fc3256ad43dbd87fbe9a8441ca751ccc|192 / 10|
|B v2|58c75712df9464efcab970e10074a2f3ecf0f13f4c8f3402655835263ad84a6b|e67a59a7709f0b7599a496c78990927ece78a4a2fc1e5e5c8b5aaab69c054715|234 / 116|

A在同一mask内有182个实心像素。完整prompt、源、donor和未通过候选分别为art024-B-vN-prompt.txt/source.png/donor-96.png/candidate-96.png，逐点差分和参数在report.json。均用内置imagegen，没有CLI/API替代。

## 具体失败依据

第一版生成将翼部放得过高，不是A的轻微整体上抬。固定画布格式转换与保护合成后，A原可动区182个实心位置全部消失，仅在别处保留10个实心像素，形成左右各5像素孤立块。实看不成完整翼。失败后才使用第二次，prompt明确约束外尖只上抬2px、根部不动、不要移到腰肩高度、保持三羽身份。

第二版回到较低位置，但仍丢失羽片长度/层次：可动区实心降为116，A原实心中118个被清除。10×左右对照显示主羽缩短、上移过多，内中羽变成短块；浅深1/2/3×也能看到由A展开扇面变成短翼，而非同一三羽扇面轻抬。没有新封闭透明孔、没有孤块（全图单8邻接分量2845），仍不能以连通合格替代动作身份连续性。

本轮失败是**B未延续已选A**，不是重新否定A的内羽或根尖。不得挑B2“勉强连通”制作笑脸，亦不得用程序把偏位donor下移来掩盖源图不合格。达B上限后，没有可供C/笑脸与往返验证使用的合格B，故未继续花费C生成额度。

## 五帧与动态检查状态

- neutral=A：精确字节交付，可继续作为后续固定输入。
- soft-light=B：两尝试失败，未选定。
- soft-peak=C、smile-half=B翼、smile-closed=C翼：未制作。没有新脸生成或虚构表情合成结果。
- 正式idle-soft1400ms、idle-smile1200ms原数组已读取并保留，manifest未修改；**没有完整五核心原速循环可验**，不将A/B失败往返或旧动作冒充已通过的1400/1200ms新动画。

## 旧11帧与入口/出口只读观察

预览内包含全部旧16PNG原字节，旧11非核心帧为hold-surprise、pickup-surprise、hold-half、hold-mid-closed、release-closed、release-half、hold-bridge-low/mid/high、hold-up-half、hold-down-half；未修改。页面另有“仅neutral显示A，其余原帧”的边界诊断，保持原数组和时长。它不代表新五帧或生产宿主验收。

|边界|本轮可确认的影响|
|---|---|
|pickup A80→旧hold-surprise→pickup-surprise→hold-half|静态对照显示A翼较薄外展，后三张恢复旧长中羽/分组翼形，会有形态切换；没有通过无缝门槛|
|hold低位hold-half↔bridge-low及down↔hold-half|11旧帧都没变，原内部边界没有由本轮新增像素变化；它们与新A的羽形不同，不能自动视为与未来B/C兼容|
|基础release|浏览器实看299ms旧release-half与300ms新A：翼长、羽尖位置和展开方向明显切换，同时有原本的身/表情收尾变化。需后续依赖同步，不可直接集成|
|16入口终点|文件检查全部末项frames/neutral.png160ms。11个非idle且非neutral入口的前项为旧release-half，具有同一旧翼→A风险；neutral入口自身只有A160，无翼形切换|
|4个idle来源入口|现有soft-light/soft-peak/smile-half/smile-closed都是源40→neutral160。页面使用的是旧源→A，只能作旧资产参照；新B/C和新笑脸未制，**新C→A的幅度/突跳未验证**，不得延长或插B规避|

16条入口首/末/总时长映射随art024-check-report.json保存。未动已认可的大幅上扬；不把只读影响诊断变成修改6张依赖或11张旧帧的授权。

## 实际命令及门槛

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art024-compose.py B 1
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art024-compose.py B 2
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art024-check.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art024-preview.py
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art024-B-v1-candidate-96.png
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art024-B-v2-candidate-96.png
git diff --check
```

实际exit0：CRC/96×104 RGBA8 alpha0/255、A SHA、mask外/固定根部RGBA差分0、正式17文件SHA保持。formatPass=true，B1/B2 visualPass=false；B1孤块检查明确失败，不将脚本正常退出解释成所有门槛通过。原PNG字节内嵌，静态浅深1/2/3×和10×实际查看。新整套循环、C→A和原生视觉均未通过/未执行。

## 交接与停止

只交固定A、B失败证据和旧边界观察；不要集成B尝试，不进入C、笑脸、漂浮或新表情。下一次制作若继续，需先解决生成源无法保持原画布翼部位置/长度这一约束，不能只重置次数盲试，也不能以改变A或放宽非翼保护补救。由PM裁决后续范围；自动跟进仍暂停。
