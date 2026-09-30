# 单任务模拟状态契约 v1

状态：INT-002 v1.0 候选规格，待 PM 接受；2026-09-16。运行方向依据 PM 决策 `bf673927d3d88a6da071bfe49c3ec1aaa4fadb2b`：独立 Windows 桌宠、首版只展示一个选定任务。本文件不是运行实现或真实 Codex 接口承诺。

专业输入：DEV `02626be7ab5ec947e702a9d85612e91045959e93`（C1–C4/B3–B4）、ART `d54730bfde5fc666f93e3f3a4ce96298b8f946cb`（播放与业务边界）、INT `4782cd5c5fd7d5c18a96526a89e8767caf080896`（证据和来源限制）、QA `841021ebd13cbfbb4fe85c05f8a20f80b338160f`（D1–D4/A01–A11）。旧提案多任务聚合不进入本版。下文为单一推荐，PM 接受后才可作为实现基线。

## 1. 所有权与时间

- 来源适配器只将模拟器当前状态归一化，不去重、不判过期、不选择动画。只绑定一个 taskId；切换任务等同重新绑定，不保留另一任务状态。
- **联动模块的唯一归约器**持有连接代次、序号/ID 账本、轮次基线、状态有效期和提示消费记录。程序不得另建 TTL 或去重表。
- 程序表现层持有 `normal / dragging / releasing`，覆盖角色表现；期间照常提交事件、获取归约结果。放下结束再读最新结果，不使用松手时缓存。捕获丢失也结束拖动；若宿主不能播放放下片段，立即结束覆盖并重新读取。
- 播放器只播放或停止片段，报告首帧实际启动、结束/中断；不解释任务状态或有效期。动作名和帧时长由素材契约决定。
- 所有操作在同一本地串行调度域执行。调度器采样非递减单调毫秒 `now`（非负安全整数），测试可注入同一虚拟时钟；来源不能提交 now。每个输入、读取、开始提示前先处理 `now >= deadline` 的到期；同毫秒输入按入队顺序处理。墙钟只用于诊断。
- 休眠恢复、时钟倒退或重启不恢复旧计时器：立即失去基线，停止提示并要求新绑定。归约器记录不落盘。到期检查不得依赖帧结束，宿主应按 nextDeadline 调度唤醒；被系统暂停时恢复的第一操作先失效再绘制。

| 项目 | v1 模拟值 | 起点及达到边界的行为 |
| --- | --- | --- |
| 心跳发送间隔 H | 5000 ms | 模拟源绑定后每 5000 ms 发送，发送节奏不是有效性保证 |
| 链路 C | 15000 ms | 绑定时或最近一次接受的新序号消息的本地接收 now 起算；到期撤销连接与基线，unknown，必须重新绑定 |
| 业务 T | 30000 ms | 最近一次接受的 transition 或权威 snapshot 的本地接收 now 起算；heartbeat、重复、拒收消息均不续期。到期 unknown，需新绑定/快照恢复 |
| 提示资格 P | 5000 ms | 首次接受的当前轮次 completed/failed **transition** 的 now 起算；快照、重复、同终态确认不重置。到期停止正在播放的提示并撤销未播放资格 |

链路/业务/提示是独立时钟。提示到期不会将仍有效的 completed/failed 改成 idle/unknown：回中性姿态，保留“本轮正常结束 / 本轮失败”的模拟状态标识，直到业务失效或新的合法状态。失去业务有效性必须 unknown。此选择收敛 DEV C3 的标识时长歧义，替代旧 INT 提案的“5 秒展示窗口”；5 秒仅限制提示动作，不等于终态事实有效期。这些值仅用于模拟，不声称真实来源具有心跳或延迟保证。

## 2. 绑定、身份与完整字段

