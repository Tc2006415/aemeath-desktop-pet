# QA-010 · ART021 翅尾局部修复验收

2026-09-22。结论：**可以由 PM 选择性推广指定的两张 m2 图，随后请用户原生复验普通 idle-soft。** 本轮文件、来源、保护区及生产加载器检查通过；浏览器浅深底 1×/2×/3×原速多轮抽样未见阻断性的断开重接。不能宣称已解决用户原生反馈的全部主观现象，也不能把补齐五点或连通分量数量当成视觉通过的理由。

## 固定对象

ART 提交 `81836e3d7f3bb4405ca70632649aae30e9fd3aea`，来源目录为 `C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source`。

| 仅允许选取的文件 | SHA256 |
| --- | --- |
| art021-soft-light-v1-m2-96.png | bc9fe556ac774ad2ca7c77d03446cdc451159819712e7e4fc9b8b245b48dcd70 |
| art021-soft-peak-v1-m2-96.png | 79d227136f70d87ccea3d7efa2ae94759f8868890c3ef87a984c2d8fcf045be2 |

不含 m2 的 v1-96、unaligned、mask-v1 均未作为候选。基线读取 PM worktree `C:/Users/bigxi/Documents/ChatGPT/桌宠`（检查时 HEAD `7284766`）的正式 0.4 包。manifest raw SHA256 为 `eab91ecb10037da7320d4e9c9321c8dce0f122d3b9d5daa6e101a55e1e319da3`。阅读 ART020 诊断、ART021 交付与生成合成脚本，并按现行 ADR004 的时序冻结范围审查。

## 独立差分与来源

QA 脚本使用自有只读 PNG 解码器校验 CRC、96×104、RGBA8、alpha0/255；不调用 ART 的检查脚本得出结论，不生成或修绘图像。

- 原图与 PM 正式 soft-light/soft-peak 逐字节一致。
- light/peak 分别改变 33/30 个 RGBA 像素，恰好落在各自 mask-v2 的 33/30 点内。允许窗口为左 x18..26、右 x69..77、y89..97；窗口外和 mask 外 RGBA 差分均为 0。其余部位、羽尖、头脸身脚不变。
- light 仅将 `(20,92)、(20,93)、(75,92)、(75,93)` 从透明变实心；peak 仅增加 `(76,90)`。原实心清除数均为 0。窗口内其余原透明点分别 41/33 个保持原 RGBA，全图其余原透明点也未改变，因此没有新增透明孔、裂线或误填其他分叉负空间。
- 独立在内存按保存生成源的像素中心最近邻、alpha128、整图 `(0,+5)` 重建 donor，逐像素完全一致且无实心采样裁切；再验证候选在 mask 内逐点等于 donor，外部逐点等于原图。来源链成立，不是直接手画五点的假证据。
- ART 预览内嵌的五张 PNG（neutral、两张旧图、两张 m2）逐字节等于对应文件。HTML raw SHA256：`1db49f26fca7b30e0e7ae6623a671572b5a670be126650cbb24fa79d6d5bcaf8`。
- 预览序列与正式 manifest 完全一致：neutral400→light150→peak150→peak400→light150→neutral150，总计 1400 ms。没有改 idle、release-entry 或其他动作时序。

## 实际浏览器视觉观察

将未经改写的 `art021-inspection.html` 复制到 QA artifacts，经本机回环地址打开。实际使用 CUA 浏览器截图检查，六种背景/尺度同时在可见区域；1×为原尺寸，2×/3×为整数最近邻。没有用程序合成联系表代替播放，也没有将网页称为原生桌宠。

页面保持原速运行；早期可见截图为 3842 ms/周期2/peak，91108–91210 ms/周期65/neutral。随后连续采集姿态变化的截图，截图上时刻如下（没有暂停或变速）：

| 周期 | 可见截图时刻 ms 与姿态 |
| --- | --- |
| 85 | 119224 neutral；119455 light；119612 peak；120151 light；120309 neutral |
| 86 | 120848 light；120994 peak；121551 light；121703 neutral |
| 87 | 122236 light |

这组采样实际覆盖多轮往返，并检查了每轮短暂 light 的进入和返回；不是只让页面计时后截一张图。之后使用页面控件暂停在 0/400/550 ms 对照 neutral/light/peak，并滚动查看旧→修左右局部 10×辅助图。上述截图保存在本 QA 对话的工具证据中；本次没有录制逐帧视频，时间文本读取与随后截图存在约几十毫秒差值，以截图标签为准。

观察结论：

- 浅底 2×/3×可见连接带保持实心；已知 light 竖缺口和 peak 单点没有再透背景闪现。深底中深色轮廓本来对比弱，仍可见白色羽片端部的连贯形状，没有看到新裂线或羽片突然孤立。
- 1×整体翅尾仍有预期的动作闪变；2×/3×能分辨 light 比 peak 更横向的短羽形状变化。没有把这种现存帧间位移/形状变化计为新缺口。
- 10×能看到 light 修补带有接近黑色的深色像素，以及连接处亮暗纹理差异；这些点经 RGBA 核对为不透明，不能误称透明孔。周边白色羽缘与分叉仍在，未见新增贯穿接缝的亮线。
- **限制：**3×下 neutral↔light↔peak 的白色羽尖与暗色连接带仍有逐帧跳动，不是平滑连续变形；本轮没有观察到足以阻止局部推广的明显断开重接，但不能保证用户原生桌面上的主观拼接感全部消失。此次修复范围没有授权重新制作整套 idle。

## 单次生产读包检查

QA 临时目录只复制当前 PM 正式 manifest 与 16 张帧图，替换两张指定候选；逐文件哈希差异集合严格为 `soft-light.png, soft-peak.png`，manifest 不变。引用 QA009 已验固定 `74d8442` 的生产 PackageLoader/PngDecoder；与当前 PM `7284766` 比较这两份源文件差分为空。

实际执行：

```powershell
& 'C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe' -B scripts/qa/check_art021.py 'C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source' 'C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1' artifacts/qa010/pixel-check.json
./scripts/qa/Test-Art021Load.ps1
git diff 74d8442 7284766 -- src/Aemeath.Presentation/PackageLoader.cs src/Aemeath.Host/PngDecoder.cs
git diff --check
```

全部 exit0；读包结果 schema2 / version0.4.0 / 16 images / 6 actions / 0 disabled / idle1400ms / 16 entries，manifest SHA 与基线一致。未重跑 39 测试、拖动或完整原生行为。检查后 PM 正式包 17 个文件哈希全部未变。

本地证据：`artifacts/qa010/pixel-check.json`、`loader-result.txt`、固定预览副本和临时 `package`。artifacts 不提交。独立检查脚本与本文在 QA 分支提交，沿用 Draft PR #6：https://github.com/Tc2006415/aemeath-desktop-pet/pull/6。

## 交接边界

建议 PM 只复制表中两张 m2 到正式对应文件名，保留 manifest、入口、代码与其他图片；不要合并 ART/QA 整分支的历史 0.2 素材。本次没有自行推广或发布。

当前工具禁止原生应用控制，故没有模拟输入或绕过限制。用户需在 PM 集成版本中复看普通 idle-soft 翅尾，确认原生背景与倍率下的断续感是否已解除；“其他正常”仍只是用户此前报告。若仍明显断裂，应回传具体帧/位置，由 PM 另派定向任务。本卡交付后停止，不进入漂浮、新待机或新阶段；不操作暂停中的定时任务。
