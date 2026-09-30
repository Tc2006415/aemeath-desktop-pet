# 原生 v2 定点审查（QA 本地证据编号 QA011）

2026-09-29。**未发现阻止 PM 集成候选的代码缺陷。** QA 新增八组独立定向检查通过；DEV 留存的 48 项测试、三份进程日志和二进制指纹已只读核验。建议进入 PM 集成后的人工 Windows 验收；这不是原生鼠标/视觉通过，也不是默认 0.5 包推广决定。

## 固定范围

- 规范：PM `15b2c32` 的 ADR0005 顶部冻结条款，覆盖附录中历史“待决”字样。随机 blink 完成后 4000..7000 ms、wink 50000..69999 ms；碰撞 wink 优先、已开始 blink 先完成。
- 代码：`7a28a49..c9bac870d5a19c0b43dc6ff140f997e8d351ea62`，实现提交 `c608fa1`、`c9bac87`。审查固定 git archive，最终隔离目录为 `artifacts/qa011-dev-c9bac87`；未合并其他分支。
- 最终交接文档：`843da413c6952a581c94cb7d36ab59357541eed1:docs/implementation/native-v2-progress.md`。该提交仅文档，未改变审查代码。
- 素材：ART036 `11a30f1ce32f973f02fedc85a29b20326b3ea151`，只读复制到 `artifacts/qa011/art036-package`。raw manifest SHA256 `95cf8f8102f9631d0a02ae40a46fa497f61d9d423ff350191a399104a0a4b182`；65 个文件以 Git 属性归一化后逐个匹配固定提交 blob，PNG 不转换。ART035清单使用候选旁的 `art035-handoff.json`。
- 任务卡与冻结条款已给出范围、选择和实施授权，没有重新询问已决产品设计。只增加 QA 检查与报告，不修改生产代码、素材、接口、锁文件或默认资源。

## 代码审查与证据分层

| 范围 | 检查结果及定位（均以 c9bac87 为准） |
| --- | --- |
| schema3 严格解析 | `PackageLoader.cs:41` 仅 schema3 允许并要求 behavior；`:70` entrySequences 仅 schema2。`BehaviorParser.cs:8` 严格字段、唯一路径、45组合、64键/路由完整覆盖、5类尾部及逐段精确时长；`:94` 与手动动作共用256时序项上限。保留64KiB/depth8/128路径/每图256KiB/总8MiB等边界。不是只校验总时长。 |
| 旧包兼容 | 旧 clips 构造与 schema1/2 loader/player 分支保留；旧15秒策略仅在非layered自动路径。DEV已执行的旧包、旧controller与player相关测试在48项TRX中通过；QA没有重跑整套历史测试。 |
| 真实提交与身份 | `CharacterController.cs:25` 单一 NextInstance 供手动与layered共用；`:46` 只接受最近发出的同一对象且验证key/path；`:78`/`:85` 事件仅读取提交快照，`:125` 检查epoch及注册映射。不以SHA反查语义身份。旧PlaybackId的已提交源合法，外部clone、旧issued对象、重复提交、模式/包替换旧对象无效。 |
| 700/1400/540 时钟 | `LayeredBehaviorController.cs:35` pickup完成后使用 press+700；`:37` release完成后使用 releaseStart+540，而非迟到Sample时刻。hold按1400取模，不自动缓和；单实例完成一次，重抓替换旧release。 |
| 眼动作等待 | `LayeredBehaviorController.cs:45` 已开始眼动作先完成；`:48` blink只重抽blink，不推迟wink；wink重抽两个等待；`:54` 同时到期优先wink；`:57` 翼/衣摆共用idleEpoch。迟到最多开始一个到期眼动作，不补播历史次数。生产随机调用使用 inclusive max+1，对应冻结闭区间。 |
| Host 捕获与绘制 | `PetWindow.cs:100` 使用实际FramePath赋值Image.Source再确认提交；日志包含FrameKey/BehaviorPhase/path，去重键含key/path。`:142` 先drag.End清active，再ReleaseMouseCapture，再controller.EndDrag，同步失捕获重入直接返回；鼠标抬起/失焦/Escape等沿用该路径。此项是源码审查，未在原生窗口触发。 |
| 换坏包 | `PackageLoader.cs:106` 检查图SHA，`:129` schema3任一坏图整包拒绝。`DiagnosticWindow.cs:78` TryLoad失败即返回，不SetPackage。独立检查通过“坏图但SHA正确更新”强制走解码失败路径，PackageSession保持原有效对象。 |

没有记录需 DEV 修复的 P0/P1/P2 问题。表中静态限额审查不冒充每一种极限资源均新增了运行夹具；固定 profile 的逐段精确值也会提前拒绝扩张配置。

## QA 实际新增并执行的八组检查

使用 ART036 的生产解码与固定代码，受控单调 clock、随机值和提交确认；不是原生输入。