可信宿主调用 `BindMock(sourceId, taskId, now)`，生成每次不复用的 `bindingId`（进程生命期内唯一）并创建新 epoch；本版用 bindingId 同时代表选择代次和连接代次，不再增加第二个 epoch 字段。返回绑定句柄；事件提交必须持有此句柄。解绑、重连、换源、换任务、故障重同步都调用该方法生成新绑定，清除旧状态和资格，初始 unknown/awaiting-baseline。

`sourceKind` **不在事件载荷内**。只有本地宿主注册的模拟适配器能取得绑定句柄，输出恒标 `mock`；没有 real 注册入口。任何带 `sourceKind: real` 的载荷按未知字段拒收。无来源时输出 sourceKind=`none`、unknown。身份字符串为 1–64 个 ASCII 字符 `[A-Za-z0-9_-]`；eventId 例外可含冒号，长度至多 96。

事件是严格 JSON 对象，无额外字段、无重复键；UTF-8 至多 4096 字节。数字必须为安全整数（0 至 9007199254740991），不接受字符串化数字。所有下列公共字段必填：

| 字段 | 类型和约束 |
| --- | --- |
| `version` | 整数，只能为 1 |
| `bindingId` | 字符串，必须匹配宿主句柄；仅比较不能替代持有句柄 |
| `eventId` | 字符串，严格等于 `bindingId + ":" + sequence` 的十进制规范形式，无前导零；同绑定中不可复用 |
| `sequence` | 整数，从 1 连续增长，heartbeat 也占序号 |
| `kind` | `snapshot / transition / heartbeat` |
| `taskId` | 字符串，必须等于绑定任务 |
| `occurredAt` | null 或严格 UTC 时间 `YYYY-MM-DDTHH:mm:ss.sssZ`，日期有效；只作诊断，不参与排序、TTL 或资格。未来/过去时间不延长任何期限 |

snapshot/transition 额外且必须包含以下全部字段；heartbeat 禁止携带这些字段：

| 字段 | 类型和约束 |
| --- | --- |
| `turnNumber` | 整数，任务内轮次单调递增，0 表示尚无轮次 |
| `turnId` | turnNumber=0 时为 null，否则为身份字符串；同轮次不变，新轮次不得沿用当前 ID |
| `state` | `idle / working / waiting / completed / failed / unknown` |
| `reason` | 严格匹配状态：idle=`none`；working=`none`；waiting=`approval` 或 `user-input`；completed=`turn-completed`；failed=`turn-failed`；unknown=`unavailable` 或 `interrupted` |

turnNumber=0 只允许 idle/unknown-unavailable；其他状态以及 unknown-interrupted 要求 >0。`completed` 仅代表本轮明确正常结束；工具单次失败不等于 failed；中断映射 unknown/interrupted。系统产生的 `disconnected / stale / desynchronized` 等原因只出现在输出，不能由来源伪造。

## 3. 权威快照、轮次及接收规则

这里的“权威”只指**绑定的模拟器**从其当前状态存储即时读取，不指真实 Codex。每次新绑定要求其重新读当前任务并发送 sequence=1 的 snapshot，不能把已排队事件或磁盘缓存改标签充作快照；取快照与分配后续序号在源端原子串行执行。适配器本版只接即时本地模拟事件，不接历史流/延迟重放作为新转换。归约器无法仅靠 JSON 证明来源诚实，这属于本地模拟器契约，未来真实源需单独证明。

有基线后，同绑定可用新序号的即时 snapshot 确认当前状态并刷新 T，供长等待/工作使用；它不是修复缺口的捷径。所有 snapshot 都不创建提示。模拟器可每 10000 ms 取一次当前快照以维持长状态，心跳仍独立；这是源端调度建议，不另加归约器阈值。

归约器依次处理：

