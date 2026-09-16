# 首批角色素材制作记录

状态：ART-005 已导出并由现有宿主实际加载 neutral 单帧包，待 PM/QA 外观与交互验收；不是完整六动作首包。2026-09-16。

最新产物：ART-005 neutral 正式格式帧见本文末节。用户已接受 v2 头饰方向，并明确授权最近邻缩放、alpha 阈值及整数像素对齐。下列 ART-003/004 的“未获授权”“等待确认”是历史状态，已由本次授权取代；没有动画扩展授权。全部原图保留。

## 基线、范围和产物

已执行 `git fetch origin` 并在原 `codex/animation-spec` 分支合并 PM 基准 `77fa5c0e056e45d8e5c9872195ce86ea91b9e9fd`，结果为 fast-forward；已读 AGENTS、README、ADR0003 和现行素材契约。本轮仅制作中性基准，不扩展动作、不改加载器或契约。

- 生成原图：[neutral-generated-v1.png](../../assets/characters/aemeath-v1/source/neutral-generated-v1.png)。单角色、睁眼正向、小幅中性微笑；这是待评审的角色基准原图，不是96×104成品帧。
- 完整实际提示词：[neutral-generated-v1.prompt.txt](../../assets/characters/aemeath-v1/source/neutral-generated-v1.prompt.txt)。提示词明确要求96×104、真正透明、8-bit RGBA及二值alpha，但生成结果未满足全部技术约束。
- 没有创建manifest或frames目录，避免误把不合规原图交给加载器。没有用重复帧凑齐动作，六动作均未宣称交付完成。

## 生成来源与视觉检查

使用 `imagegen` 技能及内置 `image_gen.imagegen`，无需API key；没有调用CLI/API回退。生成前使用 `view_image` 查看已选 `assets/concepts/aemeath-game-style-v2.png`；该图作为造型参考，要求以左侧睁眼姿态生成单独中性角色、删除灰背景，保留粉色紧凑发型、蓝色尖顶头饰、深浅服饰和两侧低位羽饰。

工具原始输出：`C:/Users/bigxi/.codex/generated_images/01a0abdf-e294-78d3-a6b8-eb0cef96a2a9/exec-1ac90a62-5b82-44e2-8b6c-12924fcbfc1c.png`。以 `Copy-Item -LiteralPath` 原样复制到项目source目录，保留工具原件；没有缩放、裁剪、去背景、阈值化、调色或程序绘图。模型具体版本不由本次工具参数选择，不编造生成种子。

已通过 `view_image` 实际查看保存后的原图，并在任务中inline展示：单角色正面、睁开的金色眼睛、粉发、蓝冠、紧凑小身体及低位羽饰均可辨认；没有回到第一版高挑长发造型。画面呈块状像素风，但边缘/色块是否适合96×104仍未验证；透明通道检查也不等于最终外观认可。用户尚未确认该新基准外观，不扩展idle或拖动姿态。

## 实际格式检查

首次只读检查命令 `from PIL import Image` 失败：本机Python没有Pillow。本轮未安装依赖；随后通过Python标准库 `struct/zlib` 读取PNG块、核对CRC、解压IDAT并逆PNG行过滤，统计原始alpha通道。该检查仅解码读取，没有写回或改变图片。

| 项目 | 实际结果 | 契约判断 |
| --- | --- | --- |
| 尺寸 | 1205×1305 | 不符合96×104 |
| PNG位深/色彩类型 | 8 / 6（RGBA） | 符合8-bit RGBA |
| PNG静态性/CRC | 未见acTL；所有块CRC通过 | 静态PNG，读取完整 |
| 文件大小 | 778921 bytes | 超过单PNG 256 KiB上限；仅作为source保存 |
| alpha=0像素数 | 987626 | 确实包含透明背景像素，不是只有灰底的RGB图 |
| alpha=255像素数 | 1628 | 存在完全不透明像素 |
| alpha=1…254像素数 | 583271 | 不符合二值alpha；共256种alpha值 |
| 任意非零alpha边界（含端点） | (0,53)–(1188,1304) | 存在接近画布边缘的非零alpha，不可直接把此边界当成角色裁剪框 |
| SHA-256 | `251add4c2c0384f2d0ed58a3f4ca2cfc6c67b7dfd2cf6cb1c65f3dd276dea815` | 用于原图一致性核对 |

图片没有独立锚点元数据；尚未创建manifest，不声称脚部已对齐(48,94)。本轮未运行宿主、加载器或播放测试：已知尺寸/alpha/字节数不合规，不能把“PNG可解析”称为“可用包”。提交前另执行 `git diff --cached --check`、基线后允许路径检查和原件/项目副本SHA-256一致性核对，实际结果随交接回报。

## 所需最小转换与下一步门槛

