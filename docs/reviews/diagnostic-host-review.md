# QA-003：第 1–4 步诊断宿主独立验收

状态：待 PM 验收；自动化与进程证据已取得，原生 UI 必要项待验。规则基线：`dd284ec9698037ebfc008d64c7e17be8bcb3e4e5`；按 ADR 0002 接受的范围验证，不扩大为完整 M2、角色、状态归约器或真实联动验收。

## 范围与证据分层

独立 QA worktree 已快进合并 PM 基线。宿主/素材规格分别以 ADR 0002 固定的 DEV `6c929a5`、ART `ce81a52` 为准；状态 `807fffd` 仅保留将来接入边界。诊断素材只能为明确标识的测试夹具。

| 必要项 | 独立验证方法 | 能证明 / 不能证明 |
| --- | --- | --- |
| SDK、restore、Release build | 使用固定 SDK 绝对路径，在 QA worktree 重跑命令并记录退出码 | 能证明此提交在此开发环境构建；不能证明干净设备分发 |
| A15 播放器 | 按不等帧时长测试边界前/等于/后、循环跨周期、once 一次结束、替换和取消、旧实例回调 | 能证明逻辑时序；不能证明拖动期间真实窗口继续绘制 |
| A14/W09/QAR07 素材 | 对合法包、坏 neutral、共享坏帧、非法元数据/路径、资源上限做独立输入验证 | 能证明加载分类和回退输出；错误可见与键盘退出仍需真机 |
| A16/QAR05 坐标 | 已知物理像素/DPI/倍率的独立期望值、负坐标、抓取偏移与工作区夹取 | 能证明纯换算；不能证明 Win32/WPF 实际边框、捕获或点击命中 |
| H1/H2/H4 当前 DPI/H5 真机 | 实际透明窗口、慢快拖/窗口外松手/捕获取消、框外点击、坏素材报错及键盘退出 | 必须实际 Windows 操作与证据；程序内事件、启动存活、浏览器预览不能替代 |

原生 UI 限制：当前 CUA 工具明确写明 Native computer APIs are disabled；已阅读 computer-use 技能，不使用其他输入注入、UI Automation 或截屏程序绕过禁用。程序任务也确认同样限制。可执行构建/纯逻辑/应用自检将继续做，受限手工项目不写通过。

## 固定代码与实际命令

第一固定增量：`372e38dbb415175194959f25b954111c23ecf2c7`。已快进合并到 QA worktree；此提交只有初始控制窗，透明窗口尚未交付，不能按完整宿主验收。没有修改其业务代码。

已独立执行 SDK/环境探测（程序任务部署后）：

```powershell
$sdkExe = Join-Path $env:LOCALAPPDATA 'Aemeath/toolchains/dotnet/10.0.401/dotnet.exe'
& $sdkExe --info
& $sdkExe --list-runtimes
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture
```

两条 dotnet 命令退出码均为 0；SDK 10.0.401、MSBuild 18.9.11、RID win-x64，Microsoft.WindowsDesktop.App/Microsoft.NETCore.App 10.0.12。OS 为 Windows 11 家庭版中文版、10.0.26200、64 位。此时 PM 纯文档基线无 global.json；待程序提交后再核固定版本选择。官方 ZIP 校验部署为程序任务报告，本 QA 未重复下载或冒称独立验证下载哈希。

程序提交的 global.json 已核为 10.0.401、rollForward=disable、allowPrerelease=false；后续命令在该版本选择下执行。

在固定增量和其 global.json 下执行：

| 命令 | 实际结果 |
| --- | --- |
| `& $sdkExe new list wpf` | 退出 0，WPF 应用/类库模板存在 |
| `& $sdkExe restore Aemeath.slnx --locked-mode` | 退出 0，三项目还原成功，锁文件未变 |
| `& $sdkExe build Aemeath.slnx -c Release --no-restore` | 退出 0，0 警告、0 错误 |
| `& $sdkExe test tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj -c Release --no-build --logger trx` | 退出 0，20/20 通过，0 跳过；这是 QA 独立复跑开发方套件 |
| `& $sdkExe run --project scripts/qa/DiagnosticChecks.csproj -c Release` | 最终退出 0，10 个独立契约探针通过；首次 QA 脚本编译因 Geometry 命名冲突失败，补显式别名后通过，不归因于产品 |
| `& ./scripts/qa/Test-ReparseBoundary.ps1 -FixtureRoot <上条输出的 FIXTURE_ROOT>` | 退出 0；真实 Windows 包根 junction、frames junction 两个输入均在解码回调前拒收 |

工作目录为本 QA 仓库根；SDK 使用前述绝对路径。TRX 位于 `tests/Aemeath.Presentation.Tests/TestResults/bigxi_SENJO_2026-09-16_14_56_31_net10.0.trx`（本地生成、不提交）。独立探针不复用开发方测试方法，直接调用公开加载/播放/几何边界，并用规格的独立常量判断。

