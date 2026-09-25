# ART-023 · A放松整翼单帧尝试：未通过，按上限停止

**无选定可采用候选。** 两版文件可查看，但均未通过A造型门槛，不进入B/C、不替换正式neutral。imagegen内置工具共2次；合成共2版，共用1张语义mask。第二次只针对第一版实看失败迭代；没有第三次生成、第三版合成或额外过渡。

## 输入和语义标定

以PM52ef940正式neutral为固定底，SHA `5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d`。保存art023-original-neutral/smile-closed/hold-half/release-half.png逐字节副本；正式17文件SHA记录于mask-definition。

已实际查看原neutral及放大图，羽根重新标定在发尾下方深色袖口：左x24..27/y82..85及镜像右x68..71/y82..85，共32个固定样本。它替代ART022仅设计性的约(30,84)/(65,84)，后者不是已验精确骨骼。固定根部样本保持原RGBA，包括其中透明像素。

art023-mask-v1.png白色838样本可编辑，其他全部保护。允许搜索包络内采用逐行阶梯和根部扣除：左从x8至逐行maxX，右x95-x镜像；y78..99逐行maxX为19,20,21,22,23,25,27,28,29,30,30,30,30,30,30,30,29,28,27,26,25,24；再扣除两侧固定根部。完整坐标见art023-mask-definition.json。上界沿发尾下缘，内界止于x30/65，保护袖子/身体x31..64；不是矩形整片覆盖，也没有沿旧x23/24边界把同一羽片中段切开。较高处原透明区域允许翼轮廓搜索，但本轮结果在此形成了不期望的凸起，这是失败点之一。

语义mask SHA `d73ca172573f5f5c43b75a8d2561ab8e79ed5d026b38651de48ba311aa34404a`。原图、mask、源图、donor和合成在预览内可核对。

## 两次生成与转换

|尝试|生成源SHA|96×104尝试文件SHA|RGBA改变/字节|
|---|---|---|---|
|v1|432abc97a9392ec8cdf3afc8e02d8316f84f19f632d001de5744896aa032d059|44a7eb885356174df99f2a4763b11ef671f4cf0132abe4f61a801f7d7a6aab86|389 / 8548|
|v2|82b5d202376f5164f9d8af0552a80f67e81fb6eb0cbaa8e622c8d6ebd2921bf0|e2f90c5dc97a24b9dc7714776d575fafe56791b9dc568e03f152b111badbe6c8|383 / 8392|

文件命名art023-vN-source.png、vN-prompt.txt、vN-donor-96.png、vN-candidate-96.png、vN-report.json；candidate仅表示尝试文件，不代表通过。完整实际prompt保留在txt；v2明确针对高根尖角和竖直内羽，引用原底、失败v1和同一mask。

工具两次均返回1205×1305。转换严格为整画布像素中心最近邻96×104及alpha阈值128；然后只通过显式mask复制生成RGBA到原neutral。未采用历史(0,+5)配准；没有平移、重新居中、独立翼缩放、旋转、扭曲或程序绘像素。生成源非翼部不是原图精确副本，因此只能作为donor，不能直接交付或整图覆盖。

## 实看结果与失败原因

v1外羽方向较原neutral统一，但新羽根向上拱、与固定袖口出现尖角；内侧短羽仍近竖直下垂，外、中、内羽仍有三条手指状分离感。10×检查后才调用第二次生成。

v2缩短了部分羽尖、减少顶部凸出，但未把内羽自然并入同一向外走势。两侧(23,82)/(72,82)仍新增原本透明的实心样本，固定根部外缘形成高凸尖角；10×对照显示原根部与新扇面方向尚不一致。不能仅以孔洞减少或像素相连宣称完整翼造型自然。浅深1×/2×/3×及局部10×均实际查看；两版仍判视觉失败。

两版全图8邻接各为单分量（2953/2911像素），没有新孤立块；这只说明连通，不证明羽序、分叉和运动逻辑通过。开放分叉仍可见，但内羽走势未达到本卡目标。没有制作动作循环，不能宣称协调轻扇已完成。

## 与旧拖动入口/出口对照

art023-inspection.html并列当前neutral、两尝试、原smile-closed、hold-half、release-half，另给各图原PNG浅深1/2/3×及根部10×。

旧四图保留原来较长、下垂的中羽和分组翼形；v1/v2翼面更薄、更向外伸，羽尖长度和底部位置不同。若直接切换，新A到旧hold-half会恢复旧中羽和折点；旧release-half到新A会突然变短、改变外缘走势。smile沿用旧翼也会回跳。即使将来A通过，仍需PM另卡同步依赖/定向检查，本次不触动已认可的大幅上扬，也不宣称已无缝。

## 实际验证命令与结论

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art023-prepare.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art023-compose.py 1
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art023-compose.py 2
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art023-check.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art023-preview.py
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art023-v1-candidate-96.png
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art023-v2-candidate-96.png
git diff --check
```

以上实际退出0。CRC/96×104/RGBA8/alpha0/255通过；两版mask外RGBA差分0、许可包络外0、固定翼根0，头脸身脚保护、anchor(48,94)不变；正式16PNG+manifest的17项SHA保持不变。报告art023-check-report.json明确formatPass=true、visualPass=false。脚本成功不是视觉通过。预览为原PNG字节/CSS展示，非原生应用验收。

## 交接

按生成和合成上限带失败证据停止。请PM决定下一张卡如何约束翼根接合与内羽造型；本卡不继续重试，不自动扩大mask，不改正式包/manifest/代码/时序，不制作B/C/表情/过渡，不进入漂浮。自动跟进仍暂停。
