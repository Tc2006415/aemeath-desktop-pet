# 首批角色素材制作记录

状态：ART-008 v2单帧合成方式已获PM验收；2026-09-21 ART-009完成source内两动作候选子包，格式/局部合成/浏览器检查及定向宿主加载自检通过，待PM/QA。峰值局部距离3px限制保留；正式目录未替换，不是完整六动作首包。

最新产物：ART-009独立候选子包、眼口/羽饰mask及检查预览见本文末节；已验neutral和现有正式目录保持原件。ART-007时尚未授权拼贴，ART-008/009已明确授权限定区域合成，历史限制不应误读为本轮仍禁止合成。全部原图和旧候选保留。

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

### ART-006 PM审查补充与最小返修提案（尚未执行）

PM复核对象为提交 `6edab8fcf2d6cb8f38a236307e8884e8a7dd192c`、四帧既有 Inspect-Png 结果和宿主日志。结论：**格式/时序候选通过，视觉未通过；不合并为已验动画，不进入拖动动作。** 退回三项与本任务既有逐帧数据一致：冠尖y21/22跳变；非表情区域冠线/发饰重绘；soft-a左右羽饰各内收5px，超过轻待机1–2px目标。

以下为 **PM提供的检查证据**，不是本动画任务新做的浏览器或原生窗口检查：用户已授权继续浏览器检查，PM通过CUA在明确地址 `http://127.0.0.1:8847/source/idle-inspection.html` 恢复预览，查看浅深底3×与1×、待机逐帧以及半闭眼/闭眼笑。PM报告只读DOM抽样为15555ms闭眼、15864ms收势、16318ms返回idle-soft。该证据补充确认预览可用和抽样切换，不能推导为连续无闪动、原生宠物连续视觉通过或最终外观认可。前节Computer Use终止是当时本任务的历史事实；本轮没有重新操作界面。临时本地URL不是永久交付地址，离线HTML仍是可复核产物。

**返修边界：**仅提案，等待PM另发修订制作卡后才执行。继续用内置imagegen局部编辑；程序只做既有授权的最近邻缩放、alpha阈值与整数对齐。前节曾提及的锁区合成不属于本次方案，也没有获得授权：不使用程序锁区拼贴、复制neutral像素覆盖候选、手工补线、颜色替换或整图平移来消除差异。正式neutral、四张现有候选和manifest本轮均不变。

| 退回问题 | 建议的最小编辑 | 重新导出后的通过条件 |
| --- | --- | --- |
| 冠尖y21/22跳变 | 以已验neutral为位置/轮廓基准，要求imagegen恢复冠尖及细冠线到neutral的形状与位置；不能用整体下移1px修冠尖 | 冠尖最上可见像素回到y22，脚部仍在y93、锚点仍为(48,94)，头冠留空不闭合；与neutral交替检查无冠尖跳变 |
| 非表情区域重绘 | 笑脸只编辑眼睑/眼内与嘴；呼吸只编辑下部发梢、羽尖及必要衣襟。提示词逐一列出必须保持的冠线、小侧羽饰、头部外轮廓、静止色块，v3作直接编辑源、已验neutral作最终像素位置/轮廓参考，避免继续累积候选的重绘偏差 | 只读差分单独检查静止头冠/侧羽饰区域；其alpha轮廓不得改变，RGB差异单独列出并实看，不因整体差分均值小而放行。表情和动作区域外若出现可见色闪/线跳即退回 |
| soft-a内收5px过大 | 先做一张较小幅的呼吸修订：羽尖只朝内/上约1个最终像素，最大不超过2px，保持羽片形状，不卷成钩；发梢同样限小幅。以原neutral的羽尖为位移参照，不把已内收的A当中性 | 相对neutral左右极值内收各不超过2px（neutral边界x9…86，候选左右极值分别不越过x11/x84），再逐一看羽尖/发梢而非仅凭包围框；与另一呼吸姿态形成真实、幅度递进的往返 |

建议按下列顺序控制返修量，而非同时重新生成四张：

1. **单帧试修。** 先从v3源图局部编辑出一张小幅呼吸候选，以已验neutral核对最终像素位置，用它同时验证冠尖保持、静止区域保持、羽饰幅度三个风险。源图和完整提示词新建版本保存，不覆盖现有文件；派生检查图先留在source。若imagegen不能稳定保持静止区域，不承诺后面三张能够自动一致。
2. **先检查再扩展。** 要求保留v3的1205×1306源画布和取景，复用全画布像素中心最近邻96×104、阈值128、偏移(0,+5)；记录实际源尺寸和哈希。已对齐的96×104 neutral仅作参照，不再次对它施加+5偏移。如果新输出改变了画布比例/取景，使此映射失配，应退回候选，不通过逐帧改缩放/偏移掩盖漂移。检查CRC、RGBA8、二值alpha、256KiB上限、无裁边、脚部y93，以及上表三项。首张失败时只建议针对一个明确残留问题再做一次局部修订；仍失败则提交差分/图例回PM，不继续批量生成。
3. **通过试修后再制作剩余姿态。** 第二张呼吸在已通过的小幅姿态范围内做另一真实局部变化；半闭眼、闭眼笑分别从v3做眼口局部编辑，以已验neutral核对最终像素位置，避免串行重绘扩散。每张先单独通过静止区域与脚基线检查。四张未全部通过前不替换正式帧或manifest；时序仍保持原卡的6项和1400/1200ms。
4. **再做动态验收。** 在明确本地地址的检查页逐帧比较，并在浅深背景1×/3×看至少两个呼吸循环、一次完整笑脸、首尾接续和15秒切换；记录具体观察，而不是只取DOM状态。复用已有生产加载器/宿主验证引用与切换；原生宠物连续视觉若仍不能捕获则单列未验，由PM/QA安排，不用日志替代。无需重复无关全套测试。

本轮实际仅补充本Markdown记录，未调用imagegen、未改变任何图片/manifest/预览或验证脚本。提交前以 `git diff --check`、暂存路径和资产目录差分检查确认范围；本提案不代表返修已完成或制作已获准开始。等待PM评审方案并发修订制作卡。

## ART-007：单帧试修两次，未通过（2026-09-21）

用户经PM明确恢复执行已通过的5863c9d方案，本卡只允许source新增候选/检查材料和本记录。沿用原worktree及分支，未重写提交。开工时工作区干净；重新读取README、开发流程、任务交接、ADR0003及现行方案。`Get-Command gh -ErrorAction SilentlyContinue`未找到CLI，本轮未能重新读取远端历史Issue #2；当前派单依据为对话中的ART-007，不以历史Issue替代新范围。

**结论：两次imagegen额度已用完，两个候选均失败；不替换正式frames或manifest，不进入其他姿态或拖动。** 第二张仅解决冠尖高度，未解决固定头饰轮廓保持。失败是输出差异，不是PNG格式问题。没有执行程序锁区拼贴、补像素、手工描线、颜色修正或逐帧调整缩放/偏移。

### 来源、固定转换及视觉检查

采用imagegen技能与内置image_gen.imagegen，每次一张。生成前实看v3和正式neutral；第一次从v3局部编辑，仅请求低位羽尖微抬/微内收，neutral只作固定像素参照。首次失败后，第二次以首张为编辑目标、v3及neutral为参照，针对明确的头冠/侧羽饰漂移做唯一一次局部修订，要求保留其余区域。完整实际提示词保存在下表链接，不把提示词要求当作实际结果。

| 次数 | 归档源图 / 提示词 | 工具原始输出文件名 |
| --- | --- | --- |
| 1 | [v1 source](../../assets/characters/aemeath-v1/source/art007-trial-v1-source.png) / [prompt](../../assets/characters/aemeath-v1/source/art007-trial-v1.prompt.txt) | `exec-b5c30698-63fd-473e-8a51-e4adb105286e.png` |
| 2 | [v2 source](../../assets/characters/aemeath-v1/source/art007-trial-v2-source.png) / [prompt](../../assets/characters/aemeath-v1/source/art007-trial-v2.prompt.txt) | `exec-ed8d9189-05be-419c-a561-0e20103a1157.png` |

工具原件目录为 `C:/Users/bigxi/.codex/generated_images/01a0abdf-e294-78d3-a6b8-eb0cef96a2a9/`，原件保留。两张实际都是1205×1306，取景/头身比例目视未见整体缩放或平移；脚基线也保持一致，但局部冠线变化仍不合格。同一固定变换：全画布像素中心最近邻到96×104、alpha阈值128、整数偏移(0,+5)，无裁剪、包围盒归一化或自适应对齐。

新增 [check-art007.py](../../assets/characters/aemeath-v1/source/check-art007.py)仅在source写入本卡候选、4×并排检查图及JSON报告；复用既有PNG读写函数，不改正式素材。源画布尺寸不符时只输出失败报告，不继续适配导出。所有正式帧和manifest的哈希在脚本运行前后核对一致。