1. 到期优先。已故障/失效的绑定拒收其后全部事件；返回重同步请求，不允许恰好到期的 heartbeat/快照“救活”旧绑定。
2. 结构、句柄、版本、字段或 taskId 不合法：拒收且不变更基线、序号、期限；记录类别，不记录原载荷。错误来源不能破坏当前有效任务。旧绑定消息直接拒收。
3. 对已记录 eventId 比较完整解析后字段（键顺序无关，值严格相同）：完全相同为重复，忽略且不续任何期限；任一值不同为冲突，置 unknown/desynchronized，停止提示并撤销绑定。账本保存当前绑定所有已接受事件（最多 4096 条）；第 4097 条之前要求新绑定，不静默淘汰后宣称仍能识别冲突。单绑定内存上限约为 4096×4096 字节外加索引，待实现选择紧凑表示。
4. 非重复消息 sequence 必须等于上次+1。缺口或不存在账本的回退均视为 desynchronized，不缓冲排序；撤销绑定并请求新快照。此处理是有序本地模拟流的最小方案，不承诺任意网络乱序容错。
5. 第一条必须 sequence=1、kind=snapshot，建立任意合法当前轮次基线；初始 heartbeat/transition 是协议失步。heartbeat 只刷新链路，不改变业务或轮次。
6. 后续 transition 的新轮次只能 `turnNumber=当前+1`、新 ID、state=working；允许从任意旧轮次状态开启新轮次。后续 snapshot 可跳到更大的轮次但不得降低；ID 必须不同，清除旧提示，建立无庆祝基线。任一消息同号异 ID、较低轮次或非法状态跳转均失步并撤销绑定；不能猜它是新工作。
7. 同轮次状态转换按下表。接受的非重复状态消息刷新 C 和 T。只有**非终态→终态的 transition**生成提示 token；新序号相同终态确认只刷新业务，绝不生成第二次提示或续 P。同状态 snapshot 保留已有 token 的消费/原截止时间；首次从 snapshot 看到终态，记为 suppressed，后来的同终态 transition 也不庆祝。

| 当前轮次状态 | 同轮次允许后继（transition 或 snapshot） |
| --- | --- |
| idle（含轮次 0） | idle、unknown；工作开始必须升轮次 |
| working / waiting | working、waiting、completed、failed、unknown |
| unknown/unavailable | working、waiting、completed、failed、unknown；仅限仍有有效基线且该轮次此前未终结 |
| unknown/interrupted | 同状态或 idle；视为轮次已终结，不可恢复工作 |
| completed / failed | 同一终态、idle、unknown；不可互改、不可回 working/waiting |

归约器另保存当前轮次的终结锁：一旦 completed/failed/interrupted，随后 idle/unknown 不清锁；只允许相同状态确认、idle 或 unknown，不能再次终态提示或重新工作。锁只有更大轮次/新绑定的权威基线可替换；新绑定仍不从快照庆祝。新事件实际改变业务状态、进入新轮次或失效时取消旧提示；heartbeat、同状态快照、相同终态确认及重复不取消正在播放的提示。state/reason 都相同才算同状态。

## 4. 归约器与表现层契约（本地逻辑调用，不指定 IPC）

输入：

| 调用 | 行为及返回 |
| --- | --- |
| `BindMock(sourceId, taskId, now)` / `Unbind(now)` | 前述选择/取消选择，停止旧提示，返回 View |
| `Receive(handle, event, now)` | 前述归约，返回 `{disposition, view}`；disposition=`accepted / duplicate / rejected / resync-required` |
| `Disconnect(handle, now)` | 匹配当前绑定时立即 unknown/disconnected 并撤销绑定；旧句柄无影响 |
| `SuspendOrResume(now)` | 宿主在暂停/恢复通知时提交，立即 unknown/suspended、撤销绑定并停止提示。单调时钟倒退由任一调用入场检查自动转 unknown/clock-error，不接受该调用的业务输入 |
| `Read(now)` | 先到期，再返回 View；宿主用相同调用处理定时唤醒 |
| `TryStartPrompt(token, startFrame, now)` | 下述原子开始及实际消费，返回 `started / denied / not-started` 与最新 View |
| `EndPrompt(token, outcome, now)` | outcome=`finished / interrupted`；仅结束当前 playing token，不改变业务；旧 token 或仍 eligible 的 token 回调忽略，返回 View |

