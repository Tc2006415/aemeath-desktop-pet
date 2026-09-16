# 首批角色素材制作记录

状态：ART-005 neutral 已获 PM/QA 本阶段验收；ART-006 的 idle-soft/idle-smile 已交付可加载候选，但存在头冠1px重绘差异，未满足无抖动视觉门槛，不能作为已验动画。不是完整六动作首包。2026-09-16。

最新产物：ART-006 两动作候选见本文末节；已验 neutral 保持原件。用户已接受 v2 头饰方向，并明确授权最近邻缩放、alpha 阈值及整数像素对齐，本卡另授权 idle-soft/idle-smile。下列 ART-003/004 的“未获授权”“等待确认”是历史状态，已由后续授权取代。全部原图保留。

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

## ART-006：两动作候选及未通过的视觉门槛

本卡在自己的 worktree 将 `codex/runtime-direction` 快进到 `9f7d270`，已读 README、开发流程、任务交接及 ADR0001–0003。PM 传达 neutral 的静态/格式和 QA-005 验收已通过，QA提交90a2210已进入统筹分支。当前任务卡只保存在任务对话；本节是实际制作与验证记录。尝试用 `gh issue view 2 --json title,body,state` 以及历史文档的 CLI 绝对路径读取 Issue 均失败，当前机器没有这些可调用路径；不声称已重新读取远端 Issue。以本卡明确范围和现行契约执行。

**交付性质：供复核的候选，不是动画视觉验收通过。** 已有真实局部动作变化，格式、引用、时长及宿主自动切换通过；冠尖、细线与局部色块仍有重绘差异。未在此授权之外做锁区拼接、手工描线、调色或重采样补帧来掩盖问题。未绘制拖动/状态动作，未修改程序、测试、接口或锁文件。

### 图像来源和帧安排

使用内置 imagegen 共4次，一次一张，输入均为 v3 清理源图（编辑目标）和已验 neutral（位置/轮廓参考）。四个工具原件均保留，源图和每次完整提示词已原样归档 source。闭眼笑仅借鉴已有 ART-001 所记录的游戏闭眼笑姿态，开闭眼连接为原创改编；没有追加视频考据或宣称游戏逐帧复刻。

| 正式格式候选 | source源图/提示词同名前缀 | 工具原始文件名 | 实际姿态 |
| --- | --- | --- | --- |
| `frames/soft-a.png` | `soft-a-generated-v1` | `exec-4f3a318e-2fcf-4433-bf88-ea95aad181e7.png` | 发梢抬起、下方羽饰内收较大，衣襟略变化 |
| `frames/soft-b.png` | `soft-b-generated-v1` | `exec-88447047-293b-44a3-aef5-fcc49cc1e9a8.png` | 发梢抬起、羽尖内收较小 |
| `frames/smile-half.png` | `smile-half-generated-v1` | `exec-906fa4ec-fa50-4ac4-9630-a3744f641405.png` | 半闭眼，仍可见金色眼睛 |
| `frames/smile-closed.png` | `smile-closed-generated-v1` | `exec-091dd6ba-9d0c-4ad9-a23f-fb99bd700539.png` | 闭眼弧线和笑嘴 |

工具原件所在目录统一为 `C:/Users/bigxi/.codex/generated_images/01a0abdf-e294-78d3-a6b8-eb0cef96a2a9/`。保留v1/v2/v3及已验neutral，neutral SHA-256仍为 `5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d`。

manifest 升为0.2.0，仍为 schema1、character、sourceScale1、96×104、anchor(48,94)，共3动作5张实际图片：

| 动作 | 第1–6时序项 | 时长ms | 来源/播放 |
| --- | --- | --- | --- |
| idle-soft | neutral → soft-b → soft-a → soft-a → soft-b → neutral | 400,150,150,400,150,150；总1400 | original / loop |
| idle-smile | neutral → smile-half → smile-closed → smile-half → neutral → neutral | 120,120,500,120,120,220；总1200 | adaptation / once |

呼吸按生成后的实际幅度排序，B是中间态、A是最大内收；A连续两个时序项合计550ms为顶点停留，首尾neutral形成550ms休止。笑脸闭眼保持500ms，末两项neutral合计340ms为收势。每动作3张不同姿态；复用是往返/停留，不是六张重复图充数。没有程序整图平移形成动作。

### 转换、逐帧检查与已知问题

[export-idle.py](../../assets/characters/aemeath-v1/source/export-idle.py)无新增依赖，复用既有PNG读写函数。每张源图都是1205×1306，固定全画布像素中心最近邻到96×104、阈值128、偏移(0,+5)，与neutral同参数；不按各帧包围盒缩放/居中。所有源图SHA、正式帧SHA及参数见 [idle-export-report.json](../../assets/characters/aemeath-v1/source/idle-export-report.json)。

| 帧 | Bytes | 不透明像素 | 可见包围框（含端点） | 脚部末行 | 上半头部alpha差异数* |
| --- | --- | --- | --- | --- | --- |
| soft-a | 8566 | 2982 | (14,21)–(81,95) | 93 | 29 |
| soft-b | 8728 | 3028 | (11,21)–(84,96) | 93 | 18 |
| smile-half | 8945 | 3141 | (9,21)–(86,97) | 93 | 26 |
| smile-closed | 8843 | 3148 | (9,21)–(86,97) | 93 | 26 |

