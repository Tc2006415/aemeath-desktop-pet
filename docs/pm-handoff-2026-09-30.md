# 爱弥斯桌宠：新 PM 会话交接

交接日期：2026-09-30。用户明确要求将旧统筹会话的职责、项目情况和下一步同步到新会话，以减少上下文。新会话接任 PM，沿用现有专题任务，不重开项目、不重复需求访谈、不立即进入新功能。此交接不是新的开发阶段授权。

## 1. 你的职责

你是本项目唯一的活跃统筹 PM。负责维护产品范围、已确认需求、共享契约/ADR、任务依赖、集成分支、版本边界及用户验收。你需要检查实际交付、提交、图片及必要测试证据，不能只转述专题任务的“完成”。你可以在用户既有授权范围内阅读和消息协调下列现有任务。

向任务直接发任务卡，每张写清目标、固定基线、允许文件、禁止范围、交付内容、必要验证及停止条件；不把任务卡同步 GitHub。尊重各任务独立 worktree/分支。共享接口由 PM 决定；跨模块变更先报告影响。集成应选择确切提交或路径，不整分支合并历史内容。尤其 ART 分支正式目录包含旧的、已弃用素材，绝不能整体回流。

用户要求先确定动画需求，再制作完整小阶段预览，审核通过才能下一项。已确认的审美、时序、技术授权不反复询问。用户不喜欢重复测试或无意义的细节审批：只验证实际风险及变动范围，失败或未决才扩大。发现素材/代码问题派回对应任务，不要越过职责偷偷修改其工作区。PM 可在自己的集成目录维护文档、共享规范、集成和打包。

用户对当前项目的协作授权持续有效，但不要额外创建专题任务或子代理。本次新建 PM 会话是用户明确要求的交接例外。旧 PM 不再同时派单，避免双重指挥。

## 2. 项目与现有任务

- 项目：独立 Windows 爱弥斯像素桌宠，参考《鸣潮》游戏里的像素小爱。不是 Codex 内置桌宠改包，不是 ChatGPT Work Pets。不要用 work-pets 技能。
- 仓库：私有 https://github.com/Tc2006415/aemeath-desktop-pet 。本机 C:/Users/bigxi/Documents/ChatGPT/桌宠 。PM 分支 codex/runtime-direction。
- 交接前代码/候选集成 HEAD：5c810d7，工作区干净。此交接文档会产生后续文档提交，代码版本不变。
- 旧 PM 任务：01a0abcd-069c-7f32-bf63-e115dd4b14dd。
- 程序 DEV：01a0abdf-e286-7e01-b893-937bd3ddd507；worktree C:/Users/bigxi/.codex/worktrees/e114/桌宠；codex/desktop-runtime-proposal；既有 draft PR8。
- 动画 ART：01a0abdf-e294-78d3-a6b8-eb0cef96a2a9；worktree C:/Users/bigxi/.codex/worktrees/eaf8/桌宠；codex/animation-spec；既有 draft PR5。
- QA：01a0abdf-e3be-75a3-8721-17120f6fa7c0；worktree C:/Users/bigxi/.codex/worktrees/26d3/桌宠；codex/acceptance-matrix；既有 draft PR6。
- 联动 INT：01a0abdf-e29c-7ee3-94f0-9408e0e48848；worktree fa60；当前无执行任务，不启动联动。
- 所有专题任务已完成本轮交付，停在等待验收。需要进度时优先 wait_threads 紧凑快照/游标，避免重复读取整段历史或重复派单。

## 3. 接任时读取的文件

先读 AGENTS.md、README.md、docs/development-workflow.md、docs/task-briefs.md；历史文档的 GitHub 任务卡/早期范围不能覆盖最新用户指令和直接卡。然后读本文件、docs/project-status.md 顶部、docs/adr/0005-native-v2-behavior.md、docs/reviews/qa011-native-v2-review.md、docs/implementation/native-v2-progress.md。ADR0005 顶部已接受条款优先于附录保留的旧“待决/推荐”措辞；旧包兼容参考 ADR0004。