内置生成没有产出精确小画布或二值alpha。建议在用户认可外观后，由PM明确授权一次确定性导出：将该原图以最近邻方式映射到96×104画布，把alpha按明确阈值二值化（建议128作为起点），只做整数像素位置对齐以满足固定锚点(48,94)和脚部基线；导出8-bit RGBA PNG并检查大小、留白和羽饰/头饰完整性。不可据任意非零alpha包围盒直接自动裁剪，不改变角色造型，不用程序画新姿态。映射及阈值可能丢失细节或留下杂边，需对转换结果再次视觉检查，必要时回imagegen编辑；本轮没有执行任何这些步骤。

这是唯一请求的范围补充：允许针对已生成原图做尺寸、alpha及整数对齐转换，输出仍在 `assets/characters/aemeath-v1/`，不改加载器或契约。若不授权，可继续用内置imagegen尝试技术修正，但不能保证精确尺寸/alpha，也不把重复生成视为已解决问题。

在外观确认及导出方式获准前，停在这张基准图。PM可先展示本文件链接的原图给用户；下一步才是合规neutral导出、视觉检查，以及按后续授权扩展六动作。真实播放与首角色包验收另行进行。

## ART-004-H：v2头饰外观候选

状态：文件归档及视觉检查待PM验收；**外观等待用户确认，尚未满足正式像素帧规范**。2026-09-16。本轮不重新生成、不做缩放或alpha转换、不进入动画扩展。

来源：PM提供集成工作区 `C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1/source/` 下的两个新文件。随附提示词记录为PM使用内置imagegen编辑v1，并以指定游戏视频正面截图作为参考，响应用户“头饰更贴近游戏原版正面”的要求。本任务没有再次调用imagegen或重新考据视频，没有把PM生成操作称作本任务生成。

- [v2原图：neutral-generated-v2-headpiece.png](../../assets/characters/aemeath-v1/source/neutral-generated-v2-headpiece.png)
- [PM原始提示词及来源记录](../../assets/characters/aemeath-v1/source/neutral-generated-v2-headpiece.prompt.txt)

使用 `view_image` 实际检查该候选：头冠改为较细的蓝白尖拱，冠弧与粉发上沿之间可见留空；画面右侧头部蓝白羽饰明显缩小并贴近鬓侧。下方两侧羽状装饰仍保留，不能把“侧羽饰缩小”误记成下方羽翼被要求缩小。粉发、金色睁眼、小身体和正面中性姿态仍可辨认。冠尖、冠弧外沿及头部周围存在蓝色/青色零散边缘噪点，不能称为干净的最终像素轮廓；其余部位也未做逐像素一致性证明，不能因提示词要求保留就声称与v1完全相同。是否足够贴近游戏正面由用户评审，不在本任务中代为通过。

实际检查与结果：

| 检查 | 结果 |
| --- | --- |
| PM给定PNG SHA-256与源文件核对 | 一致：`6E78FAA19B4ED324B34938E85F18CECFEB48C02C6814E4ABFD1C2D91ED6CE26E` |
| `Copy-Item -LiteralPath` 后两文件逐一 `Get-FileHash -Algorithm SHA256` | 项目副本与PM源文件逐字节一致；未覆盖v1 |
| 提示词副本SHA-256 | `239DAD952B6A84B3BB28BE2AF980D43426A06FCC28D2B142DBD3F5F855D5E0DA` |
| Python标准库读取PNG签名与IHDR | 1205×1306，8-bit，色彩类型6（RGBA）；仅只读检查 |
| 文件大小 | 716536 bytes，超过单正式帧256 KiB限制；只存source |
| 96×104及固定锚点 | 尺寸不符；未生成manifest或做锚点对齐，不能宣称通过 |
| alpha、像素成品和实机播放 | 本轮未统计完整alpha分布或验证二值alpha，未做像素清理、正式帧或运行验收；边缘噪点已视觉确认 |

本轮只新增上述PNG、提示词并补充本记录，提交前检查 `git diff --cached --check` 与暂存路径。没有改代码、接口、manifest或其他图帧。到此停止，等待外观反馈；之前提出的确定性转换建议仍未因本轮复制归档而获得授权。

## ART-005：一次边缘清理及 neutral 单帧包

用户通过 PM 明确授权格式转换；范围为本角色目录和制作记录，转换脚本只能位于 source，无新增依赖。本轮仅使用内置 imagegen 对 v2 做一次局部清理，没有扩大动作或修改代码、接口及契约。

### 来源、固定参数和产物

