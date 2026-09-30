# ADR 0005：v2 原生组合待机与拖拽

状态：PM接受实施。用户已确认随机4–7秒眨眼和推荐优先级，并授权原生接入。以下冻结条款优先于后附原始提案中的“待决/推荐”措辞；原提案保留作设计依据。

## 冻结决定与实施顺序

- schemaVersion=3，profile=layered-idle-drag-v1；候选packageVersion=0.5.0，目录 assets/characters/aemeath-v1/source/art036-package/。不替换正式0.4.0。
- 接受下附字段、校验限额、源快照、中断和兼容设计。blink每次完成后均匀整数闭区间4000..7000ms；wink50000..69999ms。拖拽/释放优先；空闲同时到期wink优先；已开始blink完成再wink，wink期间不积压blink。
- releaseStart+540重启idle epoch及两个眼动作等待。无有效源用本包neutral并记录回退。无效schema3包整包拒绝并保留已加载有效包。
- 素材固定2c31b27c99550f9002662cfb6f55181bd9fc0deb，交接651c7d0dd32fec9d3c31a4f5ec6aea20291410e8。64语义键/独立路径逐字节复制，不重新生成、改像素或去除别名。
- 手动六动作：neutral=A-open-base一帧；idle-soft取open/base的A400 B150 C150 C400 B150 A150；idle-smile仅作手动wink诊断，A翼/base衣摆的mid250 wink450 mid350 open150；drag-pickup以neutral首60ms加规定panic尾；drag-hold为规定annoyed循环；drag-release为neutral首60ms加normal尾。完整键来自ART035。手动帧loop等外层字段沿用现行规范，neutral/idle-soft/drag-hold循环，其他单次。自动不调用旧15秒笑脸。
- ART先制作候选manifest/64PNG和来源映射，DEV并行实现解析/调度；双方只按本契约协作，出现歧义上报PM，不自行创造字段。
- DEV交付受影响测试和真实候选加载证据后，QA检查固定提交与候选，再由PM集成真实宿主供用户验收。日志不替代原生视觉；默认包推广另由PM决定。
- 本轮不做随机漂浮、任务联动、持久化、自启、公开发布；不重画已认可动作。现有接缝与透明点继续披露。

## 原始方案依据

状态：供 PM 冻结的提案，2026-09-29；不是已接受接口或实施授权。对应对话任务卡「DEV-原生v2集成方案」。本轮仅此文档，不修改代码、正式素材、manifest、锁文件、旧 ADR 或 PM 状态。

## 先列待决项

PM 已答复可在本提案中保留生产参数待决，不阻塞文档交付，也不再访谈已认可动作。下列建议必须经 PM 整体审核后才成为实现要求。

| 决定 | 推荐 | 当前依据/边界 |
| --- | --- | --- |
| 正式眨眼频率 | 每次眨眼完成后重新抽取 4000–7000ms 等待；均匀整数，含端点 | 尚未冻结。网页首次 4000ms、后续按采样时间重排只是演示，不等于此推荐获批；240ms 动作本身已认可 |
| 到期碰撞 | 拖拽/释放优先；空闲同刻到期 wink 优先 blink；已开始 blink 可完成，wink 最多等剩余240ms；wink 中不积压 blink | PM允许作为推荐写入；与网页直接打断 blink 存在区别 |
| 契约 | schema3 内嵌有限 behavior 配置，schema1/2 原语义保留 | 待 PM 冻结新 ADR；不原地扩大 schema2 白名单或限额 |
| 无有效提交快照 | 使用本包 neutral 作为捕获源并记录原因；按同一新动作时长执行 | 不是猜测旧包/旧屏幕；窗口操作仍立即响应 |
| 无效 v3 包 | 整包加载失败、保留当前有效包；启动失败沿用原错误入口 | 保证组合表/选路原子有效。schema1/2 原有按动作停用规则不变 |
| 新包版本/默认推广 | PM 决定新 packageVersion；先显式目录验证，通过后另行决定替换默认 | 当前正式仍0.4.0；不能把 v2 造型名称当 packageVersion |

不重问的已决内容：认可 ART026 轻扇、ART027 眨眼、ART028 wink歪头、ART029 衣摆和 ART034 嘟嘴/怒筋；wink 随机约50–70秒、拖拽屏蔽、结束重计时；panic700ms → 持续恼怒1400ms循环 → release540ms；当前源首60ms；release260ms舒展移除符号；不做随机漂浮、联动、持久化、自启或公开发布。

## 已核实基线与素材证据