| 项目 | 第一次v1 | 第二次v2 |
| --- | --- | --- |
| 96×104候选 | [art007-trial-v1-96.png](../../assets/characters/aemeath-v1/source/art007-trial-v1-96.png) | [art007-trial-v2-96.png](../../assets/characters/aemeath-v1/source/art007-trial-v2-96.png) |
| 4×对比（左neutral，右候选） | [v1对比](../../assets/characters/aemeath-v1/source/art007-trial-v1-compare-4x.png) | [v2对比](../../assets/characters/aemeath-v1/source/art007-trial-v2-compare-4x.png) |
| 只读差分与哈希 | [v1报告](../../assets/characters/aemeath-v1/source/art007-trial-v1-report.json) | [v2报告](../../assets/characters/aemeath-v1/source/art007-trial-v2-report.json) |
| RGBA8 / 静态PNG / CRC / alpha=0或255 / 非全透明 | 全部通过 | 全部通过 |
| 文件大小 / 不透明像素 | 8899 bytes / 3106 | 9067 bytes / 3127 |
| 包围框（含端点） | (11,21)–(84,97) | (11,22)–(84,97) |
| 冠尖 / 中央脚末行 | y21失败 / y93通过 | y22通过 / y93通过 |
| 两侧羽饰极值内收 | 左2px、右2px | 左2px、右2px |
| 羽饰左右alpha变化像素 | 32 / 33 | 35 / 36 |
| 羽饰不透明集合最大Chebyshev距离* | 左3px、右3px | 左3px、右3px |
| 全固定头部alpha变化像素 | 27 | 39 |
| 上冠及相邻头发矩形alpha变化 | 25 | 31 |
| 侧羽饰矩形alpha变化 | 3 | 6 |
| 全固定头部共同不透明像素中的RGB变化数 | 1689 / 1766 | 1715 / 1762 |
| 固定头部最大通道差 / 平均每像素最大通道差 | 131 / 6.751 | 249 / 10.697 |
| 固定头部最大通道差>24的像素数 | 88 | 130 |

*额外的幅度诊断：对两个羽饰不透明像素集合分别计算双向最近点的最大网格距离，并非语义对应羽尖的位移。它说明内收极值合格不代表全部局部变化均≤2px；不能将此指标单独解释成角色整体移动。固定头部检查范围为x0…95/y0…68；上冠及相邻头发为x20…75/y18…47；侧羽饰为x61…78/y39…59。后两者是保守矩形检查区，有重叠且包含相邻像素，不是假称精确分割的头饰mask，计数不相加。RGB只比较共同不透明像素，alpha新增/移除坐标另列在JSON中，不将色值变化和轮廓变化混成一个数字。

两张均实际通过view_image查看原图、1×候选和4×并排图。脸、睁眼、衣服及脚保持可识别，低位羽饰有真实局部形变，绝非整图平移；阈值后平移裁掉的不透明采样数为0，留白未触边。v1冠尖高一像素、羽饰偏上翘；v2冠尖高度恢复，但冠弧走势与冠下留空相对neutral发生变化，侧羽饰和静止色块也没有完全保持。第二次修订没有达到“固定头饰alpha不变”，不能因y22通过就宣称头饰修复。RGB差异可能包含小幅重编码色差，因此单列统计；较大的局部差异与并排观察仍支持失败结论。

没有新建manifest，(48,94)仅作为固定参照记录；不是新增包。未运行宿主、浏览器动态检查或无关全套测试：本卡单帧已在静态门槛失败，不将静态比较扩写为连续无闪动或可用动画。

### 实际验证与交接

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/check-art007.py v1
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/check-art007.py v2
& ./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art007-trial-v1-96.png
& ./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art007-trial-v2-96.png
git diff --check
git diff --exit-code -- assets/characters/aemeath-v1/frames assets/characters/aemeath-v1/manifest.json
```

导出/报告命令exit0表示成功生成检查材料，**报告结论均为FAIL**，不是验收通过。既有Inspect-Png两次均exit0，确认96×104、位深8、色彩类型6、半透明0、alpha两种、大小低于256KiB。v1正式格式候选SHA-256为 `ea7b18fe821f32e9bf0586d122eb02f017c69e42528a411fbde44e03d885deac`，v2为 `6edad393443b1379d2bb7a688a3a5be2f7502de6140aa36fe8cffa205e92fc17`。这些文件只位于source；neutral及其余正式帧、manifest保持未变。

交PM验收的是失败试修与可复核证据，不是获准使用的动画帧。已达到本卡最多两次生成限制，到此停止，不继续试图靠全局偏移修冠尖，也不通过程序拼贴静止区域绕过限制。按任务卡直接回报统筹，等待PM决定；自动跟进仍暂停，本任务不自行开启后续。

## ART-008：授权局部合成，一张待机试样（2026-09-21）

用户经PM明确回复“允许”，新增授权程序保留neutral静止像素，只合成下部羽饰变化区域。本卡按此授权执行，未调用imagegen、未用程序绘制新角色。开工工作区干净，重读README、开发流程、任务交接及ADR0003；Issue CLI仍沿用上轮不可用记录，现行范围以对话ART-008为准。只新增source试样、脚本、mask、报告和预览，正式frames、manifest、代码、接口、锁文件未修改。

**自检结论：单帧局部合成可行，推荐v2；格式/静止像素/接缝自检通过，待PM验收。** 两版mask后停止。左右极值各内收2px，符合1–2px目标；外侧羽尖局部不透明集合最大网格距离仍为3px，属于保留的幅度限制，不能宣称所有局部像素只动1–2px，也不能将此试样称为完整自然呼吸动画。

### 来源、合成规则与显式mask

- 不可变底图：`frames/neutral.png`，SHA256 `5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d`。
- 变化素材：`source/art007-trial-v1-96.png`，SHA256 `ea7b18fe821f32e9bf0586d122eb02f017c69e42528a411fbde44e03d885deac`。采用既有已对齐96×104候选；本轮没有再缩放、阈值化或移动，原始生成来源及完整提示词见ART-007。
- mask由指定下部羽饰区域内的neutral/候选不透明轮廓并集及1px相邻透明边带形成，不是把矩形整块当mask。坐标零起算、两端包含，右侧按 `x→95-x` 对称；实际所有mask像素坐标保存在每版report.json的 `maskCoordinatesXY`，白色mask PNG为相同区域。
- mask内**完整替换RGBA**，包括将旧姿态对应像素替换为透明；mask外直接保留neutral字节。没有仅透明叠加，没有手绘新像素或调色过渡，没有把mask扩大到头部。

| 版本 | 左侧允许域（包含端点） | mask像素 / RGBA变化像素 | 选择理由 |
| --- | --- | --- | --- |
| v1 | y82–84:x15–26；y85–87:x12–26；y88–98:x8–26 | 494 / 357 | 初版接缝目视无明显断口，但内缘靠近发梢/羽根交界，保留为历史候选 |
| v2（推荐） | y83–84:x15–23；y85–87:x12–23；y88–98:x8–23 | 392 / 278 | 进一步保留整条x24–71中央区域及y<83区域，减少静止羽根附近色值替换；保留同样的外侧动作轮廓 |

脚本：[compose-art008-v1.py](../../assets/characters/aemeath-v1/source/compose-art008-v1.py)、[compose-art008-v2.py](../../assets/characters/aemeath-v1/source/compose-art008-v2.py)。均仅用标准库、复用既有PNG读写，运行前后检查全部正式帧和manifest哈希；未新增依赖。

### 产物与实测数值

| 产物 | v1 | v2（推荐） |
| --- | --- | --- |
| 试样96×104 | [v1 PNG](../../assets/characters/aemeath-v1/source/art008-v1-96.png) | [v2 PNG](../../assets/characters/aemeath-v1/source/art008-v2-96.png) |
| 显式mask | [v1 mask](../../assets/characters/aemeath-v1/source/art008-v1-mask.png) | [v2 mask](../../assets/characters/aemeath-v1/source/art008-v2-mask.png) |
| 差分/区域/哈希 | [v1报告](../../assets/characters/aemeath-v1/source/art008-v1-report.json) | [v2报告](../../assets/characters/aemeath-v1/source/art008-v2-report.json) |
| 离线切换预览 | [v1 HTML](../../assets/characters/aemeath-v1/source/art008-v1-inspection.html) | [v2 HTML](../../assets/characters/aemeath-v1/source/art008-v2-inspection.html) |
| 大小 | 8786 bytes | 8793 bytes |
| mask外RGBA差分 / 头部差分 / 中央身体脚差分 | 0 / 0 / 0 | 0 / 0 / 0 |
| 清除旧不透明 / 新增不透明 | 47 / 18 | 47 / 18 |
| 包围框 / 中央脚末行 | (11,22)–(84,97) / y93 | 相同 |
| alpha值 / 不透明像素 | 0、255 / 3079 | 相同 |
| 羽饰左右极值内收 / 集合最大局部距离 | 2、2px / 3、3px | 相同 |

两张CRC、静态RGBA8、96×104、二值alpha、非全透明、256KiB上限均通过。锚点沿用参照(48,94)，不创建manifest。v2输出SHA256为 `31b0f4265b047685db6256c6891882eb19ada91b8d74499db1c404177a49b749`。v2边界上两处alpha变化为外侧新增抬起羽尖 `(17,83)` / `(78,83)`，不是羽根切口；每版报告另列边界共同不透明色值变化坐标，不能因为mask外零差分就跳过接缝观察。3px距离按ART-007相同的双向不透明集合最近点度量计算，是局部轮廓变化诊断，不能等同整图移动或精确语义羽尖轨迹。

### 实际视觉检查

通过view_image实际查看两版浅底1×及浅/深底4×并排PNG（左neutral，右试样）。v2静态图：[浅底1×](../../assets/characters/aemeath-v1/source/art008-v2-light-1x.png)、[深底1×](../../assets/characters/aemeath-v1/source/art008-v2-dark-1x.png)、[浅底4×](../../assets/characters/aemeath-v1/source/art008-v2-light-4x.png)、[深底4×](../../assets/characters/aemeath-v1/source/art008-v2-dark-4x.png)。v1同名文件全部保留。

随后通过CUA打开明确本地地址 `http://127.0.0.1:8768/art008-v1-inspection.html` 和v2对应地址，实际查看1×浅深底、4×浅底，并向下滚动查看4×深底；使用neutral/试样按钮暂停对照，再恢复600ms交替。浏览器截图观察到了neutral和试样两种状态，不能只凭DOM标签声称视觉通过。头冠、侧头饰、脸与脚在切换对照中保持位置/色块不变；外侧羽片上翘内收可辨，羽根连续，未见旧轮廓残留形成双翼、直角矩形缺口或边界突然断开。v2减少了羽根附近替换，仍能保留动作，故选为交付试样。细羽尖本身有原生成像素的尖角，4×下运动更明显；该检查支持单帧接缝可行，不代表所有节奏下动作自然。600ms仅为检查节奏，没有派生正式动作时序或扩展整套动画。