View 全字段（值由归约器生成，不能从输入载荷照抄）：

未绑定时身份/轮次/期限/prompt 均为 null、sourceKind=none、state=unknown、reason=unbound、synchronized=false、baseVisual=neutral、needsBaseline=false。新绑定时绑定身份已知、轮次为 null、reason=awaiting-baseline、needsBaseline=true，仅链路期限存在。缺口/冲突输出 reason=desynchronized，容量触顶为 capacity；链路超时为 disconnected、业务超时为 stale。失效清空全部期限和 prompt，但保留绑定身份和最近轮次供诊断；synchronized=false、needsBaseline=true。若同刻多个期限到达，链路失效优先于业务失效，二者均优先于仅提示到期。

| 字段 | 类型、含义 |
| --- | --- |
| `bindingId / sourceId / taskId` | 身份字符串或 null（Unbind 后）；已失效绑定可保留身份作诊断，但不再接受事件 |
| `sourceKind` | `mock / none`，宿主决定；即使 mock 掉线也保持模拟标识 |
| `turnNumber / turnId` | 当前基线轮次或 null；失效保留也不能作为当前真实状态 |
| `state` | 六态之一；失效为 unknown |
| `reason` | 来源合法 reason，或系统 `unbound / awaiting-baseline / disconnected / stale / desynchronized / suspended / clock-error / capacity` |
| `synchronized` | boolean；仅已接受基线且未失效为 true；来源主动 unknown/unavailable 可为 true |
| `baseVisual` | `idle / working / waiting / neutral`；终态/unknown 为 neutral，不绑定具体素材标识 |
| `prompt` | null 或 `{token, state, phase, deadlineMonoMs}`；state 仅 completed/failed，phase=`eligible / playing`；无排队列表 |
| `linkDeadlineMonoMs / businessDeadlineMonoMs` | 单调截止时间或 null；失效清空 |
| `nextDeadlineMonoMs` | 尚有效的链路、业务、提示截止时间的最小值，或 null；宿主据此唤醒，不自行计算 TTL |
| `needsBaseline` | boolean；无绑定为 false，新绑定待快照/失步/过期为 true；true 时宿主按绑定流程同步，不能回放缓存 |

token 是归约器生成的不透明、不可复用字符串，逻辑身份对应绑定+任务+轮次+首次终态事件。消费记录只在归约器；读取 eligible 不算消费。

开始播放必须解决“验证资格”和“实际首帧开始”之间的竞争：**本版要求同一调度域内同步原子交接**。表现层仅在 normal、素材就绪且准备提交首帧时调用 TryStartPrompt。归约器先处理到期、核对 token 仍 eligible，然后同步调用宿主提供的 startFrame；该回调不得 await、阻塞或重入归约器，只执行首帧提交并返回 boolean。返回 true 表示首帧已交给播放器开始展示，归约器当场置 consumed/playing；false 或抛出失败表示未开始，资格保留到原截止时间，宿主不得忙循环重试。回调失败必须保证未提交首帧，否则违反契约。此处“实际开始”指播放器首帧提交，不要求证明显示器扫描输出。

宿主必须保证该原子交接时交互阶段仍 normal；其他事件/拖动输入只可在它前后处理，不能穿插。异步进程传输不在 v1 范围内；未来若必须跨进程，需 PM 接受新握手协议，不能把“已排队”回执当作开始。