PM `codex/runtime-direction` 读取时为 `5389736a319f75a3763ced74c7ece707cc3bc09a`，正式 manifest schema2/package0.4.0，SHA256 `EAB91ECB10037DA7320D4E9C9321C8DCE0F122D3B9D5DAA6E101A55E1E319DA3`。不能只凭 manifest 相同推断 PNG 与旧 ART019 全同：PM 已推广 ART021 两张待机修补图。DEV 与该 PM 基线的 Host/Presentation 源码 diff 为空，可直接评估现有模块。

已读 README、development-workflow、task-briefs、ADR002/003/004，以及 PM status 最新条目。Issue #1 是历史程序任务入口；本机 `gh` 及旧文档中的安装路径均不可用，未宣称重新读取远端 Issue 内容。本轮范围依据最新对话任务卡。旧 README/status 历史段落不能覆盖当前PM卡。

ART034 固定美术提交 `2c31b27c99550f9002662cfb6f55181bd9fc0deb`；ART035交接提交 `651c7d0dd32fec9d3c31a4f5ec6aea20291410e8`，清单为 `assets/characters/aemeath-v1/source/art035-handoff.json` 及同名md。参考 source 下 `art034-demo.html`、`art034-track.js`、`art034-timing.json`、`art034-delivery.md`，及 `art028-engine.js`、`art029-track.js`/`art029-timing.json`。ART035属于清单而非生产manifest；本轮未复制或合并任何ART文件。

实际文件集合为 ART029 45张待机组合（3翼×5眼/头×3衣摆）+ ART034 19张姿态/别名，共64逻辑键、60种SHA字节、524130压缩字节。此为读取与SHA统计，不是新增视觉检查。所有图仍是整张96×104预合成PNG，宿主无需实时拼眼、翼或衣摆，也不重新编码PNG。

参考指纹：

| 文件（source下） | SHA256 |
| --- | --- |
| art034-track.js | 6AF8E3B19C9FF12677BFA24638F760B48B589462AAC6E3835607756B753730B8 |
| art034-timing.json | 8B4D3C0F26EB844CBACDF03E3C8BB65FBA2F7968E57E40A325C4F5916F0E23CF |
| art029-track.js | 0387776F72C4BF8F42680112E5161F704A0EA8789C397CF9D1896D7B77409913 |
| art028-engine.js | 18294E7B82C4FF509345934F2290E07F9EC20591C098582A8A9565D2C08E9CA9 |

## 方案比较与推荐

1. **推荐 schema3 单manifest、有限组合调度。** 图片注册表、待机轨道和交互模板一次原子校验；新增固定profile，不做脚本解释器。新加载器仍读schema1/2，旧加载器拒绝schema3，避免静默误播。
2. schema2 外挂 behavior.json：表面改动小，但旧宿主会忽略侧文件继续15秒笑脸/旧拖动，产生相同包的两套语义，还需解决两个配置的版本/SHA绑定。因此不推荐。
3. 全展开为 schema2 clips/entrySequences：64来源×5项释放已320项，超过256总项，尚未包含其他动作；pickup也需源首帧，而schema2只允许release入口。随机表情与持续翼/衣摆组合更不能靠六个固定clip表达。不提高旧限额来迁就展开。

源包、生产包与宿主隔离：ART035中的source相对路径只用于选择性逐字节复制。生产manifest使用现有安全语法 `frames/[a-z0-9][a-z0-9_-]{0,63}.png`；例如 `idle:A-open-base` 映射 `frames/idle-a-open-base.png`，`pose:transition-annoyed-C` 映射 `frames/pose-transition-annoyed-c.png`。不硬编码worktree绝对路径，不整体合并ART分支，不把demo/生成脚本带进运行包。推荐保留64个独立路径，暂不按SHA去重；相同字节仍保留各自语义键。

## 共享接口提案：schema3字段与规则

以下是拟冻结字段，非当前加载器已支持内容。继续保留现有manifest元数据、frameSize/anchor/sourceScale/fallbackAction和六动作名集合；schema3额外必填 `behavior`。旧schema1/2不得出现此字段。`actions` 保留基础帧供手动诊断，自动schema3由behavior驱动，不再调用旧15秒idle-smile调度。