无原生宿主运行、跨DPI或完整待机连续性验收；本卡没有改正式包，不重跑无关全套测试。预览HTML已内嵌图像，可离线打开，临时HTTP服务不作为永久交付依赖。

### 实际命令、限制与交接

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/compose-art008-v1.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/compose-art008-v2.py
& ./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art008-v1-96.png
& ./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art008-v2-96.png
git diff --check
git diff --exit-code -- assets/characters/aemeath-v1/frames assets/characters/aemeath-v1/manifest.json
```

合成脚本和两次既有Inspect-Png均exit0；独立读取输出/mask再次比对，确认mask外RGBA零差分、mask内逐像素等于来源候选、y<83及x24…71保护区零差分、源文件哈希一致。正式目录无差分，未改变原件。自检通过的是**v2局部合成方式与该单帧接缝**；局部3px轮廓变化已显式交接，最终自然度和后续使用由PM决定。两版mask已停止，不扩大到头部，不进入其他动作。交付后直接回报统筹并等待验收，自动跟进仍暂停。

## ART-009：两动作局部合成候选包（2026-09-21）

前置：PM已独立验收ART-008提交1e736ab的v2方法，复核变化278像素、mask外/保护区0差分、格式8793 bytes及浅深底4×接缝；局部集合距离3px作为披露限制接受。最新对话卡授权在source内修订idle-soft/idle-smile候选，不授权替换正式目录或进入拖动。沿用现有worktree/分支，开工干净，现行ADR0003及契约不变。未新增imagegen、未手绘角色、未改生产代码/接口/锁文件，没有新增依赖。

**本轮结论：候选自检通过，交PM/QA；不是正式素材切换或完整六动作交付。** 每张新合成只用一版mask，没有为消除差分扩大到无关区域。已验峰值帧直接复制，不再次合成或改动。

### 候选包、来源与mask

- 可加载候选目录：`C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source/art009-v1-package`，其内独立[manifest](../../assets/characters/aemeath-v1/source/art009-v1-package/manifest.json)为 `aemeath-v1 / 0.3.0 / character`；schema1、sourceScale1、96×104、anchor(48,94)、fallback neutral。
- [构建脚本](../../assets/characters/aemeath-v1/source/build-art009-v1.py)、[差分/来源哈希/逐像素mask报告](../../assets/characters/aemeath-v1/source/art009-v1-report.json)。正式neutral逐字节复制，SHA仍为 `5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d`。
- soft-light来自既有ART-006 `frames/soft-b.png`，只取外侧羽饰；soft-peak逐字节复制已验 `source/art008-v2-96.png`，SHA仍为 `31b0f4265b047685db6256c6891882eb19ada91b8d74499db1c404177a49b749`。没有用相同图假造中间态。
- smile-half/closed来自既有同名生成导出帧，只替换眼口内像素；不改变面部外轮廓。所有来源完整提示词/原件在ART-006/007记录，未把局部合成称为新增绘画或游戏逐帧复刻。

羽饰mask沿用ART-008 v2的允许域（y83–84:x15–23；y85–87:x12–23；y88–98:x8–23，右侧镜像x→95-x），再取base/donor轮廓并集及1px边带。眼部允许域按左眼逐行：y56:x33–41、y57:x33–43、y58–62:x32–44、y63:x34–43、y64:x35–42；右眼镜像。为避免带入发梢/腮红，排除neutral中 `R>130且R>1.2G且B>1.12G` 的粉色像素；此为限定ROI内保守筛选，不宣称通用人物分割。嘴部仅x45–50/y65–67。眼口mask内base/donor均为完全不透明；仅复制既有生成图RGBA，不绘制、调色或平滑边缘。mask外RGBA严格保持neutral。所有mask PNG与精确坐标在source和报告中，可独立复核。

| 图帧 | Bytes | mask像素 | RGBA变化 | alpha变化 | mask外RGBA差分 |
| --- | --- | --- | --- | --- | --- |
| [soft-light](../../assets/characters/aemeath-v1/source/art009-v1-package/frames/soft-light.png) | 8767 | 374 | 263 | 52 | 0 |
| [soft-peak](../../assets/characters/aemeath-v1/source/art009-v1-package/frames/soft-peak.png) | 8793 | 392（已验mask） | 278 | 65 | 0 |
| [smile-half](../../assets/characters/aemeath-v1/source/art009-v1-package/frames/smile-half.png) | 8880 | 222 | 217 | 0 | 0 |
| [smile-closed](../../assets/characters/aemeath-v1/source/art009-v1-package/frames/smile-closed.png) | 8777 | 222 | 219 | 0 | 0 |

四张均冠尖y22、中央脚末行y93，无触边裁切；静态RGBA8、二值alpha、非全透明、CRC及256KiB门槛通过。笑脸整张alpha与neutral相同，面部外轮廓未变；头饰、头发、衣服、身体脚均在所选眼口mask外保留原像素。两张羽饰保留y<83及中央x24–71。轻/峰值两侧极值均内收2px，但局部集合距离分别2px/3px，左右alpha差分别26/26与32/33，真实形状和哈希不同。轻姿态先收外羽，峰值再抬外尖；内侧较低羽尖有1px回摆，并非每个点的线性插值。没有观察到整体幅度明显倒序，峰值3px限制保留待QA判断。

### 时序与预览

| 动作 | 六时序项 | 时长ms / 总时长 | 播放与来源 |
| --- | --- | --- | --- |
| idle-soft | neutral → soft-light → soft-peak → soft-peak → soft-light → neutral | 400,150,150,400,150,150 / 1400 | loop / original |
| idle-smile | neutral → smile-half → smile-closed → smile-half → neutral → neutral | 120,120,500,120,120,220 / 1200 | once / adaptation |

重复引用为峰值停留、收势或往返，非重复文件充数。总计3动作、5张不同PNG，neutral1000ms单帧回退。三个拖动动作未声明，不声称完整角色包。

[离线检查预览](../../assets/characters/aemeath-v1/source/art009-v1-inspection.html)内嵌候选真实PNG和时序；[预览生成脚本](../../assets/characters/aemeath-v1/source/make-art009-v1-preview.py)核对6项时长数组、总时长、引用和固定锚点。每张另有 `art009-v1-<frame>-light/dark-1x/3x.png` 并排图（左neutral，右候选）及 `art009-v1-<frame>-mask.png`。脚本没有任何写入正式目录的步骤。

实际CUA浏览器地址为 `http://127.0.0.1:8769/art009-v1-inspection.html`。已在浅/深底1×和3×实际看五种姿态，并检查重复时序项引用；半闭眼金色眼睛保留，闭眼帧没有明显原睁眼残影或矩形皮肤接缝，羽根未见双影或缺口，静止头饰无观察到跳变。逐帧暂停查看轻姿态450ms、半闭眼180ms、闭眼400ms等；连续idle运行在约4.8秒截图时已超过两个循环。

15秒模式检查最初长等待选择器超时，未将该尝试记通过；随后按当前DOM状态重播，用2/4/6/8/10/12/14秒短检查点跟随，成功完成一次连续运行：DOM约4086ms为idle第6项（已超过两循环），15284ms为笑脸第3项，16393ms返回idle第1项。对应实际截图约4140/15345/16441ms，展示待机、闭眼笑、恢复睁眼待机，均含浅深1×/3×。这是浏览器运行与截图抽样，不是假称逐个显示刷新帧录制；结合先前逐帧眼口检查确认完整笑脸连接未见明显接缝。浏览器时序不代替下述生产宿主日志，更不代表原生透明窗口观感已由QA验收。

### 定向格式与生产宿主验证