| 播放期间发生什么 | 唯一行为 |
| --- | --- |
| 提示 P 到期 | 当次 Read/输入先清 prompt，表现层立即停止；业务仍有效则 neutral+原状态标识，不回 idle |
| C/T 到期或明确断连 | 清 prompt，停止，unknown；必须新绑定恢复 |
| 新合法事件改变状态/轮次 | 立即停止旧提示，应用新 View；已消费旧 token 不再回来 |
| 同状态权威快照、同终态确认、heartbeat、重复 | 不重启、不延长提示 P，保持播放至原期限/自然结束 |
| 提示自然播完 | EndPrompt(finished)，neutral+仍有效的状态标识；无再次播放资格 |
| 开始拖动或素材/窗口中断 | 立即停止并 EndPrompt(interrupted)；消费不撤销，放下后不重播 |
| 放下中收到终态 | 仅保留 eligible，放下结束 Read 再尝试；到期则不播放。再次抓取只改变覆盖层 |

任何收到的新 View 若无原 playing token，表现层必须停止该 token 的播放器；旧动画结束回调不得改变新 View。状态文字/模拟标识在拖动覆盖时仍及时更新；拖动动画可继续，不能用它隐藏 unknown。

## 5. JSON 示例与错误示例

合法基线（绑定句柄由宿主创建为 b1，选定模拟源 s1/task-A；接收 now=0）：

```json
{"version":1,"bindingId":"b1","eventId":"b1:1","sequence":1,"kind":"snapshot","taskId":"task-A","occurredAt":null,"turnNumber":1,"turnId":"turn-1","state":"working","reason":"none"}
```

合法终态（接在上述基线后，now=1000；P 截止 6000，T 截止 31000）：

```json
{"version":1,"bindingId":"b1","eventId":"b1:2","sequence":2,"kind":"transition","taskId":"task-A","occurredAt":"2026-09-16T20:00:01.000Z","turnNumber":1,"turnId":"turn-1","state":"completed","reason":"turn-completed"}
```

合法心跳（now=5000，只把 C 更新为 20000）：

```json
{"version":1,"bindingId":"b1","eventId":"b1:3","sequence":3,"kind":"heartbeat","taskId":"task-A","occurredAt":null}
```

错误示例 E1：JSON 合法，但多了伪造 sourceKind。拒收，不推进 sequence 或刷新链路；它不能变成 real。

```json
{"version":1,"bindingId":"b1","eventId":"b1:3","sequence":3,"kind":"heartbeat","taskId":"task-A","occurredAt":null,"sourceKind":"real"}
```

错误示例 E2：在合法 b1:2 后重送相同 ID 但 failed，不是普通重复；冲突导致 unknown/desynchronized、撤销 b1。

```json
{"version":1,"bindingId":"b1","eventId":"b1:2","sequence":2,"kind":"transition","taskId":"task-A","occurredAt":"2026-09-16T20:00:01.000Z","turnNumber":1,"turnId":"turn-1","state":"failed","reason":"turn-failed"}
```

错误示例 E3：先只收 b1:1 再收下例，结构和 ID 合法但缺 sequence=2；unknown/desynchronized，不等待迟到 2 修补。

```json
{"version":1,"bindingId":"b1","eventId":"b1:3","sequence":3,"kind":"heartbeat","taskId":"task-A","occurredAt":null}
```

其他确定性错误：completed+turnNumber=0、waiting+reason=none、heartbeat 携带 state、非法日期、字符串 sequence 均为结构拒收；同轮次终态后 working、较低 turnNumber 是语义失步。occurredAt 即使为有效格式的未来日期也仅保留诊断，绝不能影响本地期限。

## 6. 最小行为测试向量（规格预期，尚未执行）

每行独立重置；时间均为本地单调毫秒。S/T/H 分别为 snapshot/transition/heartbeat，省略公共字段沿用合法示例；每个新消息用连续 sequence 和匹配 eventId，除非特意制造异常。除标明无心跳外，长场景每 5000 ms 接受 H，维持链路但不刷新业务。Start 表示 TryStartPrompt 的首帧成功；Read 包含到期。状态检查与模拟标识常驻是共同断言，不重复穷举颜色/帧数。