| behavior字段 | 结构/含义 |
| --- | --- |
| profile | 固定字符串 `layered-idle-drag-v1`；仅有限状态调度，无JS、表达式、网络、递归或任意事件图 |
| images | 对象：逻辑key → `{path,sha256}`；SHA为小写64位hex；所有引用必须存在，拒绝重复key/未知字段 |
| neutralKey | `idle:A-open-base`，其path必须等于actions.neutral唯一帧path |
| idle.combinations | 数组 `{wing,eyeHead,hem,key}`，3×5×3=45个组合完整且唯一；枚举按ART035，禁止运行时靠文件名拆分推导语义 |
| idle.wing / idle.hem | 各为 `{value,durationMs}` 数组；共用idleEpoch，周期都为1400ms，不独立随机计时 |
| idle.blink / idle.wink | 各为 `{waitMinMs,waitMaxMs,track}`，track项 `{value,durationMs}`；均匀整数闭区间等待，blink数值待冻，wink建议50000..69999精确复现源实现的50–70秒范围 |
| interaction.pickup | `{sourceDurationMs,tail}`；首项绑定捕获key，60ms，tail为固定 `{key,durationMs}` 数组 |
| interaction.hold | 固定 `{key,durationMs}` 循环数组 |
| interaction.release | `{sourceDurationMs,routes,tails}`；首60ms捕获key；routes是每个images key → tailId的全映射；tails是tailId → 固定 `{key,durationMs}` 数组 |

配置只存数据：pickup没有任意占位表达式；sourceDurationMs仅允许在pickup/release各一个首项。release有5类共用尾序列（normal、left-panic、right-panic、annoyed、transition），每类4项480ms，运行时只绑定一个来源首项形成5项540ms序列。routes由ART035完整数组反推并逐键核对，不在宿主split字符串。无多级alias/模板继承，加载时验证所有64路均可一次解析。

key限定1..64个ASCII字母、数字、冒号、连字符/下划线，区分大小写；tailId仅小写字母、数字、连字符，1..32字符。images不同key使用不同path，actions每个path都须出现在images且只有一个key；这样手动base输出也能带准确FrameKey。相同PNG字节可占不同path，不合并语义身份。waitMinMs/waitMaxMs为整数1000..120000且min≤max；仅用于眼动作等待，不受单帧10000ms上限误限。blink总长240、wink1200、pickup700、hold1400、release540和各段边界按本profile逐项校验，不能接受合计相同但分段不同的配置。

有效上限推荐维持：manifest64KiB、JSON深度8、每PNG256KiB、不同文件128张、总压缩8MiB、单项1..10000ms、每时序数组64项/60000ms、存储的时序项合计256（包含actions、两idle轨道、两表情轨道、pickup首项及tail、hold、release首项和每种tail）。注册表≤128键、组合表≤128行、routes≤128条、tails≤16组；这些映射不算时序项但分别限额，禁止循环引用。每个绑定后序列另验≤64项/60000ms，且不预展开64份。候选behavior时序项51：wing6+hem5+blink4+wink4+pickup6+hold5+release首1+尾20；手动actions须计入同一256上限。制包后实际测量manifest大小，超限先减少冗余，不能静默放宽。

路径安全、拒绝重解析点/逃逸、完整解码、固定画布/锚点、二值alpha/非全透明继续复用。schema3图SHA/引用/轨道时长/组合覆盖/路由覆盖有一项错误则整包拒绝，禁止自动截断或替换成近似姿态。重名属性、路径大小写歧义也拒绝。只在新包所有校验完成后切换images和controller/epoch。

## 精确行为与预览差异

待机翼 `[A400,B150,C150,C400,B150,A150]`；衣摆 `[base400,light150,upper650,light150,base50]`。衣摆在1200/1350ms回落，对应翼1100/1250ms，晚100ms。两者共用时间原点，眨眼/wink只换eyeHead，不重启翼和衣摆。

眨眼 `[half60,closed80,half60,open40]` 共240ms。wink `[mid250,wink450,mid350,open150]` 共1200ms。两者互斥；拖拽打断不等待眨眼收尾。wink和blink等待只在idle调度，不在panic/hold/release积压。同刻优先与已经开始blink的等待策略见待决表。

pickup依次：`captured60,left-panic-B140,right-panic-C140,left-panic-A140,right-panic-B140,transition-annoyed-C80`；700ms到hold，hold `[annoyed-A400,B150,C550,B150,A150]` 无限循环。不能在1–2秒后自行缓和。慌张末80ms必须取无怒筋的transition别名，不能换成ART034带符号annoyed-C。

release固定 `[captured60,H100,C100,normal-half-B120,idle:A-open-base160]`，H/C由route选择。所有idle来源、normal-half与normal-normal来源选normal尾；左右panic分别选左右尾；annoyed选带符号尾；transition选无符号旧字节尾。首60ms精确保留逻辑key/path；260ms进入normal-half-B，380ms进入neutral，540ms回自动待机。重抓立即新pickup，首60ms可保留原怒筋，不能为了“无怒筋慌张”偷偷换首图。

