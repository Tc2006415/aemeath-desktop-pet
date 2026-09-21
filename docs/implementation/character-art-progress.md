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