- 原始生成副本：[v3清理源图](../../assets/characters/aemeath-v1/source/neutral-generated-v3-edge-cleanup.png)，[完整提示词](../../assets/characters/aemeath-v1/source/neutral-generated-v3-edge-cleanup.prompt.txt)。工具原件为 `C:/Users/bigxi/.codex/generated_images/01a0abdf-e294-78d3-a6b8-eb0cef96a2a9/exec-3e65628b-c292-45b2-ba1d-37bf93f035db.png`，复制归档不覆盖 v1/v2。
- 视觉检查 v3 后保留其作为转换基线：未观察到已认可的头冠留空、紧凑侧羽饰、面部、粉发与身体轮廓被破坏；清理并未消除所有冠尖/细线边缘噪点，不声称逐像素不变或完全干净。
- [转换脚本](../../assets/characters/aemeath-v1/source/export-neutral.py)仅用 Python 标准库。完整 1205×1306 画布映射至 96×104，使用像素中心最近邻：`sx=floor((2*x+1)*1205/(2*96))`，y 同理；无裁剪、无包围盒归一化。alpha <128 设透明且 RGB 清零，其余保留采样 RGB 并设 alpha=255。最后固定整数偏移 `(0,+5)`，不做手工补像素、描边或颜色量化。
- [正式帧](../../assets/characters/aemeath-v1/frames/neutral.png)、[最小 manifest](../../assets/characters/aemeath-v1/manifest.json)、[4×最近邻检查图](../../assets/characters/aemeath-v1/source/neutral-preview-4x.png)、[可重现导出报告](../../assets/characters/aemeath-v1/source/neutral-export-report.json)。预览不是动作帧。
- manifest 为 `aemeath-v1 / 0.1.0 / character`，固定锚点 `(48,94)`；仅 original neutral 一帧、loop、1000 ms。未用重复帧补造其他动作。

### 实际检查与结果

| 检查 | 结果 |
| --- | --- |
| 源图 SHA-256 | `45b754f137d68f7d7acd38c25719e853af75bd4f4d11ca1cbd33cfca91a35948` |
| 正式 PNG | 静态 RGBA8，96×104，8860 bytes，小于256 KiB；重新解码且所有块 CRC 通过 |
| alpha | 仅0/255；3108个不透明像素 |
| 可见范围（含端点） | `(9,22)–(86,97)`；平移裁掉的不透明采样数为0，头冠、侧羽饰及下方羽饰未触画布边 |
| 脚部基线 | 中央脚部 x=38…57 范围末行在 y=93，y=94/95 无不透明像素；锚点保持契约常量 |
| 正式帧 SHA-256 | `5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d` |
| 静态视觉 | 用 view_image 实际查看正式1×帧及4×最近邻图；细冠尖拱、冠与粉发留空、金色眼睛、小侧羽饰和下方羽尖仍可辨认，无观察到裁边。冠尖仍有不规则像素；1×细节明显少于高分辨率原图，最终外观由用户/PM/QA判断 |
| 现有验证脚本 | `./scripts/validate.ps1 -Publish`，exit 0；Release构建0警告0错误，现有测试20通过、0失败、0跳过 |
| 真实包加载 | 复用现有宿主 CLI，下述命令参数启动自有进程 PID18276，exit 0；日志具备 control-rendered、package-loaded、pet-loaded、render-callback、layout、shutdown，无 package-rejected/position-error |

重现导出命令：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe assets/characters/aemeath-v1/source/export-neutral.py
```

现有 `smoke-host.ps1` 没有 package 参数，因此没有改写它；以它的证据断言复用现有宿主参数直接加载角色目录。实际调用（在工作区根目录解析绝对路径）：

```powershell
$artExe = Join-Path $PWD 'artifacts/host-win-x64/Aemeath.Host.exe'
$artPackage = Join-Path $PWD 'assets/characters/aemeath-v1'
$artLog = Join-Path $PWD 'artifacts/art005-neutral-load.jsonl'
$artProbe = Start-Process -FilePath $artExe -ArgumentList @('--package', ('"' + $artPackage + '"'), '--diagnostics', ('"' + $artLog + '"'), '--clip', 'neutral', '--scale', '2', '--exit-after-ms', '3500') -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
$artProbe.WaitForExit(15000)
```

[本次完整自有进程日志](../../assets/characters/aemeath-v1/source/neutral-host-validation.jsonl)记录加载 `aemeath-v1`，Kind=character，disabled=[]；这是没有失效的已声明动作，不表示六动作齐全。另五动作 idle-soft、idle-smile、drag-pickup、drag-hold、drag-release 未声明，尚未交付。实测日志 dpi=144、scale=2、192×208 px，clientOffsetX/Y均为0；日志不能代替原生UI视觉验收。本轮没有桌面截图、拖动/中断、浅深背景或跨屏DPI验收，没有真实Codex状态联动或发布。

交接：PM/QA以本次 neutral 包做下一步外观和实机验收，通过后再派多动作。本分支仅提交角色资源及此记录，复用 Draft PR #5；未合并PR、关闭Issue或新增任务。