实际命令：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/build-art009-v1.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/make-art009-v1-preview.py
foreach ($name in @('neutral','soft-light','soft-peak','smile-half','smile-closed')) {
  & ./scripts/qa/Inspect-Png.ps1 -Path "assets/characters/aemeath-v1/source/art009-v1-package/frames/$name.png"
}
```

全部exit0；独立读取实际PNG和mask再核对四图mask外RGBA差分0、mask内donor不匹配0及报告SHA。neutral与已验soft-peak逐字节保持原件；正式目录全部保护哈希一致。未重跑无关全套测试。

复用现有已验生产宿主，先核对exe SHA256等于 `E3951560B446CB708F97A928BA96940FD4B4B3182DC9FAA1C754C2ACF27113B0`（代码基线9f7d270），不重新构建无变化代码。实际启动参数：

```powershell
$art009Exe = Join-Path $PWD 'artifacts/host-win-x64/Aemeath.Host.exe'
$art009Package = Join-Path $PWD 'assets/characters/aemeath-v1/source/art009-v1-package'
$art009Log = Join-Path $PWD 'assets/characters/aemeath-v1/source/art009-v1-host.jsonl'
$art009Probe = Start-Process -FilePath $art009Exe -ArgumentList @('--package', ('"' + $art009Package + '"'), '--diagnostics', ('"' + $art009Log + '"'), '--mode', 'automatic', '--scale', '2', '--exit-after-ms', '18000') -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
$art009Probe.WaitForExit(30000)
```

实际PID21956、exit0；生产加载器接受 `aemeath-v1/0.3.0` 且disabled=[]。日志具备package-loaded、pet-loaded、render-callback、layout、shutdown，无package-rejected/position-error；从首个idle到首个smile14999ms（日志采样差），笑脸索引0…5齐全，仅1次natural-end，随后回idle-soft。完整[宿主日志](../../assets/characters/aemeath-v1/source/art009-v1-host.jsonl)和[摘要](../../assets/characters/aemeath-v1/source/art009-v1-host-summary.json)保留。这是生产加载与自有进程时序证据，不称为原生窗口连续视觉验收。

### 交接

交QA的是source内0.3.0候选子包及可重现mask/来源/预览，未修改正式frames或manifest。所有新增文件局限在source和本记录；提交前 `git diff --check` 及正式目录差分检查通过。局部合成和浏览器自检通过，但峰值3px局部距离、轻姿态内羽1px回摆及最终动态观感需QA独立评审。原生宠物视觉、跨DPI、拖动及真实Codex联动未在本卡执行。向统筹回报后等待QA，不进入拖动或其他后续，自动跟进仍暂停。

## ART-010：拖动三个关键姿态候选（2026-09-21）

### 范围与基线

现行对话任务卡优先。读取PM最新project-status和ADR0003；用户对正式0.3.0反馈“待机正常，拖动缩放和退出均没问题，可以进行下一步”。本卡只交pickup/hold/release各一张关键姿态，不创建4项动作或正式时序，不改正式manifest/frames、代码或其他模块。本轮无新增任务、无后台跟进恢复。

选择不合并统筹分支，避免本分支历史0.2.0正式素材回流。只读复制PM工作区 `C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1/` 的manifest和5帧到 `source/art010-baseline/`，PM读取时HEAD为 `a2442f3bd023a97fae70727e21f62af97b5adf68`。复制包版本0.3.0及逐文件SHA记录在 `art010-v1-report.json`。所有候选以复制的neutral为不可变底图，其SHA仍为5c8f851a87f2e7c336365ce0323c76bb6fefd6f6eb65d6eb5c76baf701ee8e0d。

绘制使用内置imagegen，以已验 `neutral-generated-v3-edge-cleanup.png` 为编辑源（1205×1306，SHA45b754f137d68f7d7acd38c25719e853af75bd4f4d11ca1cbd33cfca91a35948）。逐张prompt和原始生成源保存于art010前缀文件，未用程序绘画角色。没有将头冠当拎手，未改变头部姿势。

### 生成与选择

| 姿态 | 使用候选 | 次数 | 表现 | 脚底y |
| --- | --- | --- | --- | --- |
| pickup | art010-pickup-v1-96.png | 1/2 | 双膝收起，短靴靠拢，中央衣摆随屈腿变化 | 88 |
| hold | art010-hold-v2-96.png | 2/2 | 双腿稍松、短靴微分开，仍高于neutral | 91 |
| release | art010-release-v1-96.png | 1/2 | 双膝外展，手向中间收，脚落回原高度 | 93 |

hold-v1被主动退回：长白靴改变造型且脚底y95，比neutral低2px。原图、转换、合成和报告保留为失败证据。第二次恢复短灰靴且脚底y91，不继续生成。pickup实际收高5px，比提示中的约4px略大，作为可评审动作幅度披露。

原始生成文件对应：pickup-v1=exec-f894788d-0410-411e-8607-b9c11442d503.png；hold-v1=exec-a534899d-2d96-4d11-9011-97689907d723.png；hold-v2=exec-3171d7af-bdd9-47d4-9e21-e5b5f110cd2e.png；release-v1=exec-5e3885cf-f2c9-4783-8a32-e32ba9ae142e.png。均从当前任务generated_images目录原样复制，原文件保留。

### 转换、动作mask与差分

`art010-build.py`复用已验PNG编解码函数，最近邻pixel-center采样、alpha阈值128、整数偏移(0,+5)，没有按每帧外接框重新对齐。生成源都为1205×1306；阈值后越界不透明样本0。输出96×104、锚点参考(48,94)，全图bbox仍为(9,22)-(86,97)，因外侧羽饰静止，bbox不用于推断脚位置。

每张只用一版mask：显式闭区间x35…60、y75…97，共598像素。范围限于中央躯干、内侧手臂、衣摆和腿靴；所有y<75或x<35或x>60像素直接来自neutral。区域内整RGBA替换，包含透明擦除旧脚；不叠加旧轮廓，不绘制新像素。mask PNG及全部坐标、边界变化坐标在报告中可复核。头冠、脸、头发及外侧羽饰保持原像素。

| 使用候选 | RGBA变化像素 | mask外变化 | 头部变化 | PNG字节 |
| --- | --- | --- | --- | --- |
| pickup-v1 | 455 | 0 | 0 | 8596 |
| hold-v2 | 451 | 0 | 0 | 8807 |
| release-v1 | 472 | 0 | 0 | 8924 |

### 实际验证

以下均实际执行，退出0：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art010-build.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art010-preview.py
foreach ($name in @('pickup-v1','hold-v2','release-v1')) {
    ./scripts/qa/Inspect-Png.ps1 -Path ("assets/characters/aemeath-v1/source/art010-" + $name + "-96.png")
}
git diff --check
git diff --name-only -- assets/characters/aemeath-v1/frames assets/characters/aemeath-v1/manifest.json src
```

独立System.Drawing读取三张均96×104、RGBA8/color6、0半透明、仅两种alpha，体积均小于256KiB，结果保存在 `art010-inspect-png.json`。构建脚本检查正式文件前后SHA不变，Git正式目录与src差分为空。

实际打开本地 `http://127.0.0.1:8910/art010-inspection.html`，浏览器逐次切换pickup→hold→release→neutral并读取状态与截图，检查浅深底4×及1×。三者姿态可区分，未见明显头部跳变、旧脚双影、颈口断裂或羽根断口；查看合成浅深底对照图。该检查是关键姿态自检，不是完整动画、独立QA或原生桌宠拖动验收。页面内全部PNG为嵌入数据，不依赖外网。

### 限制与交接

release胸前白饰压缩及手部收拢较明显，与neutral的衣饰轮廓有变化，需PM确认是否接受这一动作表达；当前未将其称为最终外观通过。锁定头部的方案使动作集中在小身体，1×动作比4×更含蓄。头冠原有不规则像素沿用已验neutral。没有头部整体换姿，没有新增完整动作时序或宿主接入，不宣称桌宠已播放这三张。

建议统筹评审三个选中PNG和 `art010-inspection.html`，可从neutral切换观察保护区与身体接缝。浅深对照图顺序均neutral / pickup-v1 / hold-v2 / release-v1。只选择性采用本卡art010前缀source文件；不要合并本分支历史正式0.2.0包。后续逐帧扩展须等关键姿态确认及新任务卡；本轮交付后停止制作。

## ART-010R：release衣饰保护返修（2026-09-21）

PM审阅6732412后指出旧release胸前白饰变细，未接受ART-010整体，也未授权扩展时序。本卡仅复用现有release donor收紧局部合成mask；没有新imagegen调用，pickup/hold及正式包不动。

使用 `art010-release-revise.py` 独立脚本，不修改ART-010既有脚本或候选。neutral仍来自只读复制的0.3.0基线；donor为 `art010-release-v1-donor.png`，SHA2303d2f49ea5cec19b941b536fb2db7ddb63fa807d61bbdcf76b165321d9d381。输出 `art010-release-r1-96.png`，SHA6162ae0feee072c7c6a06dbd7e94a89b2ef969cb354ed029d3f12a40209002eb。

只尝试一版mask：闭区间x38…57/y83…94，另排除y83的x45…50和y84的x46…49，共230像素。全部y<83保留neutral；实际检查白色菱形至y83、金色尖端至y84，故采用阶梯状中央保护区，避免简单水平截断衣饰。更外侧手臂、衣摆和羽饰也全部保留neutral，变化集中在屈膝及短靴。区域内直接使用现有donor完整RGBA，包含透明擦除，不绘制或混合新像素。全部mask坐标见 `art010-release-r1-report.json`，可视mask见同前缀mask.png。