| ID | 输入 | 预期 |
| --- | --- | --- |
| V01 | 0:S idle/轮次0；100:T working/轮次1；200:T waiting；300:T working；400:T completed；401:Start；500:End(finished) | 六态中正常路径，500 为 completed+neutral、无 prompt；新轮次2工作→failed 同样可一次提示；unknown 用其他失效行覆盖 |
| V02 | 0:S working；1000:T completed；拖动遮挡；5999:release 结束并 Start | 首帧可开始并消费；6000:Read 立即停止，仍 completed；另组 release 恰在6000结束则 denied、从未消费 |
| V03 | 0:S working；1000:T completed；1001:Start；1100:拖动/End(interrupted)；1200:放下结束 | 不重播已消费提示；另一组1001 startFrame=false，1200首帧成功则只在1200消费，P仍6000 |
| V04 | 0:S working；1000:T completed（拖动中）；1200:T working/轮次2；1300:release 结束 | working/轮次2，无旧庆祝；若旧提示已playing，也在1200停止；旧token结束回调不覆盖working |
| V05 | 0:S working；1000:T completed；重复相同ID/载荷；2000:新序号相同completed；3000:S相同completed | 重复不续C/T/P；后两条可续C/T，但P仍6000、token不变；消费至多一次 |
| V06 | 0:S completed/轮次7；1000:T同终态；2000:新绑定b2并收S completed/轮次7 | 两次历史基线均不庆祝，同终态转换也不生成资格；旧b1事件与token拒绝。源切换和任务切换走相同新绑定规则 |
| V07 | 0:S working；仅H持续至30000，29999/30000:Read | 29999 working；30000 unknown/stale；同刻旧绑定S不能恢复，需新绑定和即时S |
| V08 | 0:S waiting；无H；14999/15000:Read；另组1000:Disconnect | 分别waiting/unknown-disconnected；显式断连1000即unknown；停止所有提示，不待T |
| V09 | 分别运行 E1、E2、E3；E3后补发sequence2；或同轮次completed后新序号working | E1拒收无状态副作用；E2/E3/非法跳转失步撤销绑定；补发不能恢复，要求新基线 |
| V10 | 0:S working；1000:T completed；1001:Start；1100:Disconnect；或1100休眠恢复通知 | 立即停止提示并unknown，重连S completed不补播；墙钟跳变本身不影响期限，单调时钟倒退则unknown/clock-error |
| V11 | 0:S working；1000:T completed；1001:Start；2000:S同状态；4000:End(finished)；6000:Read；31000以前新S持续保鲜 | completed标识持续，prompt永不重新出现；动画结束/P到期不制造idle；停止所有状态快照后最后一次确认+30000即unknown |

未来实现时优先将上述风险向量转成归约器测试，并以真实 Windows 窗口核对 V02–V04；此轮仅审核字段/示例/预期一致性，没有写测试程序，不宣称向量通过。多任务、网络重排重试、真实 Desktop 六态验收不属于这些模拟测试。

## 7. 接受与交接

本规格收敛了轮次、阈值起点/等号、快照、顺序冲突、来源绑定及提示消费，不需要用户重复决定独立运行方向。无阻碍文档交付的问题。请 PM 统一接受本候选及与 DEV/ART 002 的调用/素材映射差异后再派实现；特别确认本地同步首帧交接和“提示5秒、业务标识30秒可由权威快照续期”的区分。真实来源接入须独立任务验证受支持入口、仅状态投影和事件保证，不能直接将本 mock 绑定改成 real。

本轮只提交本规格及自身旧提案的状态指引；未修改公共决策、其他角色文件或历史任务卡。既有来源调查不重做，任务卡不复制到 GitHub。文档检查命令与结果在任务对话交付；保留已有 Draft PR，不合并、不关闭 Issue，不自动启动工程。
