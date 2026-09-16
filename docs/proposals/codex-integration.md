# Codex 联动：来源调查与状态协议提案

状态：提案，未接受；调查日期：2026-09-16。关联 [Issue #3](https://github.com/Tc2006415/aemeath-desktop-pet/issues/3)。依据 ADR 0001，技术栈、共享接口及合并由统筹决定。本文不建立正式跨模块接口，也不包含运行时代码。

## 结论与建议

**存在有文档的 Codex 事件协议，但尚未证实外部 Windows 桌宠能以受支持、仅状态的方式订阅当前 Codex Desktop 已有任务。** 本机确认有 `codex-cli 0.153.4`，能导出包含状态事件的协议 schema；这证明本机具有协议定义，不证明完成了连接、权限、订阅或真实事件验证。

建议 M2 保留独立桌宠及显式模拟模式，真实来源未接通时显示“未连接 / 状态未知”。M4 以真实来源验证为入口条件，不能凭进程存在、窗口标题、文件更新时间或长时间静默推断任务完成。文中 `completed` 只表示一个 Codex 轮次明确正常结束，不表示用户整个目标、测试或交付已经成功。

外观仍遵循游戏内像素小爱与 `assets/concepts/aemeath-game-style-v2.png`。本任务仅阅读 `docs/aemeath-reference-notes.md`，未重新观看视频或检查素材，不提出已验证动作、帧数或图集要求。

## 调查边界与证据

已读 AGENTS、README、development-workflow、task-briefs、唯一现行 ADR 0001 和参考笔记；通过已登录 GitHub 页面读取 Issue #3，验收包含六种状态、事件时间、任务标识、异常顺序、多任务和诚实降级。未读取会话日志、完整对话、凭据、Cookies 或账号数据库；未修改 Codex 文件或配置，未安装 hook，未开启服务、监听端口、自启动或远程控制。

### 本机可复核结果

以下命令在本任务独立 Windows worktree 执行，除特别标注外退出码为 0。

| 检查 | 实际结果 | 能证明什么 / 不能证明什么 |
| --- | --- | --- |
| `git status --short --branch`、`git worktree list` | 初始 HEAD 为 `369b826`，worktree 干净且独立 | 未与其他开发任务共用 checkout |
| `codex --version` | `codex-cli 0.153.4` | CLI 版本；不能代替 Desktop 版本 |
| `codex app-server --help` | 有 stdio、Unix socket、WebSocket 选项，命令标注 experimental | 有启动入口；未启动服务器 |
| `codex exec --help` | 有 `--json`，说明输出 JSONL 事件 | 有流式输出选项；未执行模型任务 |
| `codex app-server daemon --help`、`codex app-server proxy --help` | 前者有 daemon 管理子命令，后者代理控制 socket | 帮助存在不等于 Windows 支持 |
| `codex app-server daemon version` | 退出 1：`daemon lifecycle is only supported on Unix platforms` | 该 daemon 查询路径在此 Windows CLI 不可用；不推断所有 app-server 传输不可用 |
| `codex app-server generate-json-schema --out <临时目录>` | 成功导出默认 schema，无 `--experimental` | 可离线核对字段，不含会话内容；未建立连接 |
| `git ls-remote --heads origin` | 成功读到 main | Git 远程读取可用；当时尚未验证推送 |

实际临时目录为 `$env:TEMP/aemeath-codex-schema-01534`，生成文件不提交仓库。复核命令（只生成协议定义）：

```powershell
$schemaDir = Join-Path $env:TEMP 'aemeath-codex-schema-01534'
codex app-server generate-json-schema --out $schemaDir
Get-Content (Join-Path $schemaDir 'v2/ThreadStatusChangedNotification.json')
Get-Content (Join-Path $schemaDir 'v2/TurnCompletedNotification.json')
Get-Content (Join-Path $schemaDir 'v2/ThreadReadParams.json')
```

本机 schema 的具体证据：

- `ThreadStatusChangedNotification` 必须有 `threadId`、`status`；状态为 `notLoaded`、`idle`、`systemError`、`active`。active 标记包含 `waitingOnApproval`、`waitingOnUserInput`。通知本身没有事件 ID、序号或时间字段。
- `TurnCompletedNotification` 必须有 `threadId`、`turn`。`TurnStatus` 枚举含 `completed`、`interrupted`、`failed`、`inProgress`；适配器仍需验证终态通知与状态是否相符，不能按方法名一律庆祝。Turn 对象还含 `items`、`error`、`startedAt`、`completedAt` 等字段，不能整体转发。
- `ThreadReadParams` 有 `includeTurns`；即使不带 turns，`ThreadReadResponse` 的 Thread 仍有 `preview`、`name`、`cwd`、`path` 等字段。metadata-only 不等于无正文或无敏感信息，不能把默认响应当成安全状态通道。

### 官方资料及适用范围

本次打开并阅读以下官方页面（developers.openai.com 原路径重定向至 learn.chatgpt.com）：

1. [Codex App Server](https://learn.chatgpt.com/docs/app-server)：公开 JSON-RPC 协议、初始化、状态通知、终态及 schema 生成方式。文档将 app-server / WebSocket 标为实验性，不能承诺生产支持。`thread/read` 不订阅事件；启动或恢复线程涉及会话生命周期。文档未在本次核查中建立第三方 Windows 程序自动接入现有 Desktop 实例的受支持发现与只读订阅契约。
2. [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)：`codex exec --json` 输出生命周期与 item 事件。适用于调用方启动的 CLI 工作，不自动覆盖 Desktop 已有任务；流也可能包含消息及工具内容。
3. [Advanced Configuration — Notifications](https://learn.chatgpt.com/docs/config-file/config-advanced#notifications)：`notify` 当前说明仅覆盖 `agent-turn-complete`，JSON 参数含输入消息和最后回复；不能补齐六态或直接转发原载荷。TUI 通知不等于外部全量状态 API。

本对话可调用的 `list_threads`、`read_thread`、`wait_threads` 是 Codex 给当前代理的工具权限，不是外部 exe 的公开凭据或监听端点。本任务没有将它们包装成适配器，也未用它们读取其他任务的对话。

## 三条路线与取舍

| 路线 | 价值 | 缺口与建议 |
| --- | --- | --- |
| 订阅现有 Desktop 的正式状态源 | 符合现有任务自动驱动桌宠的体验 | 未证实可访问端点、只读授权和无正文订阅；保持 unknown，不能宣称 M4 达成 |
| 经批准的自有 CLI / app-server 会话 | 可使用文档事件，schema 可按版本校验 | 属于新增运行方式；不等于 Desktop 旁路观察。需解决仅状态投影与 Windows 实测；作为后续受控验证候选 |
| 独立运行 + 显式模拟 | 不依赖尚未确定的联动接口，可开发动画和交互 | 始终标“模拟”，无真实完成承诺；建议作为当前降级 |

`notify` 仅作受限补充候选，因信息范围和正文载荷不列为默认路线。不读取内部数据库、扫描会话 JSONL、注入进程、修改安装包或猜测私有 socket。发现 CLI proxy 子命令不构成使用内部 Desktop socket 的依据。

## 与桌宠程序无关的协议草案

以下字段、枚举和阈值均待统筹接受。适配层负责来源确认及归一化，状态层负责顺序和聚合，渲染层只消费展示状态；不依赖 Electron、Tauri、图集坐标或动画文件名。传输可在技术栈确定后选受当前用户 ACL 限制的本地 IPC；本提案不指定端口或命名管道名称。

### 候选事件封装

| 字段 | 语义 |
| --- | --- |
| `schemaVersion` | 草案示例为 `1`；未知主版本拒收并标记来源不兼容 |
| `sourceId`、`sourceKind` | 来源实例的本地不透明 ID；kind 为 `real` 或 `mock`，由接入配置绑定，不能相信任意发送方自称 real |
| `epoch` | 适配器连接/进程代次；重连换代，不跨代比较序号 |
| `eventId`、`sequence` | 同一 epoch 下稳定唯一 ID、严格递增整数；重发必须保留原值，由适配器生成，不冒称 Codex 原生字段 |
| `taskId`、`turnId` | 来源内稳定的任务 ID 与轮次 ID；组合键含 sourceId。线程级快照的 turnId 可为 null，不用于宣布轮次完成 |
| `kind` | `transition`、`snapshot` 或 `heartbeat`；heartbeat 只证明链路活性 |
| `state` | 前两类必填：`idle / working / waiting / completed / failed / unknown`；heartbeat 不携带业务状态 |
| `occurredAt` | UTC RFC3339 事件时间；来源无时间时为 null，禁止伪装原始时间 |
| `observedAt`、`timeBasis` | 本地收到来源事件的 UTC 时间；basis 为 `source` 或 `adapter-observed`；实际超时另用单调时钟 |
| `reason` | 受限机器枚举，如 `approval`、`user-input`、`turn-completed`、`turn-failed`、`interrupted`、`stale`、`disconnected`、`unavailable`；不带自由文本 |

允许的正常结束示例仅用于规格讨论，**是模拟数据**：

```json
{
  "schemaVersion": 1,
  "sourceId": "demo-source",
  "sourceKind": "mock",
  "epoch": "demo-epoch-1",
  "eventId": "demo-epoch-1:42",
  "sequence": 42,
  "taskId": "demo-task-A",
  "turnId": "demo-turn-2",
  "kind": "transition",
  "state": "completed",
  "occurredAt": null,
  "observedAt": "2026-09-16T19:00:00Z",
  "timeBasis": "adapter-observed",
  "reason": "turn-completed"
}
```

不携带任务标题、提示词、回复、推理、工具参数/输出、diff、工作路径、账号、令牌或错误原文。默认只保留内存中的最新状态与有界去重记录；诊断只记计数、版本和错误类别。来源 ID 也不上传遥测。

### 候选状态映射

| 状态 | 足够证据 | 不足证据 / 边界 |
| --- | --- | --- |
| idle | 有效来源明确报告当前线程 idle，或已确认完整范围内无活动任务 | 未连接、空缓存、静默不是 idle；独立待机动画不代表 Codex idle |
| working | 确认的当前轮次开始；或 fresh active 且无等待标记 | 进程运行不构成任务 working |
| waiting | active 带上述等待标记；受控源明确请求审批或用户输入 | 不能读回复文本猜测；不替用户作答或批准 |
| completed | 当前轮次显式正常终态，具有可关联 turnId | `turn/completed` 方法名、`item/completed`、线程 idle 均不单独够用 |
| failed | 当前轮次显式失败终态 | 工具单次失败、可重试错误不等于轮次失败；线程 systemError 暂映射 unknown + 来源错误 |
| unknown | 启动、断连、过期、未知版本、notLoaded、关联不明 | 取消/中断用 unknown + interrupted，不当作成功；随后有效 idle 可恢复 idle |

真实映射未来必须按来源版本核对。本机 schema 含 waitingOnUserInput，但未通过真实 UI 等待场景验证。CLI 若缺少所需字段或等待事件，对不支持状态报告 unknown，不靠内容推断补全。

### 顺序、去重与过期

1. 接收端先验证来源身份、版本、字段类型和大小上限，来源故障不崩溃渲染器。sourceKind 与接入配置不一致则拒收。
2. 同一 `(sourceId, epoch, eventId)` 重复只处理一次；相同 ID 不同载荷视为来源错误。同代序号小于等于已接收位置的迟到消息不得回滚状态。序号跳跃说明可能漏事件：将受影响来源任务置 unknown，要求权威快照再继续。
3. 本地 sequence 只保留适配器的接收顺序，不证明上游事件本来有序。上游没有顺序保证时，不按壁钟强行排序；终态与新开始矛盾、缺失轮次归属时进入 unknown 并重同步。
4. 以 `(sourceId, taskId, turnId)` 记录轮次终态与已展示标记。旧轮次完成不能覆盖新轮次 working；同轮次终态不可被迟到 working 复活。同线程无 turnId 的 idle 更新只更新基础状态，不能凭它制造或清除某轮次完成事实。
5. 建议链路 heartbeat 5 秒、连续 15 秒未收到即 unknown；明确断开立即 unknown。建议业务状态 30 秒无权威确认即 stale。**heartbeat 不续业务状态有效期**；长任务/长等待只有来源能提供当前权威状态快照时才能续期，否则诚实显示 unknown。这些值只是产品候选，不是官方 SLA。
6. `occurredAt` 用于说明来源时间，`observedAt` 用于诊断；超时用接收端单调时钟。若已知可靠的源时间表明事件早于有效期，即使刚收到也拒绝作为当前状态，先取快照。没有源时间且不能保证实时交付的积压消息也不触发庆祝。源时间不可信、休眠恢复或时钟跳变时先重同步。
7. 重连换 epoch，旧代消息全部丢弃。先清除有效性并标 unknown；新代的首个权威完整快照建立所选范围基线，再接收后续转换。恢复快照可显示当前状态，但不回放历史完成/失败动画；离线事件不冒充刚刚发生。
8. 去重记录建议内存有界，淘汰时保留当前/最近轮次终态水位；应用重启不从缓存推断真状态。无可靠轮次与基线能力的来源不能支持完成动画。

### 多任务和拖动期间的展示

建议默认只关注用户选定任务。多任务模式必须明确集合与完整性；“没有看到其他任务”不是“其他任务已完成”。每项独立维护状态，不将一项 completed 聚合成全部完成。

可供统筹选择的聚合规则：选定集合中 waiting 优先，其次 working；都没有时，只要存在 unknown 就显示 unknown；否则显示短时 failed、短时 completed，再回到已确认 idle。旁边保留计数及离线标记，例如“1 等待、2 工作、1 未知”，避免优先级隐藏并行工作。终态展示窗口候选为 5 秒，不改变底层业务记录；超时回到 fresh 基础状态或 unknown，不能无依据回到 idle。新轮次开始立即覆盖同任务旧终态展示。

拖动是渲染层覆盖动作，不是业务状态。拖动期间继续处理事件、过期与去重；松手重新计算最新有效聚合状态，不能恢复按下鼠标前的旧 working。完成动画只在同轮次、仍在展示窗口、尚未播放且未被新轮次取代时允许播放一次；断连或过期时恢复 unknown。具体动作映射与时长交由程序、动画任务和统筹共同确定。

## 仅状态接入的前置条件

后续若选择真实验证，先用无私密内容的受控任务验证，不接入现有真实会话。必须先证明来源能在数据进入桌宠适配层前完成仅状态投影；不能以“收到完整流后不保存”代替“未读取完整对话”。

App Server 的通知排除能力不等于字段白名单：终态对象、读取响应仍可能含 items 或 preview，新增方法也可能带内容。需要正式仅状态接口，或由获准拥有会话的源端组件输出最小投影，并验证权限和版本变化。当前没有实现或验证这样的桥接；若做不到，则保留 unknown。桌宠不承担会话控制、批准工具调用或代理登录职能。

后续验证退出条件：Windows 可访问的受支持入口、只读与仅状态边界、六态真实证据、断连/重连快照、来源版本兼容性均有记录。新建独立 app-server 看到的状态不能作为 Desktop 既有任务联动证据。

## 交给测试任务的场景（未执行）

| 输入或操作 | 应观察结果 |
| --- | --- |
| working → waiting → working → completed | 对应同一真实轮次，完成只展示一次 |
| 同一终态重送、sequence 回退 | 不重复动画，不回滚 |
| 新轮次 working 后旧轮次完成 | 保持新轮次 working |
| 序号缺口、未知枚举、冲突终态 | unknown，等待权威基线 |
| 断连 / heartbeat 正常但状态已过期 | 均不保留伪工作或伪完成状态 |
| 重连快照包含历史 completed | 不补播历史庆祝 |
| A 完成、B 工作、C 等待、D 掉线 | 可区分并行状态，不宣布全部完成 |
| 拖动时完成、又开始新轮次，再松手 | 恢复新状态，不播放旧完成 |
| 拖动时完成且随后断连 / 过期 | 松手显示 unknown |
| 人为取消、工具报错后继续、任务正常结束 | 不混淆 interrupted、局部错误和正常终态 |
| 系统休眠恢复、壁钟变更、应用重启 | 重同步；旧缓存不能宣布完成 |
| mock 与 real 切换、伪造来源、含正文载荷 | 清空旧基线，标明模拟；拒绝越界载荷，不写原文日志 |

自动化可验证状态归约、时间、异常输入及去重；真实连接、权限、正文隔离与 Windows 拖动恢复必须后续实测。本文没有实现测试或运行桌宠，不声称这些场景通过。

## 待统筹决定与交接

首要决定：是否接受“现有 Desktop 的外部仅状态订阅尚未证实，M2 独立运行、M4 单独设接入门槛”的范围。随后决定是否另开受控 CLI/app-server 验证，或等待 Desktop 正式状态入口。

协议字段、取消映射、过期阈值、终态展示窗口、默认关注单任务/聚合规则均为评审输入。统筹接受后才写入正式共享接口；程序任务当前只能依赖“业务状态与拖动动画分离、未知不可猜成功”的原则，不能把本文 JSON 当成已冻结契约。动画任务不需据此修改图集；测试任务可将上述场景纳入自己的验收矩阵。

本阶段只交付本文件，不改 ADR、运行时代码、依赖或他人文件。提交前检查文档 diff、JSON 示例可解析、六态和 Issue 验收覆盖；PR 中记录实际检查结果。Draft PR 不代表 ADR 被接受，不自动合并或关闭后续真实验证工作。