实际验证命令（退出0）：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art010-release-revise.py
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art010-release-r1-96.png
git diff --check
```

结果：96×104、RGBA8、alpha仅0/255、8869字节；205像素变化，mask外变化0，y<83变化0，冠顶y22、脚底y93，锚点仍(48,94)。脚本核验正式manifest/frames、pickup、hold、旧release及donor SHA不变；既有文件未覆盖。转换沿用已验96×104 donor，无额外缩放、平移或裁切。

实际查看浅深底1×、4×对照PNG，均按neutral / 旧release / 修订release排列。白色菱形和金色尖端完整保留；屈腿与向外落脚仍可辨，未见明显矩形接缝、衣摆腿根断裂或旧脚双影。仅进行了静态并排视觉自检，没有宣称完整动画或原生宿主验收。附独立离线切换页 `art010-release-r1-preview.html` 供PM复核；本轮未用浏览器运行该页面。

r1达到本次返修自检要求，不使用第二版mask额度。外观最终确认及ART-010整体验收仍由PM决定；不扩展完整拖动时序。交付仅source/art010-release-r*文件和本记录，不推广正式包。

## ART-011：带表情的0.4.0拖动时序候选（2026-09-21）

### 范围、最终入口与保留来源

PM已接受ART-010的pickup-v1、hold-v2和release-r1作为时序基础。本轮按ART-011制作source内0.4.0候选；制作期间用户追加“可以在拿起，拖动和放下中修改人物表情，更加生动活泼”，PM明确扩展眼口mask范围，合并进入本轮交付。

最终包为 `source/art011-package/`，完整互动页为 `art011-inspection.html`，表情并排图为 `art011-expression-keys-light-3x.png` / dark对应图及1×图，顺序neutral / pickup惊讶 / hold半睁眼 / release闭眼笑。实际最终加载证据文件统一为 `art011-expression-host-*`。无表情的早期预览和包另存 `art011-body-only-inspection.html`、`art011-body-only-package/`，原早期宿主日志 `art011-host-*` 和浏览器观察仅作过程来源，不能代替最终表情版验证。

沿用art010-baseline已验0.3.0的五张PNG逐字节复制。manifest保留原始字节结构，仅替换版本并在actions末尾追加三动作；脚本反向删除新增块、恢复版本后，要求整份manifest与基线原字节相同，因此原三动作未重序列化或改时长。最终12张PNG、6动作，fallback neutral、96×104、锚点(48,94)不变。未合并统筹分支或历史0.2.0包；正式manifest/frames与代码未改。

### 最终时序

| 动作 | 播放 | 四项文件名（frames/内） | 毫秒 |
| --- | --- | --- | --- |
| drag-pickup | once | neutral → hold-surprise → pickup-surprise → hold-half | 80 / 80 / 100 / 100 = 360 |
| drag-hold | loop | hold-half → hold-light-half → hold-peak-closed → hold-light-half | 180 / 180 / 180 / 180 = 720 |
| drag-release | once | hold-half → release-closed → release-half → neutral | 80 / 100 / 120 / 160 = 460 |

拎起先松腿再收腿，最后回悬停腿姿态并微笑，与hold首项逐字节同图。hold腿姿态保持，羽饰轻/峰/轻往返，峰值闭眼眨眼，其余半睁眼微笑；四项为三张不同图，不以静帧充数。release由松腿入落稳，闭眼笑后半睁眼，最后neutral与idle-soft首项同图。身体脚底沿用已验y88/91/93，不使用整图平移。pickup、release身体图直接来自PM已验关键姿态；新增hold羽饰图用已验soft-light/soft-peak局部像素合成。

### 表情绘制与mask

惊讶用内置imagegen编辑neutral-v3，只生成一次，源图 `art011-surprise-v1-source.png` 原样保留，原始文件exec-b61115c2-e2e8-4ea6-8ffc-c16c0de5c4cd.png，完整prompt在同前缀prompt.txt。没有程序绘脸。1205×1306源按既有pixel-center最近邻、alpha128、整数(0,+5)转换，越界不透明采样0。眼睛略睁大和小张嘴，不采用哭泣/恐惧表达；半睁眼和闭眼笑只复用0.3.0原素材。

眼口mask复用ART-009已验222像素遮罩：眼部逐行范围限制在x32…63/y56…64，排除原粉色头发/腮红像素；嘴为x45…50/y65…67。全部原与donor像素alpha255，合成不改变身体图的任何alpha。脸外轮廓、腮红、头发、冠和侧头饰保持neutral。每个最终新图另有明确union-mask.png，身体/羽饰mask与眼口mask无交集，union外RGBA差分0。最终报告 `art011-expression-report.json` 包含来源和哈希；`art011-check-report.json` 从最终PNG和并集mask再次读回验证。

身体mask继续采用ART-010的中央躯干范围；release采用已验ART-010R阶梯式胸前保护；hold-light/peak另并入ART-009各自下羽饰mask。新增表情仅1版mask，惊讶1/2生成机会，未扩大头部轮廓或新画无关区域。全部7张新合成相对neutral变化像素依次为660、664、668、931、948、424、422，union外0；惊讶/半睁眼/闭眼笑相对身体图分别改变209/217/219像素，脸部alpha变化0。

### 实际验证与预览

实际执行以下命令均退出0：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art011-build.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art011-expressions.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art011-preview.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art011-face-preview.py
./assets/characters/aemeath-v1/source/art011-run-host.ps1
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art011-check.py
git diff --check
```

build生成body-only来源；expressions再生成最终包。所有PNG经生产格式检查脚本Inspect-Png读取：12张均96×104 RGBA8/color6、alpha仅0/255，0半透明，最大8886字节，小于256KiB。所有manifest引用存在；三段时长及4项固定值通过。原五张与基线字节相同，新七张的静止区/并集mask检查通过。

实际自有宿主三次运行（manual模式显式clip，scale2，2200ms定时退出），最终表情版PID41972/41284/14376均exit0；生产加载器接受aemeath-v1/0.4.0、disabled=[]，三个动作的索引0…3均出现在真实frame日志，均有shutdown、无package-rejected/position-error。运行脚本记录exe和最终manifest SHA，保留完整jsonl及Inspect结果；为防覆盖证据，重新运行需先选择新的日志文件名。未修改程序；真实控制器和鼠标捕获边界留给独立QA。

实际浏览器访问本地art011-inspection.html，制作方查看浅深1×/3×，检查表情关键帧、逐项与情境；最终观察记录 `art011-expression-browser-observations.json`。正常情境560ms为pickup惊讶，760ms转hold微笑，1120ms闭眼眨眼；2580ms落稳闭眼，2680ms半睁，2800ms恢复neutral，2960ms回idle。快松手440ms进入release半睁眼，跳过未到达的惊讶段；再抓730ms回pickup入口neutral，810ms惊讶，1090ms回hold微笑。hold719→720ms检查轻羽饰回首项，表情同为半睁眼。实际点击预览按下/松手按钮后，连续状态出现pickup→hold→release→idle。

身体版早期曾因100ms时序项漏采样导致一次浏览器等待超时，改用时间滑块定位；未将该超时当成素材失败或连续视觉通过。最终采用关键时刻截图、逐项定位与按钮实时状态交叉检查。并排表情图可辨小惊讶、眯眼和闭眼笑；未见明显头冠抖动、脸边改变、衣摆/羽根断口或旧脚双影。该结论是制作方自检，不代替PM/QA动态验收，也不称网页模拟为原生拖动。

### 限制与交接

1×小张嘴较含蓄；hold每720ms眨眼一次，节奏是否理想由PM视觉评审决定。羽饰沿用已验素材的峰值局部集合距离3px和内羽1px回摆限制。固定四项动作在中途松手/再抓会从目标动作入口开始，不做上一姿态插值；快松手可能跳过惊讶，属于取消pickup的预期。真实输入下的节奏及任何阶段切换自然度仍需QA评审，未宣称全部边界通过。

本轮仅交付source/art011-*与本记录；请只选最终art011-package，不采用body-only历史过程包，不整体回流分支的旧正式0.2.0。等待PM/QA独立验收，正式0.3.0保持，不推广、发布或进入联动。

## ART-012：中幅扇翼两端关键姿态试样（2026-09-21）

### 任务边界与基线

用户追加拖动时中等幅度扇动翅膀。PM派ART-012仅制作两端关键姿态供审核，暂停旧hold视觉放行；本卡不扩循环、不改时长、不替换正式包。读取最新PM状态后以395fce2的最终 `art011-package/frames/hold-half.png` 为不可变底图，保留微笑表情、收起身体、头冠、头发、脸外轮廓与锚点(48,94)。绘制仍以neutral-v3高分辨率原图为imagegen编辑源，最终只采用翼部像素。

### 次数与来源

内置imagegen共3次：上扬v1、上扬v2、下压v1。各原图与完整prompt保存为art012相应前缀source.png/prompt.txt。上扬v1明显把翅根提到头发两侧，翼片过大，主动退回；只保留原图、96×104完整donor与失败理由，不将其截断后冒充可用姿态。上扬v2已达2次上限；下压仅用1次。全部合成只用一版翼部mask，未新增程序绘制像素。

生成原始文件：up-v1=exec-fcf73410-4dd2-4fd4-8226-85b3b2b5480c.png；up-v2=exec-383b3f01-d407-4cab-834c-091913dfb2c5.png；down-v1=exec-f097869e-bb8a-4dbf-92fb-4f87fd5cf853.png。原始generated_images文件保留，仓库副本逐字节复制。

### 合成与幅度证据

`art012-build.py`独立生成：1205×1306源采用既有pixel-center最近邻、alpha128、整数偏移(0,+5)，没有对整图或翅膀做程序旋转/平移/拉伸；姿态来自imagegen重绘。明确翼部mask左侧为x4…23/y78…84、x4…26/y85…88、x4…30/y89…102，右侧镜像x→95-x。全部y<78及中央x31…64保持底图；脚本禁止mask包含底图粉发像素。mask内完整RGBA替换包含透明擦除，去除旧翼轮廓；mask外RGBA差分0。

| 候选 | PNG字节 | 变化像素 | 旧不透明清除 / 新增 | 全图bbox | 底部透明余量 |
| --- | --- | --- | --- | --- | --- |
| up-v2 | 8758 | 450 | 122 / 90 | (9,22)-(86,96) | 7px |
| down-v1 | 8731 | 472 | 152 / 111 | (12,22)-(83,99) | 4px |

输出SHA：up-v2=`fe631808c7cef27795fdae51daff0fae9ea98251b36356b855881062d6586a85`；down-v1=`e3af22f9bb6f9c9405ddc22b78badd1cf986658eb359e383ccec2de0acf0e2c0`。两图96×104 RGBA8、二值alpha、无越界不透明采样，冠顶y22；身体和表情与hold-half逐像素一致。两个生成donor在(72,65)各有一处额外不透明像素，属于翼区外重绘，遮罩明确丢弃并保留原头发像素，不是裁去翼尖。

幅度采用明确可复核的轮廓代理：左右外翼区域最外两列不透明像素的平均y，不声称为同一物理羽尖的精确点跟踪。原hold左右均93.222；up左右83.500/83.857；down均96.375。因此相对原姿态上移9.722/9.365px、下移3.153px；两端总行程12.875/12.518px，半行程约6.44/6.26px。**这不是围绕原姿态对称±4–6px，上扬实际超出该试样目标**。画布容得下且静态角度可辨，但是否仍符合用户所说中幅需PM确认；不偷偷称幅度达标，也不因有余量继续突破上扬2次上限。此处像素均为96×104/sourceScale1角色像素；高分辨率生成源按同比例提示。

