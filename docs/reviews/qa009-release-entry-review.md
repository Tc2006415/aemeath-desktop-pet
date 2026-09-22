# QA-009 · DEV007 release-entry 独立验收

日期：2026-09-21。结论：固定版本的代码审查、39 项受影响测试、独立边界检查及当前 Host 实跑通过；本次未发现需退回 DEV 的阻断缺陷。原生拖动、失捕获和视觉连续性仍待用户验收，不能据此宣称完整桌面交互验收通过。未修改生产代码或素材，未合并、提升正式资源或发布。

## 固定输入与隔离

- DEV007：`74d84427c4b392d14aff146489acec820654488a`；交接文档读取自 `5eab52028edb7bfa769e7842ff44f11ceb1ef8ca`。
- PM ADR004：`22799b4`；ART019：`c2f5a71312746990b9e7c715ad67e5e568d97a7c`。
- 实现通过 `git archive` 解压至 `artifacts/qa009-dev-74d8442`；没有合并 QA 分支的历史正式 0.2 资源。
- 候选复制自 ART 的 `assets/characters/aemeath-v1/source/art019-package` 至 `artifacts/qa009-art019`。原件与副本 raw manifest SHA256 均为 `EAB91ECB10037DA7320D4E9C9321C8DCE0F122D3B9D5DAA6E101A55E1E319DA3`。17 个文件通过 `git hash-object --path=<仓库路径>` 与 ART019 对应 blob 比较，全部一致（应用 Git 文本属性）。运行前后 manifest 哈希一致。

## 验收证据

| 项目 | 结果与证据边界 |
| --- | --- |
| 真实 16 入口 | DEV 的 CandidateReleaseTests 在上述候选上实际执行，非跳过：经真实动作取得各源帧后确认提交，再释放，逐入口检查每段起点、结束前 1 ms、完成时刻及一次完成。 |
| 独立 ADR 时序 | QA 自行固定 16 个源路径及 deadline，不以 manifest 的时长作为期望值。首帧保留来源、最后 neutral、end−1 不完成、end 恰好完成且不重复，全部通过。 |
| 有效 framePath | 独立核对 up→H→M→L→hold-half→release-closed→release-half→neutral，起点为 0/40/80/120/160/240/340/460 ms。覆盖超出四项基础 release 的索引。Host 使用 Sample.FramePath 查图。 |
| 未绘制的新请求 | 已提交 idle 后按下、39 ms 松手而未提交 pickup，入口沿用旧 PlaybackId 的真实提交图；跨越时序边界但未提交新图，也沿用已提交路径。 |
| epoch 与重抓 | 新 controller 拒绝旧样本、第一帧前松手走基础 release 并记录 no-submitted-frame；模式变更清除快照。重抓首帧 neutral，旧 release 不产生完成回调；旧未提交样本不能覆盖新状态。 |
| schema 与降级 | 受影响测试覆盖 schema1、schema2 字段/重复键/首尾限制、65 项拒绝、总计 256 接受/257 拒绝、坏图降级。QA 独立补测 entry-only 序列 60000 ms 接受/60001 拒绝，损坏其独有 PNG 只停用 release，随后释放回 idle；schema1 仍可加载。 |
| 原生捕获清理 | 仅源码审查：PetWindow.cs:140 先 drag.End，再 ReleaseMouseCapture，再 controller.EndDrag；同步 LostMouseCapture 重入因拖动已清除而返回。未在原生 UI 触发验证。 |
| 当前 Host | 新构建 self-contained Host，PID 43260，ExitCode 0；schema2/version0.4.0/manifest 哈希一致、无停用动作、16 入口库存、20 个 hold 时序项路径正确，epoch=1、提交序号有效；包含 pet-stopped/shutdown，无 package-rejected 或 position-error。这不是 16 入口的原生激活记录。 |

独立 deadline：up 620；H 580；M 540；L 500；hold-half 460；down 500；hold-mid-closed 460；hold-surprise 与 pickup-surprise 各 500；neutral 160；release-closed 380；release-half 280；soft-light、soft-peak、smile-half、smile-closed 各 200 ms。

审查定位均以固定 DEV007 快照为准：

