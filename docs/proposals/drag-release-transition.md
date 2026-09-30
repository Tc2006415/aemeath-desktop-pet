# 拖动松手衔接：显示帧驱动的 release 入口提案

状态：DEV-006 只读调查与方案，待 PM 接受；未实现、未变更公共契约、未制作补帧。关联程序 Issue #1，执行范围以本次对话任务卡为准。生产实现基准为 `d80c30294fc5369ba465d28a73d6dc5f030c1824`；调查时本地统筹分支头 `179da56`，其 Host、Presentation、正式角色 manifest/frames 与 d80c302 比较无差异。没有合并 ART 分支或历史正式包。

## 结论与最小范围

建议：**松手立即停止窗口位移并释放捕获，以最后提交显示的完整帧选择一条预载的 release 单次序列。** 上扬入口增加少量真正画出的中间翼姿，回到已有收翼尾段。所有序列继续使用同一个单调时钟、同一个播放器实例编号机制；不新增第二个计时器、通用动作跳转图或位图插值器。

这不能仅改时间解决。ART013 的上扬端点与既有 release 首帧相距约 9–10 源像素；若保留中幅扇翼且希望将相邻收翼步进控制到约 3 px，必须提供中间翼姿。推荐先评估三个上扬回中位姿态，翼尖大致距中位 7、4、2 px；这是制作/验收目标，不是授权程序平移羽毛，也不是已有合格素材。下压→中位约 3 px 可先复用现有图，仍须实际视觉确认。

方案只解决松手入口。它不自动修复 ART013 hold 循环自身的上扬→中位大步进、720 ms 规律眨眼，也不承诺 release 中重抓后原有 pickup 首帧的视觉连续性。重抓必须仍立即取消收翼并响应新抓取，不能为视觉衔接延迟输入。

## 实际输入与问题位置

候选为 ART 提交 `390aeabb577448a30d5f1df002dc1294004cf763` 的 `assets/characters/aemeath-v1/source/art013-package/`，不是生产 0.3.0。其 manifest SHA256 为 `6DF3616190D43B977157D0A110F9B3A609599802BAABF1118AE3B2107E102ABF`，声明 packageVersion 0.4.0 / schemaVersion 1。已只读解析并计算：

| 动作 | 实际时序项 | 合计 |
| --- | --- | --- |
| pickup | neutral 80 → hold-surprise 80 → pickup-surprise 100 → hold-half 100 | 360 ms |
| hold | hold-half → hold-up-half → hold-mid-closed → hold-down-half，均 180 | 720 ms loop |
| release | hold-half 80 → release-closed 100 → release-half 120 → neutral 160 | 460 ms |

