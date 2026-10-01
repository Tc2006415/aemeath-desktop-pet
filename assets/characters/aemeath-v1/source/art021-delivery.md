# ART-021 · idle-soft 翅尾局部修复候选

仅供独立QA、PM决定采用。正式0.4包、manifest、动作时序和程序均未修改。

## 选定文件

|帧|文件|SHA256|RGBA改变|
|---|---|---|---|
|light|art021-soft-light-v1-m2-96.png|bc9fe556ac774ad2ca7c77d03446cdc451159819712e7e4fc9b8b245b48dcd70|33像素|
|peak|art021-soft-peak-v1-m2-96.png|79d227136f70d87ccea3d7efa2ae94759f8868890c3ef87a984c2d8fcf045be2|30像素|

两图均96×104、RGBA8、alpha0/255。light仅增加(20,92)/(20,93)/(75,92)/(75,93)四个实心像素；peak仅增加(76,90)。没有原实心像素变透明，所有其他透明像素不变。左右许可窗口x18..26及69..77、y89..97外RGBA差分0。全图8邻接始终一个分量，新增点均接触原实心像素，没有新增独立块；没有新透明孔或透明细线。包围框不变，头冠/脚和锚点(48,94)保持基线。

## 生成和遮罩

每帧imagegen调用1次、遮罩2版，未达到每帧2次生成上限。生成源1205×1305，保留原PNG、完整prompt、原始生成图、donor、两版显式遮罩及报告。先直接缩小的light落位错误，保留unaligned证据；选用历史整图配准：像素中心最近邻96×104、alpha128二值化、整图(0,+5)，无剪掉实心样本，无独立羽翼变形。最终仅从donor经mask-v2复制RGBA；程序不绘制补丁。

mask-v1带入了羽尖缩短，light清除20、peak清除45原实心像素，已淘汰。mask-v2只覆盖连接带与亮暗接缝，冻结羽尖。未另创第三版。带v1-96（不含m2）的图、unaligned图均不是交付候选；不要误用。

art021-report.json记录逐点mask、差分、生成/原图/候选/遮罩SHA；art021-evidence-sha.json补充所有证据文件SHA。mask1-report和unaligned-report是当时失败检查原样保留，其preservedNormalGapPixels旧字段实际为窗口减遮罩的数量，不可解释为纯透明空隙计数；最终报告已更正字段名。

## 实际视觉检查

art021-inspection.html内嵌5张原始PNG字节，原neutral→修light→修peak按正式6项1400ms运行，浅/深底同时1×/2×/3×；下方原→修左右局部10×对照。

已在浏览器实际检查暂停0/400/550ms三帧、六种背景/尺度及10×左右局部；运行截图28445ms为light、28729ms为peak（周期20）。已知五点不再透背景闪现，正常羽尖分叉负空间仍在，未见新增透明细线、孤立块或贯穿遮罩边缘的亮线。局部10×能看出生成暗色连接点，连接带亮暗纹理仍有差别，不能声称完全消除所有主观重接感；独立QA应重点复核。这是网页抽样视觉检查，不是逐帧视频或原生桌宠验收。

## 实际验证

以下实际执行退出0：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art021-build.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art021-check.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art021-preview.py
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art021-soft-light-v1-m2-96.png
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art021-soft-peak-v1-m2-96.png
git diff --check
```

检查报告：art021-check-report.json、art021-png-inspect.json、art021-preview-report.json。正式16PNG及manifest共17文件SHA保持不变；manifest仍eab91ecb10037da7320d4e9c9321c8dce0f122d3b9d5daa6e101a55e1e319da3。

## 交接

由PM交独立QA；若通过，只取上述两张m2候选按正式命名集成。不得整包合并本ART分支历史0.2正式资产。其他动作、entry、时序、schema、代码和依赖均不在本次范围。完成这一轮后停止，自动跟进保持暂停，不进入float。
