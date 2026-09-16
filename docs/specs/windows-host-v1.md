# Windows 单屏诊断宿主 v1（候选实施规格）

状态：DEV-002 v1.1 修订，待 PM 接受；2026-09-16，关联 Issue #1。本文是工程规格，不是任务卡副本，也不是已实现软件。接口与 SDK 固定值须由 PM 合并接受后生效；本轮未安装、构建、运行或打包。

## 1. 已确定范围与输入

运行方向已由用户确定为独立 Windows 桌宠。PM 基线 `bf673927d3d88a6da071bfe49c3ec1aaa4fadb2b` 的 ADR 0001 已接受方向；本地未合并该分支。推荐唯一实现路径：Windows 11 x64、C#、WPF、.NET 10。首个小样只验证透明窗口、两个循环片段和一个单次片段、单屏拖动、整数物理像素倍率、可发现的键盘退出和自包含目录包。

持久化、完整跨屏/热拔插恢复、逐像素穿透、托盘、开机启动、真实 Codex 数据、全部角色动作和公开分发不纳入本小样。小样不等于完整 M2 或日常可用桌宠。框架选择不再全面比较。

固定输入及使用方式：

| 输入 | 核对小节及约束 |
| --- | --- |
| DEV `02626be7ab5ec947e702a9d85612e91045959e93`，desktop-runtime.md | 「跨提案依赖核对」C1–C5；保留单轮终态、最新状态恢复原则；本轮 PM 输入收窄窗口验证范围 |
| ART `d54730bfde5fc666f93e3f3a4ce96298b8f946cb`，animation-spec.md | 第 3/5/6 节的固定画布、锚点、毫秒时间、中断和坏素材回退；1.1–1.2 节的观察/改编边界不作为诊断帧依据 |
| INT `4782cd5c5fd7d5c18a96526a89e8767caf080896`，codex-integration.md | 「INT-001：跨提案核对与 PM 冻结项」「顺序、去重与过期」；唯一状态归约器与表现层分离，未知不猜成功 |
| QA `841021ebd13cbfbb4fe85c05f8a20f80b338160f`，acceptance-matrix.md | A02–A04/A14/A15、W01–W03/W08/W09/W11 中适用部分；本文提出单屏小样门槛，不把完整多屏/发布矩阵标为通过 |

v1.1 按 PM 集成裁决，以以下固定规格替代上表旧提案中的素材/状态候选；其余专业输入保留作追溯。这里只收敛宿主消费方式，不修改 ART/INT 文件，也不宣称公共接口已完成冻结：