*相对neutral，统计y=22…55的alpha变化；不含新帧y=21冠尖新增像素。RGBA逐字节不同像素数量很大，包含生成重编码/细小色值差异，不把它等同于有意义动作幅度。

已使用 view_image 实看四张生成原图和四张4×最近邻导出图，并对照前卡neutral 1×/4×。眼睛、脸和紧凑头身比仍可识别，细冠留空、小侧羽饰保留；所有帧脚部中央x=38…57末行y=93，画布留白完整，阈值后不透明采样裁切数0。正式PNG均RGBA8、alpha只有0/255，CRC重新解码通过，均远小于256KiB。

**未通过/待复核项：**

- 新帧冠尖最上方为y=21，neutral是y=22；固定整数偏移不能单独修复冠尖而不移动脚。上半头冠/发饰边缘存在18–29个alpha变化，1×/4×可对比，循环存在闪动风险，不能宣称无抖动或逐像素锁定。
- soft-a的羽饰左右极值比neutral各收进5px，soft-b各收进2px；大于提示词所期望的1–2px，发梢也有形变。实际更像小幅收羽/发梢起伏，不能宣称精确的纯胸腔呼吸。A/B/neutral往返的平滑感需用户评审。
- 笑脸表情明确，但非眼部也有重绘色值和细线差异。没有足够证据把4张候选标记为外观一致性通过。

### 可复核预览与实际验证

[独立检查页 idle-inspection.html](../../assets/characters/aemeath-v1/source/idle-inspection.html)内嵌真实PNG，离线即可打开；含浅/深底3×、源帧1×、六项逐帧按钮、逐毫秒拖条、循环/单次及15秒待机→笑脸→待机预览。4张 `source/*-preview-4x.png` 是最近邻静态检查图，不是额外动画帧。检查页由 [make-idle-preview.py](../../assets/characters/aemeath-v1/source/make-idle-preview.py)生成，只作审查，不改变宿主。

实际命令与结果：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/export-idle.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/make-idle-preview.py
& ./scripts/build.ps1 -Publish
foreach ($name in @('soft-a','soft-b','smile-half','smile-closed')) {
  & ./scripts/qa/Inspect-Png.ps1 -Path "assets/characters/aemeath-v1/frames/$name.png"
}
```

上述命令均exit0。构建0警告0错误；没有重跑无关全套测试。预览生成检查引用均存在、两动作各6项/3个不同图、时长数组与1400/1200ms精确匹配，固定锚点正确；独立既有 Inspect-Png.ps1复核四帧格式、二值alpha及字节数通过。

复用生产宿主/加载器以及现有 smoke-character-host 的断言，使用实际角色目录参数（未修改现有验证脚本）：

```powershell
$artExe = Join-Path $PWD 'artifacts/host-win-x64/Aemeath.Host.exe'
$artPackage = Join-Path $PWD 'assets/characters/aemeath-v1'
$artLog = Join-Path $PWD 'assets/characters/aemeath-v1/source/idle-host-automatic.jsonl'
$artProbe = Start-Process -FilePath $artExe -ArgumentList @('--package', ('"' + $artPackage + '"'), '--diagnostics', ('"' + $artLog + '"'), '--mode', 'automatic', '--scale', '2', '--exit-after-ms', '18000') -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
$artProbe.WaitForExit(30000)
```

实际PID52448，exit0；日志 [idle-host-automatic.jsonl](../../assets/characters/aemeath-v1/source/idle-host-automatic.jsonl)有package-loaded/render-callback/shutdown，无package-rejected/position-error；从首个idle-soft到首个idle-smile精确15000ms，笑脸索引0…5均出现，仅1次natural-end，此后返回idle-soft。宿主exe SHA256为 `E3951560B446CB708F97A928BA96940FD4B4B3182DC9FAA1C754C2ACF27113B0`，代码基线9f7d270。另一次60秒3×运行PID41528用于窗口检查，记录在 [idle-host-validation.jsonl](../../assets/characters/aemeath-v1/source/idle-host-validation.jsonl)，正常定时退出。

使用computer-use技能/sky实际查看原生控制窗：0.2.0角色包已加载、自动idle-soft、DPI144、3×；显示可播放neutral/idle-soft/idle-smile，缺失三个拖动动作。透明宠物窗口未出现在可选窗口列表，未通过猜测句柄绕过。该截图只证明控制窗状态，不能作为宠物连续视觉验收。浏览器检查页已在本地打开且观察到时间项前进；独立Chrome界面检查被Computer Use终止，原因是无法足够可靠确定当前浏览器URL以执行策略。此后停止所有界面输入，没有绕过。连续播放的视觉平顺性、浅深底动态表现、原生宠物的15秒笑脸切换视觉均保留待验，日志不代替它们。

### 交接

PM可从上述HTML直接逐帧比较，重点看冠尖y21/22和发冠边线。当前manifest是便于加载的0.2.0候选，未获准替换默认皮肤；neutral原件完整保留。若要求像素完全锁定的静止区域，下一步需PM决定重新生成策略或另行授权锁区合成，不能在本卡仅允许的格式转换外自行修补。交付本次候选和具体失败证据后等待下一卡，不继续扩展动作。