1. 两个1400ms周期内翼/衣摆全部联合边界前1ms与边界，包括1100/1200、1250/1350错开的回落。
2. pickup的59/60、199/200、339/340、479/480、619/620、699等半开边界；跳到1450ms时hold使用press+700原点；2099/2100ms确认hold周期回绕且ID不变。
3. release的0/59/60/159/160/259/260/379/380/539ms十个时刻，真实Sample→CommitRendered后重抓：保留各阶段源图，新pickup ID更大，旧release期限不能切走新动作，新pickup完成仅一次。
4. release开始于20ms，迟到1000ms采样仍按560ms重启idle；4559ms未blink、4560ms开始blink；15000ms不调用旧自动笑脸。
5. 49760ms迟到启动blink，49999ms仍完成该blink，50000ms立即wink；wink51200ms结束才重排两等待，55200ms开启新blink；2000000ms迟到只完成当前眼动作并开始一个到期动作，同刻不重复回调/抽签。
6. 手动/自动共享递增ID；clone拒绝；按下未绘制、40ms松手仍使用之前提交图；过期/重复issued对象拒绝；模式切换及新epoch清除旧源，缺源使用本包neutral并记录回退。
7. images/routes/tails内部重复属性、总周期相同但399/151错误分段、schema3夹带旧entrySequences语法均拒绝。
8. behavior-only图`idle:C-wink-upper`损坏，同时将manifest SHA更新到坏字节的正确SHA：整包拒绝，旧有效PackageSession对象保留。

实际命令（QA worktree 根目录）：

```powershell
./scripts/qa/Test-NativeV2.ps1
& 'C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe' -B scripts/qa/check_native_v2_evidence.py artifacts/qa011/art036-package artifacts/qa011/art035-handoff.json 'C:/Users/bigxi/.codex/worktrees/e114/桌宠' artifacts/qa011/evidence.json
git diff --check
```

结果均 exit0；八组PASS，0失败。证据位于 `artifacts/qa011/checks/independent-results.json` 和 `artifacts/qa011/evidence.json`。未新增依赖；`.cs.txt` 复制到隔离项目，避免进入旧QA项目默认编译范围。

## ART 来源与64路证据

独立读取 ART035 assets 清单与 ART036 manifest：64逻辑键/64独立路径、60种PNG SHA、524130压缩字节；逐个大小和SHA完全匹配，别名身份未按相同字节合并。manifest 29882字节。64个release映射展开均与ART035的首60ms及四项尾部一致。

DEV `NativeV2CandidateTests.ActualCandidateAll64BoundReleasePathsMatchArt035AndCompleteOnce` 的留存通过记录是**binder+Playback穷举**，不是controller/鼠标64源穷举。其真实候选controller用例覆盖可达phase。QA新增的是上述controller时间与提交风险，未制造外部快照绕过所有权来声称64源controller覆盖。

## DEV留存测试与进程核验

没有重复启动相同smoke。读取固定交接中的真实命令、测试结果及保留文件，并执行独立验证脚本：

- TRX `e114/桌宠/tests/Aemeath.Presentation.Tests/TestResults/bigxi_SENJO_2026-09-29_17_29_31_net10.0.trx`：48个实际结果均Passed，48执行/0失败/0跳过，包含旧包、新包、controller、候选及五个player相关测试。SHA256 `21eb3a529b8a1fd83f6394f3d1681feddd7536ab57af53ecd46da839fb308417`。这是QA核验DEV结果，不是QA重跑48项。
- 三份日志均核对schema3/version0.5.0/profile/manifest，64键、45组合、64路/5尾部；每个frame的注册key/path、epoch、严格递增提交序号正确；包含render-callback、pet-stopped与shutdown，无package-rejected/position-error。

| DEV日志 | PID | 核对到的帧日志/完成 |
| --- | --- | --- |
| artifacts/smoke-v2-automatic.jsonl | 17244 | 76条帧日志，idle/blink，2次自然完成 |
| artifacts/smoke-v2-manual-wink.jsonl | 56248 | 6条帧日志，包含手动wink四项且一次完成 |
| artifacts/smoke-v2-manual-release.jsonl | 54016 | 7条帧日志，包含手动release五项且一次完成 |

三个退出码0来自DEV固定交接记录；QA确认了对应PID和正常shutdown日志，未亲自等待这三个已结束进程，因此不把日志等同独立观测的ExitCode。自动短探针没有覆盖随机50–70秒wink；手动wink日志只能证明手动动作绘制。

专用 `e114/桌宠/artifacts/native-v2-win-x64` 三个文件的实际SHA与DEV记录一致：

| 文件 | SHA256 |
| --- | --- |
| Aemeath.Host.exe | 9C266D8E594D5CD1D63AF8C81252302C2FE2EFBF85AA332946A4BED9B78208DE |
| Aemeath.Host.dll | C33F8E0CB167B466A7F660705F9B622A7B2A606EDC5CD00BA2DD44994DBC7610 |
| Aemeath.Presentation.dll | 6872A2184688B30D47EDBB4DD5F375E5F04C7CEA27EF1DF395145EA902C1D385 |

这些文件是显式`--package`候选探针产物，默认资源仍为DEV旧配置，**不是已推广0.5分发包**；本轮未触碰PM正式0.4。

## 人工门槛与交接

当前工具明确禁用原生应用控制。已读当前computer-use技能，但没有使用其他原生输入/截图途径绕过限制，也未打开DOM预览冒充本轮原生验证。以下仍pending：实际慢快拖与窗口外松手立即停位移；失捕获/失焦/Escape；眨眼/wink中按下、40ms快松、620–700ms松手；带符号release、各阶段重抓；1×/2×浅深桌面的符号阶段、入口接缝、闭眼/wink首60ms后回正、衣摆回基础层与退出可达。

建议PM只接收DEV两笔实现与相应文档/QA报告，在当前集成基线上构建显式候选供用户验收。保留用户已认可的美术及既有接缝/透明点披露。没有新增动作、漂浮、联动、持久化、自启或发布；默认包推广另由PM决定。本任务交付后停止。

QA交付在 `codex/acceptance-matrix`，沿用 Draft PR #6：https://github.com/Tc2006415/aemeath-desktop-pet/pull/6。只选择本次QA提交，不合并QA分支历史素材。固定QA提交哈希随对话交接提供。