- `src/Aemeath.Host/PetWindow.cs:90` Rendering 唯一调用 Draw；`:98` 采样后赋值 Image.Source，再 CommitRendered。`:66` 更换包创建递增 epoch 的新 controller；`:195` 停止并清理引用。
- `src/Aemeath.Presentation/CharacterController.cs:26` 只接受本实例最近发出的同一 sample 对象；`:59` 释放使用 LastSubmitted，不在松手时重新采样；`:75` 仅当前 expectedInstance 的完成触发状态转换。
- `src/Aemeath.Presentation/Playback.cs:21` 保存所选入口完整数组；`:35` 统一单调时间、半开区间与 once 完成。
- `src/Aemeath.Presentation/PackageLoader.cs:48` 所有基础与入口序列共用 64 项、60000 ms 校验；`:59` 累计 256 项/128 路径；`:98` 保持 8 MiB 累计限制。128 路径和 8 MiB 本次为代码核对，未新增极限资源夹具。错误图片使使用它的动作整体停用，坏 neutral 拒绝整个包。

## 实际命令与结果

在仓库根目录创建隔离输入：

```powershell
git archive --format=zip --output=artifacts/qa009-dev-74d8442.zip 74d8442
Expand-Archive artifacts/qa009-dev-74d8442.zip artifacts/qa009-dev-74d8442 -Force
Copy-Item -LiteralPath 'C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source/art019-package' -Destination artifacts/qa009-art019 -Recurse
```

在实现快照根目录执行：

```powershell
./scripts/build.ps1 -Publish
$sdkExe = Join-Path $env:LOCALAPPDATA 'Aemeath/toolchains/dotnet/10.0.401/dotnet.exe'
$env:AEMEATH_RELEASE_PACKAGE = 'C:/Users/bigxi/.codex/worktrees/26d3/桌宠/artifacts/qa009-art019'
& $sdkExe test tests/Aemeath.Presentation.Tests/Aemeath.Presentation.Tests.csproj -c Release --no-restore --filter 'FullyQualifiedName~PackageTests|FullyQualifiedName~ReleaseControllerTests|FullyQualifiedName~CandidateReleaseTests|FullyQualifiedName~CharacterControllerTests|FullyQualifiedName~PlaybackGeometryTests.HalfOpen|FullyQualifiedName~PlaybackGeometryTests.Once|FullyQualifiedName~PlaybackGeometryTests.Replacement|FullyQualifiedName~PlaybackGeometryTests.Missing|FullyQualifiedName~PlaybackGeometryTests.Clock' --logger 'trx;LogFileName=qa009.trx'
./scripts/smoke-release-entry-host.ps1 -PackageRoot 'C:/Users/bigxi/.codex/worktrees/26d3/桌宠/artifacts/qa009-art019'
```

结果：锁定还原与构建通过，0 警告、0 错误；发布资源检查 10 个文件均匹配、额外文件 0；测试 39 passed / 0 failed / 0 skipped；Host 检查退出码 0。未运行无关的完整几何测试。

在 QA 仓库根目录执行 `./scripts/qa/Test-ReleaseEntry009.ps1`：16 个独立 deadline 用例及有效路径、controller 隔离、loader 边界/降级三组检查通过，退出码 0。脚本只引用固定快照；`.cs.txt` 避免被现有 QA 项目自动编译。`git diff --check` 通过。

本地证据（artifacts 不提交）：

- `artifacts/qa009-independent/results.txt`
- `artifacts/qa009-dev-74d8442/tests/Aemeath.Presentation.Tests/TestResults/qa009.trx`
- `artifacts/qa009-dev-74d8442/artifacts/smoke-release-entry.jsonl`
- 本次 Host exe SHA256：`A8274605D923B32EF79B3B38A17D8A3AE339AEAB1D6485C4EE83DAB0E721B705`；dll：`6C535B94701ED4F3AC00DBA342122ADBF6412A93A3C1036BE2026DF10D5658CF`。这是 QA 新构建产物，不沿用 DEV 或旧 QA 的二进制哈希。

## 待用户原生验收与交接

当前工具明确禁用原生应用控制；未使用输入注入、截图脚本、UIAutomation 或浏览器模拟替代。仍需在当前 Host 上验证：拖动中松手立即停止位移、失捕获/失焦/Escape 清理、快速按下松手、不同翅膀阶段的收翅、release 中重抓与旧完成隔离、换包/模式切换。当前 evidence 只确认 Image.Source 提交，不能证明屏幕实际呈现确认或连续视觉。

重抓采用 ADR004 的 neutral-first 策略；潜在视觉跳变未获得原生验证，不宣称无缝。保留用户 KEEP 放下大幅上抬的选择，未私自缩小幅度。上述待测项不是已复现的代码缺陷；本次无可报告的 P0/P1/P2 代码问题。

交付在 `codex/acceptance-matrix`，沿用 Draft PR #6：https://github.com/Tc2006415/aemeath-desktop-pet/pull/6。QA 提交由 PM 选择性接收，避免合并此 QA 分支历史素材；集成、正式包提升和发布仍由 PM 决定。QA-009 交付后停止，未进入下一阶段。