- [ART animation-assets-v1.md @ ce81a521e6058cca3e50603b9a3b327dc7fcbbbd](https://github.com/Tc2006415/aemeath-desktop-pet/blob/ce81a521e6058cca3e50603b9a3b327dc7fcbbbd/docs/specs/animation-assets-v1.md)：第 1–3 节为格式/动作唯一来源，第 4 节为播放语义，第 5 节为资源上限及降级策略。
- [INT task-state-v1.md @ 807fffd8f8d6f665fe6f734d00dd8ad7f36b42d4](https://github.com/Tc2006415/aemeath-desktop-pet/blob/807fffd8f8d6f665fe6f734d00dd8ad7f36b42d4/docs/specs/task-state-v1.md)：第 1 节为时间语义，第 4 节为唯一归约器调用及 View，第 6 节为后续模拟验证向量。

## 2. SDK 与只读工具链证据

推荐 **SDK 10.0.401，win-x64**，目标框架 `net10.0-windows`，运行时 RID `win-x64`。2026-09-16 读取 Microsoft [10.0 发布元数据](https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json) 得到：latest-sdk=10.0.401、latest-release=10.0.12、发布日期 2026-09-08、active/LTS、EOL 2028-11-14；对应 x64 ZIP 条目实际存在。不是仅依据主版本猜测 SDK 号。官方[支持政策](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core)要求跟进修补；此版本是本次可复现起点，后续安全更新由 PM 更新基线。

实际检查：`Get-Command dotnet -All -ErrorAction SilentlyContinue` 无命中；`Test-Path` 对以下四个 dotnet.exe 均为 False：`C:/Program Files/dotnet`、`C:/Program Files (x86)/dotnet`、`$env:USERPROFILE/.dotnet`、`$env:LOCALAPPDATA/Microsoft/dotnet`。限定为这些探测范围内**未发现安装**，不是证明整机没有自定义 SDK，更不是 build 失败。`Get-CimInstance Win32_OperatingSystem` 返回 Windows 11 家庭版中文版、10.0.26200、64 位；本轮未核查 Windows 更新状态和全部可选组件。

推荐用户级部署：官方 SDK ZIP 校验后解压到 `%LOCALAPPDATA%/Aemeath/toolchains/dotnet/10.0.401`；仅使用绝对路径调用 dotnet，不修改系统/用户 PATH，不复用 Codex 安装目录。SDK 包含桌面运行时；官方[Windows 安装说明](https://learn.microsoft.com/en-us/dotnet/core/install/windows)支持手动部署。手动 ZIP 不自动配置 OS 前置依赖或持续更新，实际 `--info`/restore/build 结果仍是开工门槛；缺依赖时记录明确错误，不改成另一个框架。

以下为**后续获派实现任务后才执行**的部署例子，本轮只核查语法。目录已存在时停止以免覆盖；下载/磁盘/网络失败须记录，不绕过校验。SHA512 来自官方元数据，不是本轮已下载包的计算结果。

```powershell
$sdkVersion = '10.0.401'
$sdkDir = Join-Path $env:LOCALAPPDATA "Aemeath/toolchains/dotnet/$sdkVersion"
$sdkZip = Join-Path $env:TEMP "aemeath-dotnet-$sdkVersion-win-x64.zip"
if (Test-Path -LiteralPath $sdkDir) { throw 'SDK directory exists; inspect before reuse' }
$metadata = Invoke-RestMethod 'https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json'
$sdk = @($metadata.releases | ForEach-Object { $_.sdks } | Where-Object { $_.version -eq $sdkVersion })
if ($sdk.Count -ne 1) { throw 'SDK version missing or ambiguous' }
$archive = @($sdk[0].files | Where-Object { $_.rid -eq 'win-x64' -and $_.name -like '*.zip' })
if ($archive.Count -ne 1) { throw 'Archive missing or ambiguous' }
Invoke-WebRequest $archive[0].url -OutFile $sdkZip
if ((Get-FileHash -LiteralPath $sdkZip -Algorithm SHA512).Hash -ne $archive[0].hash) { throw 'SHA512 mismatch' }
Expand-Archive -LiteralPath $sdkZip -DestinationPath $sdkDir
$dotnetExe = Join-Path $sdkDir 'dotnet.exe'
& $dotnetExe --info
if ($LASTEXITCODE -ne 0) { throw 'SDK probe failed' }
& $dotnetExe --list-sdks
& $dotnetExe --list-runtimes
```

验收应看到 SDK 10.0.401、x64 和 Microsoft.WindowsDesktop.App 10.0.12；存在 exe 但 probe 非零才称“SDK 验证失败”。网络 restore 失败、编译失败和真机运行失败各自分类。为可复现构建，后续工程根 `global.json` 候选如下，不允许静默选预览或别的 SDK：

```json
{"sdk":{"version":"10.0.401","rollForward":"disable","allowPrerelease":false}}
```

## 3. 模块和唯一状态归约边界

建议后续目录（此轮均不创建）：`src/Aemeath.Host/` 放 WPF App、PetWindow、DiagnosticWindow、WindowsInterop、DpiGeometry；`src/Aemeath.Presentation/` 放无 WPF 依赖的播放器/表现协调/素材验证模型；`src/Aemeath.State/` 由联动任务维护唯一归约器；`tests/Aemeath.Presentation.Tests/` 放真实行为单测；`assets/diagnostic/` 放明确标记的合成测试 PNG。不引入 DI 框架、渲染库或第三方托盘库。共享模型存放位置由 PM 与 INT-002 统一，不在两项目各复制一份。

| 责任 | 输入与输出候选 | 唯一职责 / 禁止重复 |
| --- | --- | --- |
| 宿主（程序） | HWND、屏幕物理位置、鼠标、DPI；输出 DragStarted/Ended/Cancelled、缩放请求；消费当前帧 | 管窗口/捕获/坐标/生命周期，集中 UI Dispatcher 调度；不解释外部状态事件 |
| 播放器（程序） | Play(clip, playbackId, monotonicNow)、Sample(now)、Cancel(playbackId)；输出 frameIndex 和一次性 ClipEnded(playbackId) | 只计算片段时间与帧，不判断业务状态、有效期或完成事实；过时 playbackId 的结束回调不能复活旧动作 |
| 表现协调（程序） | 最新不可变展示快照、交互事件、ClipEnded；输出 Play/Cancel 和标签 | 决定拖动覆盖、片段映射及何时请求消费提示；不建立事件去重表、不计算第二套 TTL、不保存按下前业务状态用于恢复 |
| 唯一状态归约器（联动） | INT-002 归一化模拟事件与共享单调时钟；输出 View | 独占身份、轮次、顺序、bindingId 代次、有效性、提示资格及消费记录；无 HWND/帧名/DPI。此版只有 mock/none，不新增 real 入口 |

唯一进程内归约接口采用 INT 第 4 节：`BindMock(sourceId, taskId, now)`、`Unbind(now)`、`Receive(handle, event, now)`、`Disconnect(handle, now)`、`SuspendOrResume(now)`、`Read(now)`、`TryStartPrompt(token, startFrame, now)`、`EndPrompt(token, outcome, now)`。宿主消费该节完整 View，不增加修订号、另一份事件 JSON 或自定义消费接口。归约器返回的 sourceKind、state/reason、baseVisual、prompt、nextDeadlineMonoMs 和 needsBaseline 直接决定标签、播放资格、唤醒与重绑定流程；播放器不接触业务身份。

所有调用和表现切换串行到同一 Dispatcher，使用 INT 的非递减单调毫秒 now。渲染前先 `Read(now)`，同时按 View.nextDeadlineMonoMs 安排独立唤醒，不能只依赖渲染或片段结束检查到期。暂停/恢复先 `SuspendOrResume(now)` 再绘制，不恢复旧基线。宿主不自行计算 TTL。

仅在 normal、提示夹具就绪时调用 `TryStartPrompt`。归约器先核资格，再同步调用 startFrame；回调不得 await、阻塞或重入归约器，只提交预载首帧并返回 boolean。**true 后归约器才消费并转 playing；false 或失败不消费**，失败必须保证未提交首帧。资格保留到原截止时间，不忙循环重试。启动表示首帧交给播放器，不以显示器扫描为判断。自然结束调用 `EndPrompt(token, finished, now)`；拖动/素材/窗口中断调用 interrupted。任何新 View 不再包含原 playing token 时立即停旧提示；旧 playbackId/token 回调不覆盖新状态，已消费提示不补播。

按 INT 第 1 节，提示资格为首次合法终态 transition 起 5000 ms，恰到期撤销资格并停止提示；这**不是状态标识期限**。提示结束或到期后回 neutral，仍有效的 completed/failed 标识继续保留到新合法状态或业务失效。业务 30000 ms 与链路 15000 ms 的起点、续期、等号优先级全由 INT 归约器管理；宿主只读 View/截止时间，heartbeat 不续业务、重复不续期限。completed 文案为“本轮正常结束”，不表示项目成功；这些是模拟契约，不承诺真实来源。

最早的纯窗口步骤可只提供明确标记“诊断输入”的不可变快照替身以验证播放，不实现一套简化 TTL/去重；涉及模拟 completed、过期、重复等状态门槛时必须改用同一联动归约器。替身通过不算状态协议通过。

## 4. 三片段诊断素材与表现

诊断素材全部为测试夹具、无角色形象。外部包只采用 ART 第 1–3 节：根 manifest.json 与 frames/，96×104、1×、8-bit RGBA 静态 PNG、锚点 (48,94)、alpha 仅 0/255 且每帧非全透明；诊断包 packageKind=diagnostic、全部 origin=diagnostic，宿主常驻“诊断素材”。正式动作枚举仅 neutral、idle-soft、idle-smile、drag-pickup、drag-hold、drag-release，不增加别名或任务动作 ID。最早单屏窗口只需以下三条；两个 loop 中 neutral 是静态单帧，不能要求它持续换帧：

| 诊断片段 | 帧/时长 ms | 用途 |
| --- | --- | --- |
| neutral | loop，必须 1 帧；1000 | 静态回退；未知或缺任务动作时搭配明确状态文字，不表示业务 idle |
| idle-soft | loop，示例 2 帧；400、200 | 显式诊断循环选择；用于拖动过程中验证非阻塞播放 |
| idle-smile | once，示例 2 帧；300、200 | 显式诊断单次选择，500 ms 后结束；不是成功提示 |

上述时序沿用 ART 第 6 节示例的前三条，共 5 个时序项，可复用同三张诊断 PNG；不是独立包格式或角色动作预算。最早纯窗口允许无完整拖动三段：保留显式选择的 idle-soft 诊断循环以观察拖动不断帧，松手解除覆盖；没有任务动作时 neutral+状态标识，绝不把 idle-smile 隐式映射为 completed/failed。进入第一角色包及模拟交互验收时接入完整 pickup→hold→release；时长来自当前 manifest，不硬编码 460 ms，release 结束再 `Read(now)`，快速松手/重新抓取可中断。缺失或停用 release 时收到不可播放结果就立即结束覆盖并 Read，不等待不存在的结束通知。

提示动作的原子开始/中断验证使用**显式注入播放器的内存诊断夹具**，入口和画面均标“诊断提示测试”；不写入外部 manifest、不扩展六动作枚举、不复用 idle-smile 为成功动作。无该注入夹具时只显示 neutral+业务标签，不调用 TryStartPrompt 消费资格。夹具仍遵守 ART 尺寸、时间范围和 once 结束规则；其存在仅支持提示协议测试，不代表角色已有任务动画。

播放器完全采用 ART 第 4 节：以 Stopwatch 单调时间及累计时长定位半开帧区间，loop 取周期余数；once 到总时长立即结束、回 neutral、仅一次自然结束通知，不持续停末帧。同调度的新请求可替代 neutral，无需强制闪一帧中性；被请求替换/取消的实例不再报告自然结束。不可播放请求报告一次明确失败并回 neutral，不伪装自然结束。采用 CompositionTarget.Rendering 驱动采样，不以回调次数计时、不 sleep UI 线程；重复渲染时间不推进第二次，长间隔直接跳到当前帧，不堆积补播。关闭时解绑静态事件。失焦继续计时；最小化后恢复也不高速补播。API 存在见 [Rendering 文档](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.compositiontarget.rendering?view=windowsdesktop-10.0)，持续拖动流畅性仍需实测。

## 5. 窗口、物理像素与拖动

PetWindow 推荐 `WindowStyle=None`、`AllowsTransparency=true`、透明背景、`ResizeMode=NoResize`、不在任务栏单独显示；不全屏、不设置全窗鼠标忽略。WPF 透明窗口约束见 [AllowsTransparency](https://learn.microsoft.com/en-us/dotnet/api/system.windows.window.allowstransparency?view=windowsdesktop-10.0)。诊断窗正常显示于任务栏并始终可恢复；不依赖托盘发现退出。是否置顶以诊断开关控制，默认关闭。

通过应用 manifest 在创建 HWND 前声明 PerMonitorV2，不能在窗口创建后补设；推荐方式有[官方说明](https://learn.microsoft.com/en-us/windows/win32/hidpi/setting-the-default-dpi-awareness-for-a-process)。此声明不代表本阶段已支持多屏。初始化后用 [GetDpiForWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getdpiforwindow) 读取实际 DPI；无效 HWND 返回 0 时停止定位并报错，不用 96 掩盖失败。

唯一坐标约定：

- 源像素 S：固定帧格与锚点。物理屏幕像素 P：Win32 cursor/window/work-area 坐标，可为负数。局部 WPF DIP D：仅用于画布布局。变量/模型以 SourcePx、ScreenPx、Dip 后缀区分，不用无单位 Point 穿过宿主边界。
- 整数显示倍率 k 默认为 2，可切 1/2/3；物理大小为 `(W*k,H*k)`，布局 DIP 为 `(W*k*96/dpiX,H*k*96/dpiY)`，锚点亦同。图像最近邻采样，显式设置尺寸，不使用 PNG 元数据 DPI 来决定大小；不增加二次 LayoutTransform 缩放。像素网格原点贴齐物理像素，不对单个源像素做 DIP 整数舍入。
- 例：96×104、k=2、DPI=144 时，物理窗口 192×208，WPF 布局 128×138.6667 DIP；锚点物理 (96,188)，局部 DIP (64,125.3333)。DPI=120 时布局为 153.6×166.4 DIP，物理大小仍 192×208。不对全局屏幕坐标直接除 DPI，因为多显示器原点不共用此换算。
- 初始用主显示器物理工作区居中，窗口物理原点取整数；由宿主统一通过 SetWindowPos 管理顶层物理位置（移动时 NOACTIVATE/NOZORDER/NOSIZE），WPF 只管上述局部尺寸。不要同时更新 Left/Top 又移动 HWND。窗口无非客户边框仍须记录 GetWindowRect 和 ClientToScreen 的实际偏差，不能假设永远为零。

拖动采用鼠标捕获＋非阻塞 MouseMove 更新，不使用原生 DragMove 模态移动循环，以便明确观察动画继续。按下时读取全局物理 cursor `c0`、窗口物理左上 `o0`，保存 `grabOffset=c0-o0`；CaptureMouse 返回 false 则不进入 dragging。后续位置 `o=cursor-grabOffset`；帧的透明包围盒、锚点和业务状态变化均不改写 offset。源锚点是绘图对齐依据，不是强制吸附鼠标的位置。Win32 定位失败时取消捕获并在控制窗报告错误，不持续忙重试。[CaptureMouse](https://learn.microsoft.com/en-us/dotnet/api/system.windows.uielement.capturemouse?view=windowsdesktop-10.0)、[SetWindowPos](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos) 提供 API 依据。

正常松手、LostMouseCapture、应用停用取消、Escape（窗口有焦点时）和退出统一走幂等 EndDrag：清拖动标记→释放捕获→重新协调最新状态。结束路径允许重复调用，避免 LostMouseCapture 再入两次播放。倍率变更时先取消拖动，缩放围绕固定源锚点再夹入工作区，不在拖动中改变 grabOffset。

本小样限制到启动主显示器工作区，拖动计算结果夹取到该工作区；到边缘停止跟随属于边界约束，不计为漂移。窗口大于工作区则降低 k，1×仍放不下时报告不支持并保留控制窗。运行中 DPI/显示拓扑变化先取消拖动、暂停定位、重新读取主屏和当前窗口 DPI、按物理大小重新布局并移回可见区域；不能取得稳定参数时停止 PetWindow 运动并提示重启。此兜底只保证可退出，不宣称平滑跨屏支持。

允许紧凑矩形交互面，不声明逐像素穿透。WPF 层可设置透明背景根面承接命中，但系统合成/透明区域的实际命中效果必须实测：分别在可见测试块、帧内透明留白、矩形外点击底层测试窗口，记录被拦截面积和可抓取位置；不能用 WPF IsHitTestVisible 属性推断 OS 点击行为。小样只要求可见区域可拖动、矩形外不阻挡，记录矩形内边缘影响；不为实现矩形命中给所有透明像素偷偷填不透明底色。

## 6. 生命周期、坏素材与退出

DiagnosticWindow 在启动时显示，标题“爱弥斯宿主诊断（模拟/未连接）”，进入任务栏/Alt+Tab；提供命名清楚、Tab 可达的“退出”按钮（AccessText `_退出` 不作为唯一键盘路径），显式 Alt+X 命令，标准 Alt+F4/关闭按钮。控件用 AutomationProperties.Name 提供名称；提供当前来源/状态、当前 clip/frame、DPI/倍率、素材错误、重新居中按钮。诊断指标只包含合成标识和本应用坐标，默认不写日志或记录桌面内容。

关闭 DiagnosticWindow 即调用统一 Shutdown，先取消拖动和定时/渲染订阅、释放图像/事件资源，再关闭 PetWindow 与控制窗、退出进程；不采用关闭后隐藏。关闭 PetWindow 同样结束整个应用。没有成功加载素材也要先打开控制窗并保留退出入口；不出现只剩一个透明进程的失败方式。控制窗最小化仍可通过任务栏恢复。键盘退出、讲述人标签必须实际 Windows 检查，不能只做静态 XAML 判断。

加载发生在可交互控制窗建立后，先完成 ART 第 1/2/5 节的全包校验和帧分类再启用，不创建第二套宿主上限。路径使用 ART 完整正则与保留设备名限制，规范化目录边界校验，拒绝包根/frames/文件的 reparse point；不跟随外部链接、扫描目录或加载未引用图片。manifest 字段白名单、重复键、版本、动作枚举、playback/origin、固定尺寸/锚点及 durationMs 规则原样消费。

资源上限唯一来源为 ART 第 5 节：manifest 64 KiB/深度8；动作最多6；单动作/全包时序项64/256；不同图片128；单PNG 256 KiB、全部引用文件8 MiB；每图96×104，原始RGBA最多5,111,808 bytes（不等于进程内存预算）；单帧1–10000 ms、单动作累计最多60000 ms。重复文件缓存复用，累计数值采用受检整数算术。这是引用摘要，发生修订时以 PM 接受的 ART 版本同步，不允许宿主自行放宽。

预载到内存、按需 Freeze 图像，释放文件句柄，播放期间不做磁盘读取。按 ART 区分：元数据/路径/资源限额错误或 neutral 缺失、非单帧、坏帧等拒绝整包；非neutral坏PNG则停用**所有引用该帧的整条动作**，其他有效动作可播放，包标降级，不跳帧/改时长。缺失/停用动作请求回有效 neutral 并报告不可播放，不假装动作完成；第一角色包必须六动作均有效，降级预览不满足交付。

新包拒绝时保留已有有效旧包并报告切换失败；首次加载无有效旧包则隐藏 PetWindow、保留独立控制窗错误和退出，不从其他动作抽帧假装 neutral。只在显式重载时重试。素材错误独立于业务状态，不将它映射为 failed 或擅自改 unknown；来源未连接时本身就是 unknown。错误不触发提示消费；正在播放的提示若因素材中断，停止并 EndPrompt(interrupted)。错误类别受限，不在标签展示堆栈、私人路径或包外内容。

## 7. 后续开工步骤与命令（本轮未执行）

1. PM 接受本规格并与 ART/INT/QA 候选汇合，派发工程范围。按第 2 节部署 SDK 并记录三个探测命令输出；先确认 `dotnet new list wpf` 模板存在。CLI 构建纯 WPF 不以安装整个 Visual Studio 为前置，本机是否缺 OS 依赖由实际错误判断。
2. 创建 Host WPF 与 Presentation 类库、行为测试项目；State 项目由联动任务按同一契约提供。采用 C# 默认稳定语言版本、nullable；先使控制窗可启动退出，再创建透明 PetWindow。不为最早窗口步骤读真实状态。
3. 添加 ART manifest、物理像素几何转换、捕获式拖动和三动作诊断夹具；实现单调时间播放器与表现协调，先验纯窗口。之后接入 INT 的 View/调用及完整拖动三段，再验模拟交互，不另写事件规则。
4. 仅为实际风险写播放器时间/取消、抓取偏移、最新状态恢复和坏素材测试。状态去重/时限测试由联动归约器套件负责；程序保留一个集成交错用例，不复制一份状态算法测试。完成下表必要检查后构建自包含目录包。

Host 项目属性候选（完整最小项目文件例，默认 SDK 源文件包含规则；素材复制规则在采用 ART 契约后补入并验证发布目录，不能只在开发机绝对路径读取）：

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net10.0-windows</TargetFramework>
    <UseWPF>true</UseWPF>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <RuntimeIdentifier>win-x64</RuntimeIdentifier>
    <ApplicationManifest>app.manifest</ApplicationManifest>
    <PublishTrimmed>false</PublishTrimmed>
    <PublishSingleFile>false</PublishSingleFile>
  </PropertyGroup>
</Project>
```

以下假定已实现 `src/Aemeath.Host/Aemeath.Host.csproj`、`tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj`，从仓库根执行。测试工具由后续工程任务固定稳定包版本。示例命令语法有效不等于项目已存在或命令运行通过：

```powershell
$dotnetExe = Join-Path $env:LOCALAPPDATA 'Aemeath/toolchains/dotnet/10.0.401/dotnet.exe'
& $dotnetExe restore src/Aemeath.Host/Aemeath.Host.csproj -r win-x64
if ($LASTEXITCODE -ne 0) { throw 'Restore failed' }
& $dotnetExe build src/Aemeath.Host/Aemeath.Host.csproj -c Release --no-restore
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
& $dotnetExe test tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj -c Release --logger trx
if ($LASTEXITCODE -ne 0) { throw 'Behavior tests failed' }
& $dotnetExe publish src/Aemeath.Host/Aemeath.Host.csproj -c Release -r win-x64 --self-contained true -p:PublishTrimmed=false -p:PublishSingleFile=false -o artifacts/host-win-x64
if ($LASTEXITCODE -ne 0) { throw 'Publish failed' }
Get-FileHash artifacts/host-win-x64/Aemeath.Host.exe -Algorithm SHA256
# UI smoke test: foreground application is intentional for manual verification.
$hostProcess = Start-Process -FilePath (Resolve-Path 'artifacts/host-win-x64/Aemeath.Host.exe').Path -PassThru
# 操作者随后从应用退出，再在同一终端检查本次 PID；有输出表示尚未退出。
Get-Process -Id $hostProcess.Id -ErrorAction SilentlyContinue
```

实际启动与退出之间必须等操作者完成检查，不能把上面整段立即连跑来判退出。发布采用目录分发，不裁剪、不单文件、不 NativeAOT，先减少素材路径及运行时提取变量。自包含仍有 Windows 前置依赖，不承诺任意 OS 可运行；应用携带的运行时修补需重新发布。必须将**整个目录**复制到干净 Windows 11 x64 环境，从与包目录不同的工作目录启动，验证资源使用 AppContext.BaseDirectory 定位。

## 8. 必要验证与可接受证据

下表均**未执行**。单次关键路径通过即可推进，失败或改动影响才补测；不设覆盖率门槛，不穷举所有倍率/DPI，不写镜像本规格的文档测试。

| 门槛 | 步骤和通过条件 | 必需证据 / 设备 |
| --- | --- | --- |
| H1 构建与启动 | 上述 SDK/restore/build 成功；真机出现控制窗与透明测试窗口，深/浅背景各看一次；neutral 单帧loop、idle-soft 动态loop可切换；idle-smile 到期回 neutral且仅结束一次，同调度新请求可替代 | 命令/退出码、包版本、两张局部截图；实际 Windows 桌面，不能用浏览器 Canvas 预览代替 |
| H2 拖动和动画并行 | 同一屏幕中央任意可见像素抓取，慢拖/快拖各一次并持续跨越至少两个动画周期；窗口外松手与取消捕获各一次 | 录屏含 cursor、帧号与时间；记录 `cursor-origin-grabOffset`，非夹取区域每轴绝对误差不超过 1 物理像素；帧继续变化、不冻结、不遗留捕获。真人或授权 Windows UI 自动化实际操作 |
| H3 接入归约器后的模拟交互（非纯窗口门槛） | 接入完整拖动三段及 INT：working→拖动→completed→release结束Read；再测期间unknown/新轮次、提示到期与业务标签继续；显式注入诊断提示夹具验证首帧true才消费、false不消费、重复和旧回调不重播 | INT V02–V04/V11对应模拟序列＋实际窗口录屏；持续标模拟/诊断提示。无任务动作时 neutral+状态标签，不将idle-smile当成功；未接归约器记待验，不用换图冒充 |
| H4 像素/DPI/命中 | 当前 DPI 验证 k=1/2；具备设备/设置条件时增加一个 125% 或 150% 的单屏会话，检查物理尺寸和格线；测透明留白及框外点击 | 记录 GetDpiForWindow、窗口物理尺寸、局部截图及底层测试窗点击结果；需真实显示设置，修改前记录并测试后恢复。没有非整数 DPI 条件时明确未覆盖，不阻塞当前 DPI 的单屏窗口结论 |
| H5 坏素材与退出 | 坏neutral整包拒绝；非neutral共享坏帧停用全部引用动作但保留其余有效动作；非法时长/越界路径拒绝整包；保留旧有效包或首次只显示错误控制窗。各代表路径仍可键盘退出，正常关闭/Alt+F4退出全部窗口 | 加载器必要单测、错误截图、Tab/Enter或Alt+X及本次PID消失；用讲述人核对退出按钮名称。需要实际Windows/辅助技术环境，不可用时记待验 |
| H6 自包含包 | publish 成功；复制整个包到未安装 .NET/SDK 的 Windows 11 x64 测试用户/设备或 Windows VM，从别的 cwd 启动并拖动、退出 | 包 SHA256/完整目录、干净环境运行时安装清单、启动截图与退出 PID。现有开发机通过不能替代；没有干净环境则包启动待验，不称自包含验证通过 |

纯单屏诊断窗口先行门槛为 H1、H2、H5 及 H4 当前 DPI 项；H2 显式选择 idle-soft 观察持续换帧，不要求 neutral 换帧。H3 专属接入归约器后的模拟阶段，未执行不阻塞纯窗口先行，但不能宣称模拟交互或完整 M2 通过。H6 独立阻塞自包含包验收，H4 额外 DPI 组合单独记录覆盖。若 H2 跳位或动画停住，记录采样/捕获/消息路径再修复，不以删掉动画或改为页面演示通过。透明区域阻挡范围属于已披露诊断限制；窗口外阻挡、无法退出、状态失真和素材坏导致不可恢复进程属于必须修复项。

后续日常使用阶段再实施位置持久化、混合 DPI 跨屏、拔屏恢复、完整无障碍与性能门槛；本次没有将 QA 对应用例删除或豁免。真机截图/录屏仅截本应用与无私人内容的测试背景。

## 9. 本轮验证记录与 PM 收敛点

v1.0 已执行：`git fetch origin`；按固定提交 `git show` 读取规则、README、project-status、ADR 和三份专业输入；复查 ART 相对首稿的变化与 QA 目标文件（QA 指定提交中该文件相对首稿无差异）；第 2 节 SDK 路径探测、OS 查询及官方 JSON 元数据查询。v1.1 仅 fetch 并读取第 1 节固定 ART/INT 002 规格，按 PM 四项裁决修订第 3/4/6/8 节；SDK 证据沿用 v1.0，不重新调查或下载。官方资料仅证明 API/发行支持存在，不证明本机 WPF 已可用；runtime/build/Windows UI/自包含包仍未实测。

交付前只核查 Markdown 差异、嵌入 JSON/XML 与 PowerShell 示例语法、路径所有权和语义一致性；实际提交及结果在任务对话交接，不复制任务卡到 GitHub。原 Draft PR 随分支推送更新，不合并、不关闭 Issue。

本轮没有缺失调查输入造成的阻塞；后续工程开工只需 PM 收敛两项：

1. 接受 SDK 10.0.401 用户级 ZIP、单屏捕获式拖动、诊断控制窗退出和 H1–H6 门槛，随后派发 SDK 部署/实现权限。现阶段缺 SDK 是未安装，不请求本轮安装。
2. 确认本次对 ART-002 素材规则和 INT-002 Read/TryStartPrompt/EndPrompt 的对齐修订，统一冻结后派实现。只有最早纯窗口允许省略 release，第一角色包及模拟交互须接完整三段；已消费提示被打断不重播。剩余跨文档差异交 PM 统一，不制造第二份协议。

干净 Windows 测试环境是否可用目前未调查；它只阻塞 H6 的实测结论，不阻塞本规格或单屏工程准备。没有要求用户重选产品方向。