### 实际验证和实看

以下命令实际执行，退出0：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art012-build.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art012-preview.py
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art012-up-v2-96.png
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art012-down-v1-96.png
git diff --check
```

Inspect-Png的System.Drawing独立读取确认两图96×104、RGBA8/color6、0半透明，哈希同上；结果 `art012-inspect-png.json`。构建报告保留原图SHA、转换、完整mask坐标、静止区差分、透明清除、翼尖量化、四边余量，以及正式包和ART011最终包前后SHA不变证明。实际查看 `art012-compare-light-1x.png`、dark-1x、light-3x、dark-3x，顺序原hold / 上扬v2 / 下压v1。角度在1×也可辨；未见明显矩形接缝、翅根断裂、旧翼双影或触边；头部和身体稳定。原始上扬v1的失败及幅度限制完整记录于 `art012-visual-review.json`。

### 交接

只交两端姿态和并排图；另提供自含PNG的 `art012-inspection.html` 供切换，制作方本轮以PNG实看，未运行该网页。没有新增manifest或扇动时序，没有实际宿主播放本试样，不称完整动画或动态验收。既有表情来源原样保留，未来经PM批准的完整循环再同步其他表情。当前先交PM判断实际幅度，必要时收敛方案须另行授权；不修改已验ART011来源或正式0.3.0，交付后停止。

## ART-013：中幅扇翼四项循环候选（2026-09-21）

### 范围和交付入口

PM接受f415df0两端作为循环制作基础，明确允许实际上扬约9–10px、下压约3px的不对称幅度进入动态评估。本卡使用既有来源和显式mask合成，imagegen调用0；只交 `source/art013-package/` 与 `art013-inspection.html` 及证据，仍为0.4.0候选。正式0.3.0、ART011/012来源、程序、锁文件不动，不进入随机漂浮。

最终包13张PNG、6动作。相对ART011只替换manifest的drag-hold内三个图片引用，其他manifest字节完整保留；pickup360ms、release460ms及原0.3.0三动作不变，原五PNG逐字节相同。中位图使用原hold-half，故pickup尾→hold首相同；release尾→idle-soft首仍为neutral。

hold四项均180ms、总720ms loop：`hold-half`（中位微笑）→ `hold-up-half`（上扬微笑）→ `hold-mid-closed`（中位闭眼笑）→ `hold-down-half`（下压微笑）→ 回首项。仅第三项闭眼，不在每个翼姿更换脸。上扬和下压PNG直接逐字节复制ART012已验两端；中位闭眼使用ART011 hold-half身体，仅在已验222像素眼口mask内采用0.3.0闭眼笑。

### mask与来源

`art013-build.py`记录各来源SHA。上扬/下压采用身体mask∪眼口mask∪翼部mask；中位闭眼采用身体∪眼口。三个组件互不相交，分别保留PNG；每张新图另存完整union-mask及坐标。旧pickup/release图附原ART011并集mask。所有8张非基线图从最终PNG读回检查，相对neutral并集外RGBA差分0。头冠、脸外轮廓、头发、中央躯干保持原像素；仅指定眼口和翼区动作变化。

上扬SHA仍fe631808c7cef27795fdae51daff0fae9ea98251b36356b855881062d6586a85，下压仍e3af22f9bb6f9c9405ddc22b78badd1cf986658eb359e383ccec2de0acf0e2c0。最终manifest SHA为 `6df3616190d43b977157d0a110f9b3a609599802baabf1118ae3b2107e102abf`。没有程序变形、平移、重绘或新生成。

### 实际验证

以下实际运行，全部退出0：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art013-build.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art013-preview.py
./assets/characters/aemeath-v1/source/art013-run-host.ps1
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art013-check.py
git diff --check
```

13图经Inspect-Png独立System.Drawing读取：96×104 RGBA8/color6、二值alpha、0半透明，最大8886字节，参考锚点(48,94)。引用、四项时长、原五图字节、首尾接续和mask检查通过；预览嵌入的13个PNG字节与最终包逐一一致。构建前后正式包和ART011源包SHA不变，Git禁止范围无差分。

实际自有宿主只定向重跑变化的hold：PID18784、exit0，显式manual/drag-hold、scale2、4200ms定时退出。生产加载器接受aemeath-v1/0.4.0、disabled=[]；真实frame日志覆盖索引0…3，去除相邻重复后包含5次3→0完整循环回绕，正常shutdown，无package-rejected/position-error。exe SHA E3951560B446CB708F97A928BA96940FD4B4B3182DC9FAA1C754C2ACF27113B0；运行记录的manifestSHA与当前包一致。证据 `art013-host-hold.jsonl`、host-run.json、png-inspect.json、check-report.json。不重复无关控制器测试；既有QA007控制器检查留给QA复用判断，不冒充本任务重新执行。

### 浏览器实看及发现

在本地 `http://127.0.0.1:8913/art013-inspection.html` 实际运行最终候选预览，浅深底1×/3×均可见。正常情境400ms按下，760ms进入hold，4000ms松手：实时DOM/截图在1048/2035/3132ms取样，到3132ms已完整经过3个hold周期；4611ms观察到回idle。此为实时运行与抽样截图，不是原生窗口录像或鼠标捕获验收。

逐时刻定位检查：上扬松手1039→1040ms、下压松手1399→1400ms；40ms快松手440ms进入release、900ms回idle；release期间再抓730ms回pickup neutral入口、810ms惊讶；hold360ms闭眼中位，719→720ms末项下压回首项中位。记录见 `art013-visual-review.json`。另实看 `art013-hold-light-3x.png` 并排四项，浅深1×/3×对照全部提供。

未见明显翅根断口、旧翼双影、头冠或躯干晃动。扇动比旧hold明显，但上扬→中位的角度变化比下压→中位硬；上扬时松手立即回固定release入口，约9–10px翼尖收回在并排/切换中明显，下压松手和循环首尾约3px变化较小。每720ms一次闭眼显得规律。**本轮格式、加载与静态接缝自检通过，不宣称动态自然度已通过。** 按卡保留四项180ms，不自行调整或无限修补。

### 最小调整提案（仅提案，未实施）

- 降低眨眼重复感可不画新图：改为8项×180ms=1440ms，两组中位→上扬→中位→下压，第一组中位保持半睁、第二组才闭眼；扇翼仍720ms一轮，眨眼1440ms一次。须PM授权项数变化。
- 固定release首图无法同时与两端翼姿完全一致；仅改时长不能消除上扬松手的9–10px瞬时回收。若PM不接受，需要另卡决定新增中间翼姿，或由统筹评估按当前翼相位选择release入口的表现接口；本ART卡不改控制器或自创接口。当前不增加新图、不作未授权变形。

交PM/QA时请用art013-package及最终互动预览，重点复核上扬松手与720ms眨眼节奏；前代候选只作来源。完成即停，不推广正式包，不进入随机漂浮、联动或发布。

## ART-014：单张中间翼姿（2026-09-21）

按PM在DEV006之后的任务卡，只补中位与原上扬之间的一张真实中间翼姿。使用imagegen技能1次、沿用ART012翼部mask一个版本；未耗用第二次生成。交付候选 `source/art014-v1-96.png`，身体和脸来自ART013 hold-half，原上扬参考为hold-up-half。没有新增动作包或调整时序。

原始生成文件exec-b5f88ca8-d1cd-4fd2-be73-b91eecb91305.png保留，副本为art014-v1-source.png，SHA256 `92aacc1a21e6805350c52ae0ba49f7c505b19b1bac76d589ca1d7a286d838703`。生成输入为neutral-generated-v3-edge-cleanup.png与art012-up-v2-source.png；完整提示词、转换donor、mask、逐像素mask坐标与来源SHA均随art014前缀文件交付。生成器重绘的其他区域不采用，只在已验1220像素翼部mask内替换RGBA。转换保持既有pixel-center nearest、96×104、alpha阈值128与全图整数偏移(0,+5)，没有以程序移动或拉伸翼部制造姿态。

最终PNG为96×104 RGBA8/color6，8803字节，二值alpha；SHA256 `939767e70b9634464a137004293a68d2df2c379220749ea01c893574c73cd9ec`。434个像素变化，mask外RGBA差分0，清除86个旧不透明像素、增加75个，转换截断不透明样本0，翼区新donor不透明点超出mask为0。包围盒(8,22)至(87,97)，参考锚点仍(48,94)。正式包和ART013包前后SHA完全相同。

翼尖代理沿用外侧两列不透明像素的平均y，不视为骨骼或同一物理点追踪：中位左右93.222，中间左右89.000，上扬左83.500/右83.857。故中位→中间上移4.222逻辑像素，中间→上扬左5.500/右5.143；中间外缘左右各比两端多伸出1像素。实际幅度接近目标4–5px，中间→上扬左侧略超过5px，保留该差异供PM判断，没有裁翼伪造数值。

已实看原始生成图，以及light/dark两底1×与3×四张并排图；均按中位→中间→原上扬排列。三个角度可以辨认，中间长羽接近水平，短羽保留下垂分叉；未见明显矩形接缝、翅根断口或旧翼双影，头发、表情和身体稳定。静态检查支持进入下一轮动态验证，不代表release跳变或完整hold自然度已经通过。