独立覆盖：manifest 65536/65537 字节、单动作 60000/60001 ms、64/65 个时序项、非法路径在解码前整包拒绝；真实 WPF 解码合成单像素 PNG，共享坏帧停用两条完整动作、坏 neutral 首次拒绝及重载保留原包；once 在299/300/499/500 ms的半开边界、重复采样、替换/旧取消、大时间跳跃和缺失动作不伪装完成；120 DPI 的 192×208 物理尺寸与153.6×166.4 DIP、负坐标抓取偏移和夹取。不是所有动作/DPI的穷举。

探针临时夹具保留于 `%TEMP%/aemeath-qa-8843ceecf5074ae08dd70610f2c1b1d2`；junction 探针位于 `%TEMP%/aemeath-qa-reparse-b8805ee47e594e1daa0786fe5895b040`，仅指向前述合成数据。脚本不递归删除链接，不读取私人文件。这些是文件系统边界验证，不是 UI 自动化。

## 完整窗口固定提交与独立运行

完整窗口运行证据对应：`e0e0eac238f06ce4d1c43d2d8d22c9df6416673e`，较 `372e38d` 增加控制窗、PetWindow、NativeMethods、诊断日志与三帧素材。最终代码定向复核对应：`c04e96f5d238d67247a39d354a6b1bfbf79038f3`。QA 在自己的 worktree 先后快进合并这些固定对象，未读取对方未提交工作区作为验收输入。后续提交不自动包含在此结论内。

独立阅读 App/DiagnosticWindow/PetWindow/NativeMethods/DiagnosticLog、程序集与 DPI manifest、加载器/播放器和构建脚本，核查：释放捕获前清拖动标志避免重入；关闭路径有幂等保护并解绑静态 Rendering；定位异常取消拖动保留控制窗；无来源保持 unknown，手动 idle-smile 不映射任务成功；坏包加载失败不替换旧有效包。代码存在这些路径不是原生输入实测通过。

| 命令（QA 仓库根） | 实际结果 / 证据 |
| --- | --- |
| `& ./scripts/validate.ps1 -Publish` | 退出 0；locked restore、Release build 0警告0错误、20/20测试、win-x64自包含目录发布成功。TRX：`tests/Aemeath.Presentation.Tests/TestResults/bigxi_SENJO_2026-09-16_15_07_03_net10.0.trx` |
| `& $sdkExe run --project scripts/qa/DiagnosticChecks.csproj -c Release` | 完整窗口提交下重新构建独立探针并运行，10/10通过，退出0。新夹具 `%TEMP%/aemeath-qa-276f3849b2494219944254bb49a1f406` |
| `& ./scripts/qa/Test-ReparseBoundary.ps1 -FixtureRoot <首次探针夹具>` | 完整窗口提交下重跑包根/frames junction拒收，两项通过，退出0；不控制原生UI |
| `& ./scripts/qa/Test-HostProcess.ps1` | 退出0；从TEMP作为cwd启动QA自己构建的包，loop-2、once-1、bad-neutral三个进程均自行定时关闭，退出码0。不是键盘退出 |

进程证据在本地 `artifacts/qa-baec6dada0444d20bf17e54bccca7e4e/`（不提交日志/产物）：

- `loop-2.jsonl`：PID 19100，control-rendered/package-loaded/pet-loaded/render-callback；loop跨至少两周期换帧，0次natural-end；DPI144，物理192×208，clientOffset(0,0)。
- `once-1.jsonl`：PID 52464，500ms once仅1次natural-end，最后回neutral；DPI144，物理96×104，clientOffset(0,0)。
- `bad-neutral.jsonl`：PID 17044，首次坏neutral产生package-rejected且retained=false；有control-rendered，无pet-loaded，正常shutdown。只能证明独立控制窗渲染/错误分支执行，不能证明用户能看见错误或按键退出。

本次已运行的本地可执行文件：`C:/Users/bigxi/.codex/worktrees/26d3/桌宠/artifacts/host-win-x64/Aemeath.Host.exe`，对应 **e0e0eac**。SHA256：`A07D217F043B5D96C029F8C1E3F343E68FCED11881C1402340DFB5DF9D080C57`。运行需保留整个发布目录；不能只复制exe。此处哈希是可执行文件标识，不是整个包的完整性清单，也不证明干净环境通过。按 PM 收尾要求未再重发 QA 包或重复整套已通过检查；c04e96f 的修复由下节定向复核，不能把这个旧包标成包含修复。

QA 进程脚本只启动应用并读取其显式自检日志；没有注入鼠标/键盘、查其他应用窗口、截图或将内部事件冒充真实操作。定时关闭后进程已退出。日志/夹具仅本应用合成数据，测试包没有正式角色帧。

## 缺陷与验收结论

开发方在 e0e0eac 自审发现一项代码问题并主动回传：DiagnosticWindow.LoadPackage 先调用 pet.Show，Loaded/ApplyLayout 的定位错误可被后续“动作可用性”ReportError覆盖，用户可能看不到定位失败原因。QA 静态核对了该顺序；没有故障注入或真实显示失败的复现证据。问题属于 H5 错误可见性，不改变素材或状态契约。