不要从 project-status 后面的历史“待审核”段落误判当前状态。它按时间倒序保留历史，最新顶部才是当前结论。不需恢复几百条旧心跳。README 仍描述正式0.4，并非新候选功能的完整说明。

## 4. 现在到哪里了

当前完成：用户认可的 v2 动画已做成 schema3 / package0.5.0 候选，程序已接入、独立 QA 通过、PM 已选择性集成并构建。**现在等待用户对真实 Windows 候选进行人工操作和视觉验收。用户还没有报告本轮验收结果。**

正式默认包仍是0.4.0 / schema2，目录 assets/characters/aemeath-v1 的正式文件和 artifacts/host-win-x64 保持。不要宣称0.5已经默认推广或公开发布。

候选素材：assets/characters/aemeath-v1/source/art036-package/ 。64独立PNG路径、64语义键、60种不同SHA，45待机组合+19交互图；共524130字节PNG。manifest 29882字节，SHA256=95cf8f8102f9631d0a02ae40a46fa497f61d9d423ff350191a399104a0a4b182。共78存储时序项，5类释放尾序列/64完整源路由。

候选程序：artifacts/native-v2-win-x64/Aemeath.Host.exe。必须显式传候选 --package；直接双击这个exe会使用旧默认资源，不能由此判断v2无效。为用户准备了 scripts/Start-V2-Preview.cmd，自动模式/2倍尺寸/显式正确候选路径。请让用户先退出旧桌宠，然后双击此启动入口。无需重新打包才能验收。

PM 构建指纹：EXE 9A12AAD9976FBF953EB22163ACA905ED376118E66AC5BC437BB488BB4FB2CB76；Host DLL AFA75E5679F58A8119F88B81D775564E7AFD3C026255FA1CA0D5C6EDCF5B3B21；Presentation DLL 5155D9EA4CC477F39DCCAA548BFF1D1F41BBAFADE8D13C208E6A271677050B06。不要误用 DEV 工作区构建的不同指纹。

## 5. 已冻结的体验要求

- 全部外观以用户选择的第二版模型为基准，紧凑头身、保护头饰。不能恢复用户否决的 ART030 长腿/大变形或旧0.2翼形。
- 待机翅膀整体轻扇，1400ms周期；衣摆配合翅膀，回落滞后100ms；不单独随机触发衣摆。
- 普通眨眼240ms：半闭60/闭80/半闭60/开40。每次完成后均匀随机等待4000–7000ms，含端点。用户已明确确认。
- wink加同侧微歪头1200ms：中间250/wink450/中间350/回正150；随机等待50000–69999ms（约一分钟），动作结束后重新计时，拖拽中不触发。
- wink与blink互斥；同刻到期wink优先，已经开始blink让其结束（最多240ms）再wink，wink期间不积压blink；抓起始终立即打断。用户已确认，不重问。
- 抓起先700ms慌张：实际显示源60，左140/右140/左140/右140，无怒筋过渡80；随后持续微恼怒，嘟嘴+画面右上头饰外暗粉怒筋，1400ms翼循环，直到放下。不自动缓和。
- 放下540ms：实际显示源60、高翼100、中翼100、正常半眨眼120、正常A160。用户选择保留下放时较大上扬。260ms恢复正常表情并移除怒筋，540ms新建待机时钟和两个眼等待。
- 任意放下阶段重新抓起立即取消旧收尾，首60ms保留真正最后提交图，因此可能暂时保留怒筋。用最后Image.Source提交的源，不在输入事件重新采样猜测。这个提交不是显示器呈现回执。
- 无有效源用当前包neutral并记录；坏schema3包整包拒绝、保留旧有效包。保留schema1/2兼容、手动诊断。

## 6. 已有证据与仍未验证的内容

DEV解析 c608fa1、调度/Host c9bac870d5a19c0b43dc6ff140f997e8d351ea62，交接843da413c6952a581c94cb7d36ab59357541eed1；PM cherry-pick为5d6d7ac/c38263a/95fbaa1。ART036固定11a30f1ce32f973f02fedc85a29b20326b3ea151，依据素材2c31b27与ART035交接651c7d0，PM只选择性提取候选与清单，没有整分支合并。

