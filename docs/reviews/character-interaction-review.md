# QA-004：首批角色交互定向评审

状态：DEV-004 协调逻辑及宿主接线定向评审通过，无代码阻塞项；原生 UI 和可加载角色包仍待验。2026-09-16。

## 范围与证据来源

依据 PM 基线 `77fa5c0e056e45d8e5c9872195ce86ea91b9e9fd` 与 [ADR 0003](../adr/0003-first-character-package.md)。本次只评审自动待机、笑脸和拖动三阶段协调及宿主接入；不接入模拟或真实任务状态。

ADR 0003 记录的旧版显示、循环/单次播放、拖动/松手重抓、缩放、窗口外点击、错误反馈和退出通过，均为**用户人工反馈**，不是 QA 独立原生 UI 实测，也不能直接证明新增自动交互通过。首次启动坏素材与讲述人仍待验。

固定代码输入为协调器 `0b379876eea33e364a48698b7900d1e14c6d5e51` 与宿主接线 `9f0494dbea1aed8ff415b2d5e78a518a9ec4e7ec`，均已合入 QA worktree。比较 PM 基线至宿主提交，加载器、几何、播放器、依赖锁文件无改动，复用 [QA-003](diagnostic-host-review.md) 的已有证据，不重跑旧完整套件。新协调逻辑使用可控单调时间，不以等待真实 15 秒代替边界检查。

## 定向验证

| 场景 | 检查重点 | 结果 |
| --- | --- | --- |
| 自动待机与笑脸 | 15 秒阈值前/等于；笑脸结束回基础待机；长时间间隔不追赶补播 | 可控时钟通过；从实际回到待机重新计时 |
| pickup → hold | 时长取实际片段；完成前保持 pickup，完成时仍抓取进入 hold | 通过；DEV 的 120ms 与 QA 的 43ms 片段均验证边界 |
| 早松手与捕获丢失 | pickup 未结束即进入 release；重复结束不重启 release | EndDrag API 通过；真实捕获丢失待验 |
| release 期间重抓 | 立即新 pickup；旧完成不能结束新抓取 | 通过 |
| 缺失/停用动作 | 缺 pickup、hold、release、idle-soft、idle-smile 各有有限回退，不困在覆盖中 | 32 种可选动作缺失组合通过；加载器停用后同样从 clips 移除，未重跑解码 |
| 旧完成回调 | 被中断片段的旧实例和重复完成不能覆盖当前播放 | 通过；无外部回调注入接口，独占播放器只产出当前实例完成，旧期限与重复采样不能产生旧完成 |
| 自动/手动切换 | 模式切换后不被旧回调覆盖；手动播放保留；切换时抓取状态一致 | API 通过，含抓取中及 release 中切换；checkbox 实操待验 |
| 宿主接入 | 捕获成功才开始；松手/捕获丢失/取消均通知协调器；同一时钟 | 静态审查通过；实际输入待验 |

`PetWindow` 在 CaptureMouse 成功后调用 BeginDrag；EndDrag 先清拖动状态再释放捕获，避免 LostMouseCapture 重入造成重复 release。鼠标松开、捕获丢失、失焦、Escape、缩放、居中、显示变化、模式切换、换包和退出走已有统一结束路径。模式切换先结束捕获再切协调器；换包创建新协调器，旧实例不复用。UI 自动模式禁用手动动作控件，宿主 API 也拒绝手动播放。未发现接入任务状态或将笑脸宣称任务成功的逻辑。

## 实际命令与结果

环境为 Windows 11 x64，SDK `10.0.401`；命令中的 `$sdkExe` 为 `$env:LOCALAPPDATA/Aemeath/toolchains/dotnet/10.0.401/dotnet.exe`。

| 命令 | 实际结果 |
| --- | --- |
| `& $sdkExe test tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj -c Release --no-restore --filter FullyQualifiedName~CharacterControllerTests --logger trx` | 8 通过，0 失败/跳过；TRX `tests/Aemeath.Presentation.Tests/TestResults/bigxi_SENJO_2026-09-16_15_27_49_net10.0.trx` |
| `& $sdkExe run --project scripts/qa/DiagnosticChecks.csproj -c Release --no-restore -- interaction` | 5 项独立探针全部通过，其中一项遍历 32 种缺动作组合；未执行旧默认探针 |
| `& $sdkExe publish src/Aemeath.Host/Aemeath.Host.csproj -c Release -r win-x64 --self-contained true --no-restore -p:PublishTrimmed=false -p:PublishSingleFile=false -o artifacts/host-win-x64` | 固定宿主 9f0494d 发布退出 0 |
| `./scripts/qa/Test-AutomaticProcess.ps1` | Hidden 启动自有诊断进程 PID 17664，退出 0；idle → smile → idle，一次 natural-end，18 秒后正常 shutdown |
| `./scripts/qa/Inspect-Png.ps1 -Path artifacts/qa-art-872595a/assets/characters/aemeath-v1/source/neutral-generated-v1.png` | 只读尺寸/alpha/哈希核对退出 0，详见下节 |
| `git diff --check` | 退出 0；未见空白错误 |

过程日志为 `artifacts/qa-automatic-e8fcce25faf845dfa760b9e94bcb5b23.jsonl`，发布 exe SHA-256 为 `A77738411EACE423A8B45A106D98F0BB0A994E696A2010FF2931B3D87F0118F1`。两个 frame 日志观测点相隔 14999ms；日志采样/写入时刻不能判断严格阈值，15000ms 的等号由可控时钟测试证明。smile 首帧日志 15898ms，完成日志 16411ms；均为应用自身输出，未注入原生输入。DEV 后续给 smoke 脚本补 Hidden 参数属于探针修正，不改变此固定应用代码结论。

## 角色与原生 UI 限制

ART 固定输入 `872595a0f15bad3dffa781489a6f6f6cc586973b` 的 `assets/characters/aemeath-v1/source/neutral-generated-v1.png` 已从 git archive 只读导出并用 view_image 实际预览：粉发、金色睁眼、蓝色头饰、紧凑身体及两侧羽饰可辨。仅表示已检查原图，不表示用户已认可外观，也不表示缩小后视觉可用。

独立读取结果：1205×1305，778921 bytes，PNG 位深 8、色彩类型 6（RGBA）；透明像素 987626，完全不透明 1628，半透明 583271，共 256 种 alpha。SHA-256 `251ADD4C2C0384F2D0ED58A3F4CA2CFC6C67B7DFD2CF6CB1C65F3DD276DEA815` 与 ART 记录一致。尺寸、二值 alpha 及 256KiB 单图上限均不符合加载契约；无 manifest，锚点未验。本轮未修改、缩放或生成图片，也未将该原图交给宿主加载。需要用户外观确认及后续合规导出、复查，不作为六动作包通过。

当前工具禁止原生 UI 控制。新增交互在真实窗口中的按下、松手、捕获丢失、重抓和模式切换仍待人工验证，不采用替代自动化绕过限制。可控时钟结果与静态接线审查不冒称原生窗口通过。

交接 PM：可接受本轮代码定向门槛；新角色包与真实交互分别保留待验。合规动作交付后，在真实窗口检查一次 pickup→hold→release、快速松手、捕获丢失、release 中重抓和自动/手动切换即可；复用未改的几何/加载证据，不展开动作×DPI 全组合。首次启动坏素材与讲述人仍保留上轮待验。未合并 PR、关闭 Issue 或作发布决定；QA 沿用 Draft PR #6，提交哈希见交接消息。