c04e96f 将 SetPackage/Show 后置到可用性文案之后；`git diff e0e0eac c04e96f -- src/Aemeath.Host/DiagnosticWindow.cs` 确认 Show 后不再写覆盖文案。QA 已定向确认这条覆盖路径被消除；开发方报告该修订 build/20测试通过，**QA 未重复执行，不能冒称独立复跑**。修订另含开发方交接文档，未改加载器/播放器/坐标和其接口。按 PM 指令收尾，保留已有自动证据；异常定位提示的真人观察仍纳入待验。

截至 c04e96f 定向复核，无其他已确认的阻塞代码问题。QA 脚本首次命名冲突已在自己的允许范围修正。通过项目不能外推到未执行的故障路径或真实输入。

| 门槛 | 结论 | 阻塞范围 |
| --- | --- | --- |
| SDK / restore / build / 本地publish | 通过，命令与固定版本可复现 | 不阻塞继续人工诊断；不是分发验收 |
| A14/A15/A16相关自动验证 | 开发方套件20/20独立复跑，额外10探针及2项junction通过 | 已执行范围通过，不以数量声明全部边界完备 |
| H1启动与透明 | 应用进程、控制/像素窗渲染回调、loop/once路径通过；浅深背景透明效果待验 | 阻塞H1完整验收及“透明桌宠可用”结论 |
| H2真实鼠标 | 慢快拖、拖动时动画、窗口外松手/取消捕获、实际抓取误差均待验 | 阻塞真实拖动能力验收；逻辑offset测试不能替代 |
| H4当前DPI | 自身HWND数值144 DPI及1×/2×物理尺寸通过；像素视觉、留白及矩形外命中待验 | 阻塞H4完整验收；其他DPI未覆盖，完整多屏范围外 |
| H5素材与可访问退出 | 自动加载/旧包保留/首次错误进程分支通过；可见错误、Tab/Alt+X/Alt+F4与讲述人名称待验 | 阻塞可访问退出及H5完整验收；定时shutdown不可替代 |
| H3/H6、角色/持久化/完整多屏 | 本轮范围外，未执行 | 不阻塞本轮诊断准备，不可写成已验收能力 |

**唯一当前验收阻塞是原生 UI 必要证据缺失这一组**，不是已复现的程序故障。最短解除方式为下节的真人操作；若任何一步失败，将提交、日志与具体复现回 PM，由 PM 定向派修，不由 QA 改业务代码。非阻塞限制为仅主屏诊断、有限素材和开发机自包含目录试运行；这些边界须随交付保留。

## 最短人工补验路径（未执行）

使用无私人内容的桌面或测试背景，最终补验优先使用 PM/DEV 以 c04e96f 发布的目录并核对其版本与哈希。下面给出本次已实际运行的 e0e0eac 本地路径，便于立即查看诊断样机；它尚不包含定位错误提示修复，不能据其验收修复项。命令会持久在线（没有定时退出），随后由人操作；本报告中的人工入口尚未执行：

```powershell
$qaExe = 'C:/Users/bigxi/.codex/worktrees/26d3/桌宠/artifacts/host-win-x64/Aemeath.Host.exe'
& $qaExe --diagnostics 'C:/Users/bigxi/.codex/worktrees/26d3/桌宠/artifacts/qa-manual.jsonl' --clip idle-soft --scale 2
```

记录提交、包哈希、Windows版本、当前DPI和操作录像；每项填实际结果，不只勾选计划。坏neutral包可直接选择本轮生成的 `artifacts/qa-baec6dada0444d20bf17e54bccca7e4e/bad-neutral`；验证首次坏包时先退出，再用 `--package <该绝对路径>` 启动。

1. 启动控制窗及透明小窗；浅/深背景各观察一次。确认常驻诊断/未知标识，选 idle-soft 观察循环，再选 idle-smile 确认单次回 neutral。
2. 选 idle-soft，在主屏中央可见像素处慢拖和快拖，各跨至少两个周期；在窗口外松手，另做捕获取消。确认帧号继续变化、再次拖动可用；非夹取区域抓取偏移误差每轴不超过 1 物理像素。记录透明留白与矩形外点击下层测试窗结果。
3. 在当前 DPI 切换 1×/2×，核对 96×104 / 192×208 物理尺寸、锚点与清晰度。其他 DPI 和完整多屏不由这一步推定通过。
4. 正常包及首次坏 neutral 包各试一次：坏包保留可见控制窗错误、没有不可操作透明窗；用 Tab/Enter 或 Alt+X 退出，另一轮试 Alt+F4。用讲述人核对退出名称；检查本次 PID 已消失。不以强杀进程代替可访问退出。

H3 归约器、角色视觉、位置持久化、完整多屏/H6 干净环境均超出 ADR 0002 本轮完成声明；不当作已通过，也不借这些延期豁免上述真机必要项。

交接：本轮仅新增本报告及 scripts/qa 下独立验证项目/脚本，未改开发方代码或公共接口。QA提交另见任务对话；原分支推送，保留Draft PR，不合并、不关闭Issue。报告可供PM接受自动化部分、组织最短人工补验，不能据此宣布第1–4步全部运行验收完成。