QA固定c9eeca7ef537b7e256df9c36d25a4fb8a8a091d9，PM接收982d275。独立8组检查通过，涵盖翼/衣摆边界、眼动作冲突、迟到采样、重计时、源身份/过期/伪造/重复提交、未绘制40ms快松、放下各阶段重抓、坏配置/坏PNG保留旧包。无阻止候选集成的代码缺陷。

PM集成后亲自跑受影响48项测试：48通过/0失败/0跳过；TRX为tests/Aemeath.Presentation.Tests/TestResults/bigxi_SENJO_2026-09-29_17_39_07_net10.0.trx。发布成功。运行 scripts/smoke-native-v2-host.ps1 显式候选，automatic PID31724、manual-wink PID20156、manual-release PID56172三次均exit0；日志在artifacts/smoke-v2-{automatic,manual-wink,manual-release}.jsonl。核对渲染路径/状态与退出，通过。这些已验证，不因换会话重跑。

真实鼠标捕获、窗口外松手即停、失焦/Escape、快松与重抓、浅深桌面视觉尚待人工。现有工具当时禁用原生控制，不能用DOM、模拟时钟或进程日志替代；若当前工具能力变化，先查看支持边界。64路穷举是binder/player，controller检查可达状态，不是64次原生鼠标操作。

保留的美术限制：手部慌张读感偏弱；wink/闭眼回正、衣摆回基础及有限翼帧之间可能有接缝；认可翼图有少量原透明点。用户认可整体观感，并未证明任意入口完全无缝。不在验收前擅自重画或做插值。

## 7. 下一步顺序

1. 新会话先核对交接和当前状态，简短告诉用户已接任、目前等真实v2验收。不要立刻派制作/新功能卡，不重复测试，不要求用户重复已答需求。
2. 用户尚未验收时，提供 scripts/Start-V2-Preview.cmd 链接及简短检查点：普通待机/眨眼/一分钟wink；拿起慌张→持握恼怒→放下恢复；快松、放下中重抓、窗口外松手、失焦/Escape、缩放退出。精确毫秒边界已有自动测试，不要求用户手工数毫秒。
3. 若反馈缺陷，区分代码/素材；收集可以自行查证的证据，向原DEV或ART派受限修复卡。只验证受影响场景，修复后展示给用户。
4. 若用户认可候选，再根据其推进指令决定默认0.5推广：更新正式素材/打包白名单、启动说明，清理打包输出仅限验证过的目标目录，进行必要发布资源和启动检查；不能把当前显式候选当默认包已推广。
5. 后续用户已提出但未完成的功能：待机60–120秒随机等待后，在当前屏幕可用区域短距离轻盈漂浮、配合轻扇翅膀；不越界，抓起立即打断。这轮明确不并行做，需当前验收后再冻结具体动作/边界并按逐项审核流程推进。不是步行。其他任务联动、持久化、自启、公开发布均非本轮范围。

## 8. 工具、流程与历史授权

图片生成/编辑用imagegen；用户已允许最近邻缩放、二值alpha阈值、整数对齐和局部程序合成，不能用代码画占位角色冒充成品。任务卡需规定生成/合成上限，达到失败上限带证据停下，不无限循环。

本机.NET C:/Users/bigxi/AppData/Local/Aemeath/toolchains/dotnet/10.0.401/dotnet.exe；Python C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe。PowerShell，路径含中文，使用LiteralPath和明确绝对路径。当前构建不必重新运行；未来命令可查交接文档。

素材预览曾在 http://127.0.0.1:8923/art034-demo.html，服务根为ART worktree的assets/characters/aemeath-v1/source；旧PID20448不要假设仍运行。浏览器仅供美术演示，不能替代Windows验收。尽量复用已有标签。

heartbeat automation id=automation，当前PAUSED，用户未新授权重开。旧心跳提示可能仍提ART010，已过时，不得据此回退。不要迁移/重启自动化。本轮交接只换PM上下文。

AGENTS要求新实质性工作先使用grilling，但已答不重复、明确直接执行时遵从。已认可动画和本轮原生集成需求全已确认；接任不是新需求访谈。用户偏好简洁进展、完成后集中演示；无变化不反复发状态。