制作方 [视觉报告](https://github.com/Tc2006415/aemeath-desktop-pet/blob/390aeabb577448a30d5f1df002dc1294004cf763/assets/characters/aemeath-v1/source/art013-visual-review.json) 记录上扬松手瞬间收回约 9–10 px，下压/循环回首约 3 px；40 ms 快松手也被切为 hold-half。报告是网页模拟/边界抽样，不是原生鼠标验收。其 `art013-check-report.json` 的宿主证据是手动 hold 播放，不能证明实际 EndDrag 衔接通过。本轮逐张查看了候选 hold-up-half、hold-down-half、hold-half、pickup-surprise、release-closed PNG，确认姿态不同；没有独立重测翼尖 9–10 px，也没有把静态检查升级为动态验收。

以下行号均对应 d80c302：

| 代码证据 | 含义 |
| --- | --- |
| [PetWindow.cs:123](../../src/Aemeath.Host/PetWindow.cs#L123)，MoveDrag 的 125–133 行 | 只有 drag.Active 时才更新窗口位置。 |
| [PetWindow.cs:137](../../src/Aemeath.Host/PetWindow.cs#L137)，140–143 行 | drag.End 先清标记，再 ReleaseMouseCapture，再通知协调器、Draw；释放捕获会重入，但重复 EndDrag 被挡住。这个立即停止位移顺序应保留。 |
| [CharacterController.cs:43](../../src/Aemeath.Presentation/CharacterController.cs#L43)，45–49 行 | EndDrag 不携带当前显示帧；有 release 就固定 Select，否则 Idle。 |
| [Playback.cs:18](../../src/Aemeath.Presentation/Playback.cs#L18)，21–24 行 | 每次 Play 重设 started，并分配新实例；没有从某个 release 入口选择序列的能力。 |
| [PetWindow.cs:93](../../src/Aemeath.Host/PetWindow.cs#L93)，96–103 行 | 现有 Draw 重新 Sample，再用动作/帧号找 PNG、赋给 Image.Source；lastFrame 仅是日志去重字符串，不是受校验的姿态快照。 |
| [PetWindow.cs:87](../../src/Aemeath.Host/PetWindow.cs#L87)，91、119、143 行 | Rendering 和输入处理都可调用 Draw；不能把输入处理中的新 Sample 当作此前屏幕已显示的图。 |
| [CharacterController.cs:51](../../src/Aemeath.Presentation/CharacterController.cs#L51)，56–60、69–77 行 | 仅当前 expectedInstance 的自然完成推进阶段，release 后回 Idle 并重启 15 秒等待；应复用而非绕开。 |
| [PackageLoader.cs:33](../../src/Aemeath.Presentation/PackageLoader.cs#L33)，34、47、57、64 行 | 当前严格只接受 schema 1 及字段白名单，不能直接塞入新键；资源限额已有统一实现。 |

## 与纯素材修订比较

| 选择 | 能解决什么 | 剩余代价/问题 |
| --- | --- | --- |
| 纯素材：改固定 release 首帧或增加其后补帧 | 无代码/格式变化，能改善一个选定入口及其后运动 | 一个固定首帧不能同时等于中位、上扬、下压、neutral。补帧放在首次硬切之后，最先的 9–10 px 跳变仍在。 |
| 纯素材：将所有 pickup/hold 翼姿压回近似中位 | 固定入口更接近所有源姿态 | 牺牲用户已授权评估的中幅扇翼；即便选上下端的折中首帧，约 12–13 px 跨度至少一端仍距约 6 px。该量级推算以 ART 报告为前提。 |
| 本提案：源帧对应的预制 release 序列 | 首次切换保留源帧，随后用明确补帧分步收翼；快松手无需先展翼 | 需要很小的格式/播放器/宿主快照扩展和少量 ART 补帧，必须先由 PM 接受。 |

不建议等 hold 整轮结束再释放捕获；也不建议停住位置后继续播完原 hold 整轮再切换，因为原四帧上扬→中位的空间大步进仍存在且延迟随相位变化。单纯增加持续时间只把跳变推后，不能当作消除跳变。不存在从两张位图可靠自动推断羽翼骨架的现成接口，本轮也不引入这一能力。

## 拟议接口变化：只允许 release 的完整入口序列

以下名称和结构是**待审批草案**，不是已冻结 API，也不写入当前 manifest。

建议新加载器同时支持既有 schema 1 和新 schema 2；仅 schema 2 的 `actions.drag-release` 可增加 `entrySequences`：键为已校验的包内 PNG 精确路径，值为一条完整的 `{path, durationMs}` 帧数组。键表示源图，不使用“up/down”猜测、颜色识别、文件名硬编码或运行时位图近似匹配。每条数组第一个 path 必须与键相同，最终 path 必须与有效 neutral 帧相同。原 `drag-release.frames` 保留作手动播放及兼容入口。

这是同一个 release 动作的有限序列选择，不允许 nextAction、条件表达式、业务状态或新动作 ID。完整数组而非“前缀 + 跳转索引”可避免第二套拼接/时间来源；制作方可重复引用共享 PNG，不复制像素缓存。未来 manifest 中的 durationMs 是唯一播放时长来源，下节数值只是此次建议。

配套最小变更范围：

1. **加载器**：解析/预载同一动作的入口表；schema 1 规则不变，旧宿主安全拒收 schema 2。entrySequences 键无重复、路径安全、首尾约束、字段类型与 duration 均严格校验。每条可选 release 序列仍最多 64 项/60000 ms；基础 frames 与所有入口序列的时序项合计计入原 256 项上限，图片按不同路径计入原 128 张/8 MiB 等上限，不放宽任何限额。任一入口引用坏 PNG 则停用整个 drag-release（不是跳过该补帧）；坏 neutral 仍整包拒绝。元数据/路径错误仍整包拒绝。
2. **播放器**：允许在现有动作 ID 下启动一条已加载、不可变的入口序列；分配一个全新的 PlaybackId，统一半开区间、取消和仅一次完成。一个 release 不拆为多个有独立完成回调的小动画。采样结果需能给出本序列的有效 frame path；宿主不能继续用 `package.Clips[action].Frames[index]` 索引基础序列来画入口变体。
3. **宿主→协调器**：EndDrag 接受“最后提交帧快照”（候选字段：包加载代次、实际 path、PlaybackId、帧序号、提交序号）；协调器必须核对是当前包内已缓存图，不能从输入传入任意路径。需要新的按源图选 release 的内部调用；不改变业务状态模块，因为本轮仍无业务状态。
4. **显示采样**：输入事件只改变播放请求；显示提交由 Rendering 路径集中处理并保存实际交给 Image.Source 的帧。不能在松手时先 Sample(now) 把理论下一帧冒充源图，也不能在按下后、下一次绘制前把未提交的 pickup 当作源图。

包加载代次校验用于拒绝旧包快照；PlaybackId 标识显示来源，不应简单要求它等于最新请求 ID：按下后尚未绘制时，真正最后提交的可能仍是此前 idle/smile，这正是需要保存它的原因。只有 Host 当前保存的提交记录可供选路，外部旧回调不得自行注入快照。

WPF Source 赋值/Rendering 没有在现有代码中提供“该帧已被显示器呈现”的回执。上述“显示帧”严格指最后提交给渲染的帧，不能宣称掌握物理屏幕扫描状态。必要原生录屏应核对输入前画面与所选入口；合成延迟或 UI 阻塞仍可能导致跳过某些中间帧，必须按既有单调时间跳帧语义报告，不能以卡死时钟掩盖。此方案缩小源姿态选错风险，不保证任意阻塞下的逐帧可见性。

## 建议精确时序与边界

令 R 为现有 release 完整四项 `[hold-half:80, release-closed:100, release-half:120, neutral:160]`，合计 460 ms。B7/B4/B2 是待 ART 制作的上扬回中位中间图，身体/脸保持与上扬源图一致，不允许位图模糊插值。下表每行都代表将来 manifest 中一条完整数组，不是运行时猜测算法。

| 最近提交的源图 | 完整选路（括号为 ms） | 松手至逻辑回 idle |
| --- | --- | --- |
| hold-up-half | 源图(40) → B7(40) → B4(40) → B2(40) → R | 620 ms |
| B7 / B4 / B2 | 当前图(40) → 尚未经过的下一级 B 图各(40) → R | 580 / 540 / 500 ms |
| hold-half | R，第一项本来就是源图 | 460 ms |
| hold-down-half | 源图(40) → R；约 3 px 回中位待视觉确认 | 500 ms |
| hold-mid-closed | 源图(80) → release-closed(100) → release-half(120) → neutral(160) | 460 ms |
| hold-surprise / pickup-surprise | 源图(40) → R；脸和身体的衔接另须看图确认 | 500 ms |
| neutral | neutral(160)，随后 idle-soft | 160 ms |
| release-closed / release-half | 从同名源图开始的已有收翼尾段：100+120+160 / 120+160 | 380 / 280 ms |
| soft-light / soft-peak / smile-half / smile-closed | 源图(40) → neutral(160)，用于抓起尚未呈现就松手 | 200 ms |

任意输入可以落在这些源图上，包括 release→重抓→下一次 Rendering 前再松手，所以不能仅给四个 hold 图做映射。此候选共有原 13 张图，加拟议 3 张 B 图，共 16 张；覆盖这 16 个源图的入口表合计 63 个时序项，加原动作 25 项共 88，仍低于 256。资源/格式与身体衔接检查不因表格成立而自动通过。

以松手处理时刻 t 为起点，先停止位置更新，首图 `[t,t+40)` 保持真实源姿态，上扬随后三张补帧各 40 ms，原 R 从 t+160 开始；t+620 完成一次并回 idle。这里的保持用于使源帧成为合法起点，**消除大空间跳变依靠新增姿态而非这 40 ms 等待**。每一级翼尖步进目标约 ≤3 源像素，需逐帧实际量测；如果补帧不达标，不能仅调长时间过关。

40 ms 快松手：pickup 的 neutral 首项本来持续 80 ms；若它已提交，则从松手起 neutral(160)，不切到展翼 hold-half。按下 t=0、松手 t=40、正常采样时 t=200 回 idle，新的笑脸等待从 t=200 起算，t=15200 才可触发。若 pickup 尚未提交，则按实际保存的 idle/smile 图走 200 ms 分支，不假称已经显示 neutral。

release 期间再抓：成功 CaptureMouse 后立即请求新 pickup，旧 release 全序列取消，不等待 620 ms；正常窗口运动仍由抓取标记控制。此处保持既有 pickup 从第 0 帧开始的语义，未承诺同时解决反向入口视觉。若用户也要求该方向连续，需另立受控范围，不能偷偷加入此次实现。

capture loss / 失焦 / Escape 走同一幂等结束入口：先将 Host 最后提交快照复制为局部值（不重新 Sample），成功清除 drag.Active 后立即释放捕获，再把该快照交给协调器，只选一次 release。重复 EndDrag 不重启计时；后续 MouseMove 因标记已清不能再定位。模式切换、换包、退出则取消本序列并遵循既有新模式/包/退出流程，不让旧包过渡残留；主屏变化的窗口安全重定位也不能等待收翼结束。

## 兼容与错误回退

- 正式 0.3.0 是 schema 1 且无拖动三动作：继续现有 neutral 抓取回退，松手直接 Idle；不制造一条空 release，也不等待不存在的完成。
- 旧 schema 1 包有 release：沿用原固定入口，明确只兼容原行为，不声称已消除旧包跳变。手动诊断播放同样用原 frames，不自动改入口。
- schema 2 入口表没有匹配有效源图：立即用原 frames，并记录一次“无姿态入口，固定回退”；该路径不计为连续视觉通过。所推广角色包应要求覆盖全部可显示图，否则不接受其“任意相位连续”声明。
- 快照缺失、包代次不匹配：不读取旧图片；用当前包原 release 或无 release 时 Idle，保留未知/未连接业务标签。缺帧导致整个 release 被停用时也走 Idle，绝不无限重试或等待。
- 上一 pickup/hold/release 实例不能因迟到完成而改变新选择；保留现有 expectedInstance 隔离，并将包代次一起用于未来任何异步通知。当前播放器是同步采样，没有需要恢复的历史完成队列。

## 接受后才执行的测试差分

不重测未变 DPI/几何全矩阵。新增测试围绕入口选择、帧缓存和取消，使用真实播放器加可控时钟；原生输入证据另列。

| 用例 | 与当前断言的差分 |
| --- | --- |
| 40 ms 快松手 | 由固定 hold-half 改为已提交 neutral；t=40 不再移动窗口，t=199 仍收尾，t=200 Idle；若源帧未提交则按旧 idle/smile 快照分支。 |
| 四个 hold 相位 | 各相位首/末 ms 松手，首个 release 图 path 与最后提交图一致；上扬 620、中位 460、闭眼中位 460、下压 500 ms。 |
| 边界未绘制 | 时钟已跨 hold 的 180/360/540/720 ms 边界，但最后提交仍上一帧，必须按该帧选路；下一次渲染不能用旧 sample 覆盖 release。 |
| 中间图与快重抓 | 对 B7/B4/B2、release 尾图做重抓→未绘制再松手；全部有明确入口；新 pickup 立即获新 PlaybackId，旧 release 到期不回写。 |
| 完成身份/掉帧 | release 总时长前 1 ms、正好边界、越过全部时长：最多一个完成并回 Idle；不同入口总时长使用各自数组；不把桥接帧结束当作动作完成。 |
| capture loss 和重复结束 | mouse-up、capture-loss 顺序交换/重复，窗口位置冻结、捕获释放、序列 ID/起点只更新一次；补帧继续播放不继续拖动。 |
| 换包/模式/退出 | 旧快照失效；旧包完成不得覆盖新包，0.3 缺动作直接回退，自动→手动不再自动播放旧过渡。 |
| 解析/降级 | schema 1 原行为、schema 2 首尾/重复键/越界/坏图/时序总量；每条入口首图命中、显示索引走有效序列而非基础 frames。只加新字段路径相关检查。 |
| 原生/视觉 | 1×和既有整数倍率下，对上扬/下压/中位/闭眼中位及40ms短抓代表序列录像，包含指针和自身帧日志；核对松手即停止位移、第一图连续、逐级翼尖与脸/身体无额外抖动。没有工具/设备时保持待验。 |

现有 [CharacterControllerTests.cs:48](../../tests/Aemeath.Presentation.Tests/CharacterControllerTests.cs#L48) 早松手、56 行重抓、66 行缺动作测试的取消原则应保留；其样例 release 总长 280 ms 不是新包固定值。新增入口夹具必须显式携带各自 duration，而非修改一套全局 release 常量。

## 本轮验证、限制与交接

实际完成：读取 README/流程/交接/ADR 0003、统筹当前状态、指定候选 manifest、ART013 visual-review/check-report 与制作记录；按固定生产代码行追踪捕获→EndDrag→Select→Sample→Image.Source；解析六动作时序、核对候选 manifest SHA；查看五张实际候选 PNG；比较 d80c302 与统筹当前生产代码/正式帧无差异。新增时序表 16 路、63 项与合计时长作算术核对，**不是播放器实现测试或新动画运行结果**。

本轮不构建、不运行新播放器、不导出/绘制中间帧，不修改生产或候选文件。仅提交此提案；`git diff --check` 与新增路径范围检查作为文档交付验证。

PM需明确接受：是否保留中幅上扬并采用三个补姿；是否批准 schema 2 的 release 入口表及内部显示快照/序列采样扩展；是否接受160–620 ms不同入口收尾及上述像素步进作为待实测目标。随后分别派 ART 与 DEV 实施卡，并由 QA验证差分。未经此裁决，不推广ART013、不把新键写进schema 1、不开始下一阶段。