实际执行且退出0：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art014-build.py
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art014-v1-96.png
git diff --check
```

构建对候选PNG逐chunk验证CRC并解码回读RGBA；独立Inspect-Png/System.Drawing结果见art014-png-inspect.json，0半透明，SHA一致。art014-report.json保留量化与受保护文件SHA。未运行新姿态的应用动画；只交单图供PM决定下一卡如何用于release和hold，不实现三套release、全套包、两周期眨眼或idle/float，不推广正式素材。

## ART-015：B2/B7受限试样与失败证据（2026-09-21）

PM接受ART014为B4静态来源后，派单补B2/B7。使用内置imagegen，每张恰好2次，共4次；两张共用既有ART012翼mask的副本art015-mask-v1.png，仅一个版本。保持ART013 hold-half头/身体/表情；只在mask内采用生成翼像素，沿用既有nearest96×104、alpha128、全图整数(0,+5)格式转换，没有程序平移、扭曲翅膀造姿态。只增加art015前缀文件及本记录。

**结果有局限，达到次数上限即停止。** 两张第二版均过度修正，五级对照明确选首版作为当前较好试样，未宣称完全达到目标或可推广。B2-v1实际较中位上移3.222px，偏离约2px目标，且与B4仅差1px；B7-v1左/右上移6.555/6.822px，接近约7px目标。翼尖代理仍是外侧两列平均y，不是同一物理点追踪。

五级顺序中位→B2-v1→B4→B7-v1→原上扬；左侧相邻上移3.222/1.000/2.333/3.167px，右侧3.222/1.000/2.600/2.543px。轮廓代理方向单调，但严格≤3px检查为false。最终评估留给PM，不以四舍五入掩盖超限。B2-v2反而比中位低0.492/0.778px，且donor在旧mask外多出(24,81)/(71,81)两个不透明点；不扩mask修这张失败图。B7-v2较中位上移8.722px，与B4相差4.5px，太接近原上扬。所有失败源图、donor、合成图、并排图和提示词保留，不能误用v2。

交付入口为art015-b2-v1-96.png（8804B，SHA fa75d0a105183cf4f24208df965cd75b485efe92c54fe28b816a7f11131a0035）和art015-b7-v1-96.png（8726B，SHA 017cd78d9293cbe299c977175811ba2a426122a9a7043ccc5d8d7645f12d24da）。四张art015-five-{light,dark}-{1,3}x.png均已实看：长羽角度无明显反向、断根、矩形接缝或双影，头身脸不动；B2/B4差别在1×较小，B7右侧比左侧多伸1px，短羽底缘比B4高2px、到原上扬又低1px，有轮廓收放风险。未播放往返预览或原生应用，不把静态单调当成无抖动的动态验收。

两张选定v1分别变化415/456像素，mask外RGBA变化均0，转换不透明截断0，翼区新donor超mask点0。四次候选均96×104 RGBA8/color6、alpha0/255；CRC与RGBA回读通过。正式包、ART013整个包及ART014全部文件前后SHA相同。源图SHA、引用输入、生成文件名、完整提示词、donor、mask坐标、差分、逐项量测均在art015-report.json / art015-five-report.json / art015-visual-review.json及同前缀文件中。

实际执行，均exit0：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art015-build.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art015-compare.py
./assets/characters/aemeath-v1/source/art015-inspect.ps1
git diff --check
```

Inspect脚本对四次候选逐一调用独立Inspect-Png/System.Drawing，证据art015-png-inspect.json。格式检查通过不等于姿态目标全通过；按卡一并交付两张最佳试样及失败证据后停止。不改已有包、代码、正式素材，不制定hold时长、眨眼节奏、release入口或schema2，不进入漂浮/待机。

## ART-016：往返与收翼网页动态探针（2026-09-21）

按PM指定制作一次动态探针，imagegen与像素修改均0。入口art016-inspection.html，自含12张既有PNG，支持浅深底1×/3×、暂停、下一项、任意时间定位、六源图松手、40ms快松手、重抓及手动输入。所有图片逐字节与选定来源一致，无插值、淡化或整图平移掩盖差异；页面固定图片位置，只以坐标数值展示模拟输入冻结，不能当作真实窗口位置/捕获验收。没有写正式包或schema2。

每周期10项720ms严格按卡：中位80、B2-v1 50、B4 50、B7-v1 50、上扬100、B7 50、B4 50、B2 50、中位60、下压180。复制为1440ms20项，仅第19项采用原hold-mid-closed，其他half。六个收翼探针均源图40ms开始，再经剩余B图各40ms进入原R460；上扬/B7/B4/B2/下压/中位总时长分别620/580/540/500/500/500ms。页面内部数组只供视觉探针，不是共享接口或正式release入口表。40ms快松手明确使用旧R回退，未实现pickup源图选路；所有真实宿主源帧路由均未实现。

实际构建命令 `python.exe -B assets/characters/aemeath-v1/source/art016-preview.py` exit0；构建检查720/1440/460时长、闭眼唯一项、12张内嵌PNG与来源字节/SHA相同，正式包、ART013整个包、ART014/015全部文件前后SHA不变。报告art016-build-report.json。`git diff --check` exit0。没有重复执行未变宿主测试，也没有宣称新包加载通过。

实际在本地8916端口运行网页，重播hold后DOM在822ms与7930ms取样，8044ms暂停，已连续运行11个完整翼周期；对应截图864ms与7972ms展示浅深1×/3×。这是实时执行的抽样观察，不是逐帧录像。暂停定位480ms为第一周期中位，1200ms闭眼，下一项1260ms下压，2640ms再次闭眼，确认两周期一次60ms闭眼。

实际UI检查：上扬400ms源图、440ms B7、560ms R中位；B7的520/980ms、B4的480/940ms、B2和中位的440/900ms均分别进入R中位/结束neutral。下压400→440ms从源图到R中位，均冻结坐标(140,200)。快松手439ms仍pickup neutral、440ms为release-fallback hold-half、900ms结束，坐标冻结(144,200)；重抓479ms仍B7收翼，480ms立即pickup neutral，560ms惊讶，840ms进入hold。另点手动按下/松手，660ms release及9822ms idle-after-release坐标均为(138,200)。详art016-visual-review.json。

**本轮动态自评：不接受直接冻结。** 上扬逐级收翼改善原9–10px一次收回，头身稳定，采样实看未见明显断根或矩形缝。但B7短羽相对邻项仍有收放，右轮廓多伸1px；B2/B4差别小、下压停180ms，整体节奏不够均匀。闭眼60ms已执行，但稀疏截图不足以确认短时表情可读性，不以暂停清晰冒充实时自然。快松手固定R仍从neutral跳到hold-half，是明确标记的未实现源图选路，不计作该场景成功。

最小建议仅供PM判断：若允许下一次纯时序探针，可将下压180减40至140，回中位60加40至100，第二周期同项闭眼100，维持720ms。该调整只可能改善停顿和短促闭眼，不能修复短羽像素形变；本轮未实施、不再生成。当前交探针与失败结论即停，待PM决定，不冻结共享契约、不进入随机漂浮/日常待机。

## ART-017：保留高位，局部修复B7轮廓（2026-09-21）

用户选择保留放下时的大幅上扬方向；本卡仅修B7，不将B4替代高位，也不从任意低位松手强切上扬。使用内置imagegen技能1次、显式mask1版，交art017-v1-96.png作为局部改善候选。原B4和ART012 up-v2高位完全不动，不耗用第二次生成、不重排hold/release。

编辑输入为旧B7的art015-b7-v1-source.png，B4和高位源图仅供短羽长度/分叉参考。原始exec-a1aedc80-bd56-47e0-8eeb-64d140e00e9d.png保留，副本art017-v1-source.png，SHA `005312bd824ea0003a1c8679773561dbfa0d057327bee781c7dafeb27dcf6041`；完整提示词art017-v1-prompt.txt。按原nearest96×104、alpha128、全图整数偏移(0,+5)转换成donor，再局部合成旧B7身体/表情，未程序拉伸/旋转/平移羽翼造姿态。

mask为原ART012翼mask的子集：左侧保留x≤23，以及y≥93时x24..26，右侧镜像；因此内侧羽毛/翼根x24..30上部及x27..30下部不采用生成结果。完整坐标和SHA见art017-report.json。donor在固定内侧羽区(68,92)有一个额外不透明点未采用，保留旧B7原像素；无翼尖截断，不扩大mask。最终mask外RGBA变化0，278像素变化，清除19/增加22不透明像素，转换不透明截断0。

候选96×104 RGBA8/color6，8766B，alpha0/255；SHA `8cac356f170275806966d31364520c3bbc5ad3a66e04160ed59814dd4ab9557b`。包围盒(8,22)..(87,97)，参考锚点(48,94)。原正式包、ART013整个包、ART014/015/016全部文件前后SHA不变。

轮廓代理显示改善：短羽下部ROI底缘B4/旧B7/新B7/高位分别97/95/97/96，左右一致；同ROI不透明点58/46/52/48，旧B7的收缩后回涨变为逐级减少。外缘分别8..87 / 8..88 / 8..87 / 9..86，旧右侧多伸1px已消除。此为下部轮廓代理，不是解剖羽长或同一点追踪。新B7外翼尖均值左86.714/右87.000，到高位仍差3.214/3.143px，不宣称≤3，也不为数值继续修绘。

实际查看原生成图和四张art017-v1-compare-{light,dark}-{1,3}x.png，顺序B4/旧B7/新B7/高位。网页art017-inspection.html自含4张来源字节，旧/新同步B4→B7→高位→B7往返，浅深1×3×同时展示；没有位移、插值、淡化。实际运行各120ms观察档，1492ms DOM/1528ms截图已往返3次；暂停120/240/360ms逐项观察B7上行、高位、B7回程。再运行原片段50/50/100/50ms档，1392ms DOM/1427ms截图已5次，1523ms暂停为6次往返。只是局部网页片段，不是完整hold/release或原生播放验收。

本轮自评为**局部改善，可以交PM复核**：新B7短羽的缩短突变比旧版弱，分叉保持，左右宽度协调；实看未见明显断根、旧翼双影或矩形mask接缝，头饰/脸/身体稳定。仍有羽片颜色/形状差异，高位两侧各收窄1px；不宣称完全无抖动或完整动作已通过。证据是实时运行的抽样截图及暂停对照，不是逐帧录像。