计时推荐：使用现有单调毫秒时钟、半开区间；跨越700ms时hold原点为press+700，不能把采样迟到量丢掉。释放完成的idleEpoch=releaseStart+540；wink完成从winkStart+1200重新抽取wink和blink两种等待，翼/衣摆不中断。普通blink完成仅从blinkStart+240重抽blink等待，绝不推迟原wink deadline；若wink正等待blink结束，当刻直接启动wink。等待基点不是松手事件时间。mode切回自动/换新包以当时now开新idleEpoch并抽取两等待；每次release回idle重开翼/衣摆相位和两个眼动作等待。所有旧随机deadline取消。

迟到/恢复采样：持续翼/衣摆按模周期直接取当前相位，结束的交互只完成一次；到期但尚未开始的眼动作最多启动一个，起点用本次now，不补播历史次数。已开始眼动作越过结束时先结束并重排，随后至多启动一个当前到期动作；优先规则固定，可注入clock/random测试。网页的4秒眨眼以sampleTime重排，推荐生产以完成期限重排，两者差异必须在ADR中明确。

页面press/release直接draw、按钮/键盘模拟拖拽、步进与暂停只是预览工具。原生输入事件不得Sample或画图；保持Rendering唯一赋值路径。网页复制的是img最后赋值key，原生等价为最后一次Image.Source提交，不宣称显示器已呈现。不能从浏览器演示推断原生捕获和窗口位置行为已通过。

## 模块复用、源帧与中断

- `PackageFiles`/PNG解码及旧 `PackageLoader` 分支复用；新 `BehaviorDefinition`/`BehaviorParser` 解析v3，旧分支不接受新字段。
- `Playback` 保留schema1/2和手动base行为。可抽取共用半开区间查帧函数并支持绑定后的只读序列，但不复制64份长入口；旧边界测试继续适用。
- `CharacterController` 成为很薄的包profile选择入口，旧策略保留；新 `LayeredBehaviorController` 管理idle眼动作及panic/hold/release。不把这些时钟塞进任务状态模块或多个DispatcherTimer。
- `PetWindow` 继续负责鼠标捕获、即时位置更新、Rendering与包epoch，geometry/DPI计算不改。新增快照/日志字段，不把业务选图搬进宿主。

共用采样建议增加 `FrameKey`（旧包可为空）、`BehaviorPhase` 与可区分组合变化的采样序号；`FramePath`仍是实际有效文件。快照保持packageEpoch/path/PlaybackId/FrameIndex/submissionSequence，v3额外存FrameKey。提交只接受当前controller最近一次发出的对象；key与path必须与已加载映射一致，不能接受外部构造记录。绝不按SHA反查唯一key：64键只有60种字节，alias不能丢。

每次press与release均读取已保存的有效提交源，不在事件中推进动画。允许其PlaybackId早于最新请求；否则“按下尚未Rendering就松手”会丢失真实旧图。press取消旧release，开一个新pickup实例；release选路一次并开一个新实例，不为首60ms/尾部另开实例；重复EndDrag无效。旧完成号不能切走新拖拽；停止/换包/模式切换使旧采样、快照、随机期限失效。

顺序继续是DragSession.End清active → ReleaseMouseCapture → controller.EndDrag。LostMouseCapture同步重入时因active已清直接返回。鼠标抬起、窗口外松手、失捕获、失焦、Escape均立即停止位置移动，再进入同一release语义；渲染掉帧也不能延迟位置停止。重抓先成功获得捕获/开始位置会话，再立即取消旧释放并记录新pickup时间；动画不阻塞窗口跟手。

模式/换包/退出与自然松手区分：先清捕获，随后取消旧profile全部活动，不为已废弃包等待release结束。无源或跨epoch源用本包neutral并打出明确fallback；无效v3候选加载失败保留旧包，不能拿旧图拼新序列。

Host现有帧日志去重键仅PlaybackId/Action/FrameIndex；新组合可能在同一大阶段改变key，必须将FrameKey或有效path及轨道索引加入去重键。日志写profile、配置SHA、epoch、状态/实例、源key/path、提交序号、route与fallback、自然完成，不读取聊天内容。

## 建议下一张实施卡允许范围

DEV：`src/Aemeath.Presentation/{PackageLoader,Playback,CharacterController}.cs` 及新behavior解析/调度文件；`src/Aemeath.Host/PetWindow.cs`；仅必要时调整DiagnosticWindow/App的profile状态展示与包传递；对应 `tests/Aemeath.Presentation.Tests` 新契约/调度/候选测试；自己的implementation说明及一份显式包路径smoke脚本。不加依赖，不改锁文件，不重构geometry/native窗口层。

ART：由PM另卡授权选择性制schema3候选包/manifest，逐字节复制ART035清单PNG，保留64键映射；不让DEV修改正式PNG。PM拥有新ADR、默认包推广、打包白名单/项目资源项变更与合并决定；需要DEV改打包时另在实施卡中点名允许文件。QA拥有独立review/检查脚本。三者以PM冻结的一份契约协作。

建议顺序：PM冻结待决与新ADR → ART制显式目录候选、DEV实现解析和可控调度 → 读取固定候选核对全映射 → 固定提交定点QA → 真实宿主/人工输入与视觉 → PM决定默认推广。此文档交付后停在冻结前，不自动进入其中任何实施阶段。

## 必要验证与人工门槛

1. 加载器：schema1/2原行为与上限；schema3重复/未知字段、路径逃逸、坏SHA/坏PNG、组合缺项/重复、缺route/尾部引用、neutral不一致、项数/字节/时长边界；换坏包保留旧包。只跑受影响包测试，不重跑未变DPI全套。
2. 调度：翼/衣摆全部联合边界前1ms与边界；眨眼/wink期间相位持续；random两端、同时到期、blink中wink到期、拖拽抑制、完成重抽、迟到不补播、模式/包替换取消。明确断言推荐生产频率，不以网页4000ms当已冻值。
3. 交互：700ms/1400ms/540ms各边界；ART035全部64源的首60ms与H/C路线、260ms/380ms/540ms；transition无符号，annoyed保留到260ms，任意释放帧重抓首图及旧完成隔离；40ms快松、按下未提交即松、跨边界未Rendering源仍旧；伪造/过期epoch提交拒绝；EndDrag重入只选路一次。
4. 实际候选：真实decoder/loader读固定包；每key路径/PNG SHA与ART035逐项相等；全部自动/手动输出均落在登记图片；实际计数/manifest≤64KiB/总图字节等边界。手动base不受随机调度抢占，旧schema包仍按旧15秒策略。
5. 原生进程：显式候选目录启动，记录exe/DLL/config指纹、版本、真实Rendering key/path和正常退出；证据只证明加载、提交、生命周期。新代码和候选变化后才跑这轮必要smoke，文档阶段不重编或重复旧39测试。
6. 人工Windows：1×/2×浅深桌面观察全部动作与已有接缝；慢快拖与窗口外松手立即停位移；失捕获/失焦/Escape、40ms快松、wink/眨眼中按下、620–700ms松手、带符号放下、放下各段重抓；验证无旧状态覆盖、符号阶段、退出可达。工具不可用逐项pending，不能用DOM、定时进程或模拟clock冒充通过。

已披露手部读感、闭眼/wink首60ms后回正、衣摆回基础层的入口接缝、原翼透明点继续保留；集成不包含修图。发现阻断性原生跳变须交PM裁决，不擅自增加插值、任意动作图或补画帧。

## 本轮只读验证记录

实际执行：`git status --short`（开始干净）；`git worktree list`/`git log codex/runtime-direction -1`（确认PM基线）；`git diff codex/runtime-direction -- src/Aemeath.Presentation src/Aemeath.Host`（空）；读取上述规范/轨道/交付；PowerShell `Get-FileHash -Algorithm SHA256` 与 `Measure-Object -Property Length -Sum`（64图、60种字节、524130字节及参考指纹如上）。未执行旧测试、生成脚本、应用或浏览器验收。

ART035固定交付后，用 `ConvertFrom-Json` 读取assets并逐文件比较Length/SHA：64/64匹配；枚举 `interaction.releaseByCapturedKey`，确认64路各5项、首key=来源且60ms、每个目标已登记、总长540ms；去除首项后的JSON签名恰好5组，支持共用尾序列方案。命令退出0。`git -C <ART worktree> diff 651c7d0 -- assets/characters/aemeath-v1/source/art035-handoff.json assets/characters/aemeath-v1/source/art035-handoff.md` 为空。清单工作区SHA256 `144AE1213A9C9794F25CE3458CC3A21FC6D6CE23512E685517A32EF4C6398B0F`；文本跨checkout可能发生CRLF转换，源码引用另有清单gitBlobSha256，PNG始终逐字节核对。

交接给PM：审核待决表和schema3字段/限额/取消规则，接受后由PM冻结ADR并派实施；本提案本身不使新格式生效。已认可美术无需重复主观审核，本轮没有新的原生验收结论。