实际命令均exit0：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art017-build.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art017-preview.py
./scripts/qa/Inspect-Png.ps1 -Path assets/characters/aemeath-v1/source/art017-v1-96.png
git diff --check
```

CRC/RGBA回读、独立Inspect-Png格式/alpha/SHA检查、静止区差分、内嵌来源字节和保护文件SHA通过，报告见art017-report.json / contour-report.json / png-inspect.json / visual-review.json。只提交art017前缀和本记录，直接回PM后停止；未修改任何历史或正式候选包、共享schema、程序，不制作待机/漂浮。

## ART-018：完整动态探针复验（2026-09-21）

按卡一次更新ART016完整网页探针，入口art018-inspection.html。全局B7图片绑定换成ART017新图，hold及全部收翼引用均使用该绑定。每周期回中位100ms、下压140ms，其余项保持；20项1440ms，第二周期第19项闭眼100ms，保留原高位。imagegen0、像素修改0，无额外调参迭代。

`art018-preview.py`与`art018-check.py`实际执行exit0，`git diff --check` exit0。检查从最终HTML回读：12张内嵌PNG逐字节/SHA与指定来源一致，唯一图片绑定变化为B7；相对ART016只有hold零基索引8/9/18/19时长改成100/140/100/140，pickup/R及六收翼探针数组不变。正式包、ART013包、ART014至017源文件前后SHA相同。最终网页SHA `f53b38a87ff642842638a01621ac06de74fb9383da69ec106453b5d2a4c8f4a2`，证据art018-build-report.json和art018-check-report.json。

实际浅深底1×/3×同时播放完整hold，重播后1280ms DOM仍closed，第一次截图1330ms已到down；继续到3656ms DOM/3698ms截图完整5翼周期，3776ms暂停。为明确100ms闭眼能否实看，另直接抽取实时截图1268ms，状态为播放/closed，第19项，四种底色倍率均能辨认闭眼笑；未通过延长或暂停伪造时长。该补充抽样没有改参数。实时截图是抽样证据，不是连续录像。

上扬松手440ms暂停显示新B7，位置数值(140,200)已冻结；下压400→440ms从down直接回R中位，没有硬切高位。上扬实时1143ms、下压919ms均已结束neutral。快松手439ms pickup neutral→440ms明确release-fallback mid→900ms neutral；重抓479ms仍新B7收翼→480ms立即pickup neutral→560ms惊讶→840ms hold。保留真实源帧路由未实施标识；窗口位置冻结只是数值模拟，快松手仍为固定R回退，不冒充源帧选路已完成。

**本轮制作方结论：完整视觉探针可交独立QA，未发现实际1×尺寸下阻断性的短羽突缩。** 新B7的短羽分叉较连贯，100ms闭眼已实时可见，头身和翅根采样中稳定；细微形色变化、高位两侧收窄1px、邻段像素步幅不均仍保留披露，不宣称完全无形变或严格≤3px。没有据此冻结素材/DEV契约，也不是原生桌宠动态验收。

详细观察见art018-visual-review.json。自有测试页和8918服务器已关闭。只交source/art018-*及本记录，完成这一轮即停，后续由独立QA检查完整探针、PM统一决定；不改正式包/schema/程序，不做idle/float。

## ART-019：ADR004 schema2真实候选包（2026-09-21）

依PM22799b4冻结的ADR004制包，已只读读取现行ADR并原样保存为art019-frozen-adr.md，SHA记录于art019-source-report.json。该契约优先于旧探针限制。候选为source/art019-package，schemaVersion2/packageVersion0.4.0；未覆盖正式包，不合并本分支历史0.2。imagegen0、像素修改0。

保留ART013全部13张PNG逐字节不变，新增hold-bridge-low/mid/high分别逐字节来自ART015 B2-v1、ART014 B4、ART017新B7，总16图。已与PM工作区正式0.3.0实物比较：五张基线PNG和neutral/idle-soft/idle-smile三个动作一致；pickup和基础release保持ART013。所有原始文件路径/SHA/字节数随source-report交付。

hold按冻结表20项1440ms，第二周期唯一closed100ms。drag-release.entrySequences完整覆盖16个源PNG，首项path等于键、末项neutral；上扬620，H580/M540/L500，中位直接R460，下压500，闭眼中位460，两张惊讶500，neutral160，release-closed380，release-half280，四个idle表情/轻浮源各200。基础41项、入口63项、共104项。中位没有继承探针的额外40ms，低位源不先切高位。

最终manifest SHA `eab91ecb10037da7320d4e9c9321c8dce0f122d3b9d5daa6e101a55e1e319da3`。文件检查从最终manifest读回，检查重复键、schema/元数据、路径/字段/正整数时长、16图来源字节、PNG CRC/96×104/RGBA8/二值alpha、图与项数量及上限、全部入口精确顺序和时长、首尾、每条期限前1ms/边界、pickup末→hold首和R末→idle首。期限检查为文件级数组检查，不是生产播放器测试。正式包、ART013源包及PM正式0.3实物前后SHA不变。

实际命令全部exit0：

```powershell
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art019-build.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art019-check.py
& C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe -B assets/characters/aemeath-v1/source/art019-preview.py
git diff --check
```

art019-inspection.html从最终候选读取manifest和16图内嵌，回读确认manifest对象与图片字节一致。浅深1×3×同时预览，可选六动作或任一源入口，暂停逐项和时间定位。实际运行hold：1287ms截图可见闭眼，3704ms DOM/3759ms截图已完整5翼周期。抽查中位0/459/460ms、neutral0/159/160ms、闭眼中位0/79/80/460ms、高位0/40/620ms、下压0/40/500ms均显示预期首图/下一项/到期结束。实看未发现相对已验ART018新增的角色像素变化；旧细微形变限制继续保留。证据check-report、preview-report、visual-review；网页SHA `7be3ccf7ea573f471c83bbd306359cbcbc97d57468ffea4c6ba51dab60ced3f4`。

网页播放是数组展示，不是宿主按已提交帧自动选路。此任务未运行schema2生产加载器，不用旧加载器失败冒充成功；真实加载、控制器、快照/捕获和原生视觉交DEV007/QA。候选就绪直接向PM和DEV提供路径、提交和manifestSHA；自有8919测试页/服务器关闭。仅art019前缀及本记录，完成即停，不改正式素材/代码/锁，不进入漂浮、日常待机或发布。

## ART-020：普通idle-soft翅尾只读诊断（2026-09-22）

用户原生验收报告待机翅尾像素断裂、其他正常；其他项仅作为用户报告，不扩展为代理原生实测。按卡只读PM正式0.4 neutral/soft-light/soft-peak，未检查或修drag-hold，imagegen0/像素修改0。

已定位soft-light左(20,92)/(20,93)、右(75,92)/(75,93)为RGBA0，而neutral与soft-peak同位置均不透明；soft-peak另有右(76,90)透明、左镜像无同孔。缺口已存在于历史donor，并由ART009/ART008直接RGBA合成沿用；只读重建和正式图逐像素一致。light左侧为4邻接两像素孔，右侧为开放细缺口；三帧均未发现8邻接独立翅尾块，不能说整片羽翼脱落。mask左x≤23/右x≥72的硬边界另造成(24,91)/(71,91)源图近白亮部未采用、保留neutral暗部，可能加强重接感，非透明孔的唯一根因。

证据和最小修复范围见source/art020-diagnosis.md、pixel-report.json、alpha-map.txt、inspection.html。预览仅原PNG内嵌/CSS放大，已实看全图1×3×和翅尾10×以及原时序浅深底播放，484ms截图为light。未取得用户指向点位的原生截图，不声称覆盖全部主观现象。建议后续卡仅soft-light/soft-peak，局部左x18..26/y89..97及右镜像x69..77/y89..97，保护正常分叉负空间，修细连接与mask交界；不盲填所有透明孔，不改neutral/时序/其他动作/代码。

实际art020-diagnose.py和git diff --check退出0；CRC、三来源与ART019字节一致、历史mask重建、mask外差分、连通分量和内嵌字节检查完成，正式包前后SHA不变。没有生成新PNG、改正式素材或实施修复。交PM定位后停，自动跟进保持暂停，不进入漂浮。

## ART-021：idle-soft翅尾局部修复候选（2026-09-22）

依据PM最新卡，仅以正式0.4 soft-light/soft-peak为底，修许可窗口内连接和接缝。每帧imagegen1次、mask2版，最终为art021-soft-light-v1-m2-96.png与art021-soft-peak-v1-m2-96.png。生成整图经最近邻/alpha128与既有(0,+5)配准后，仅显式mask复制生成RGBA；没有程序绘补丁。初始未配准和宽mask失败证据保留，均不是候选。

最终light33像素/peak30像素RGBA改变，窗口外0；alpha仅补已知4+1点，原实心不减少，其他透明空隙全部不变，始终一个8邻接分量。96×104 RGBA8二值alpha、bbox/头冠/脚/anchor保持，正式17文件SHA不变。原速1400ms浅深1×2×3×及局部10×实看，已知透背景缺口未再闪现；局部暗色连接点仍可辨，不能宣称全消主观接缝。浏览器播放截图28445ms light、28729ms peak，非原生验收。

实际art021-build.py/check.py/preview.py、两张Inspect-Png.ps1及git diff --check退出0。原始源、prompt、donor、两版mask、SHA、diff、preview和失败证据均在source/art021-*；完整命令/限制/选定SHA见art021-delivery.md。仅交独立QA和PM决定；没有改正式包/其他动作/entry/代码/锁，不整包合并ART历史资产，不进入float。
