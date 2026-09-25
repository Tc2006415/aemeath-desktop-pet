# ADR 0004：按已提交姿态衔接收翼

状态：PM接受实施，2026-09-21。仅拖动阶段；正式0.3.0保持至集成验收。

## 依据与边界

用户选择保留放下时大幅上扬。ART018固定5a61f0e与QA008的5d08ef0通过素材/网页视觉门槛，PM重跑独立文件检查通过；不是原生验收。采用DEV006提案300442e的源帧入口方向。B4/B7形色差、不均步幅及高位各侧1px收窄为已披露限制。不得从任意低位松手硬切高位。

## 素材与时序冻结

候选packageVersion为0.4.0，schemaVersion为2；在ART019 source候选中制作，不覆盖正式包。保留ART013全部13张PNG及原neutral/idle-soft/idle-smile/pickup/base release动作，追加三张逐字节来源：

| 包内路径 | 固定来源 |
| --- | --- |
| frames/hold-bridge-low.png | ART015 art015-b2-v1-96.png |
| frames/hold-bridge-mid.png | ART014 art014-v1-96.png |
| frames/hold-bridge-high.png | ART017 art017-v1-96.png，禁止旧B7 |

下文L/M/H分别代表上述三图。hold一个720ms翼周期为hold-half80,L50,M50,H50,hold-up-half100,H50,M50,L50,hold-half100,hold-down-half140。重复两周期，第二周期倒数第二项替换hold-mid-closed100；共20项1440ms，仅一次闭眼。不得改像素或新增绘制。

R表示原release：[hold-half80,release-closed100,release-half120,neutral160]，460ms。所有路径均带frames/与.png。entrySequences键为源PNG路径，值为完整帧数组；下表中的拼接仅用于制包，运行时读取完整数组。

| 源图 | 完整序列 | 总时长ms |
| --- | --- | --- |
| hold-up-half | 源40,H40,M40,L40,R | 620 |
| H / M / L | 当前40,尚余下一级各40,R | 580 / 540 / 500 |
| hold-half | R | 460 |
| hold-down-half | 源40,R | 500 |
| hold-mid-closed | 源80,release-closed100,release-half120,neutral160 | 460 |
| hold-surprise / pickup-surprise | 源40,R | 500 |
| neutral | neutral160 | 160 |
| release-closed | 源100,release-half120,neutral160 | 380 |
| release-half | 源120,neutral160 | 280 |
| soft-light / soft-peak / smile-half / smile-closed | 源40,neutral160 | 200 |

覆盖全部16张图。基础41项，入口63项，共104项；实际制包时须重新计算确认。中位直接R460区别于网页探针额外保持40ms的500ms，避免重复首图等待；其余按表。低位松手不额外先展至最高位。

## 格式与运行规则

新加载器支持schema1/2；仅schema2的actions.drag-release允许可选entrySequences，其余字段白名单继续严格。每条首path等于键，末path等于neutral有效图；键必须属于本包已验证PNG。重复键、越界/非法路径、类型/时长/首尾错误整包拒绝。任一入口坏PNG停用整个release，坏neutral仍整包拒绝。沿用64项/序列、60000ms/序列、256总时序项、128不同图片/8MiB等原上限，不放宽。

一次release只创建一个PlaybackId，以完整所选数组作为有效序列；采样提供实际frame path，宿主不能用基础动作索引绘制变体。使用原单调时钟与半开区间，只完成一次、旧实例不得覆盖新请求。

宿主记录最后交给Image.Source的帧及包代次，不在松手时重新Sample猜测之前显示了什么。渲染提交集中在Rendering路径；快照包含有效包代次、path、来源PlaybackId与帧索引/提交序号。仅接受当前宿主保存的受校验记录，来源PlaybackId可早于最新请求（按下未绘制就松手）。这不是显示器呈现回执。

松手/失捕获/失焦/Escape立即清拖动标记、释放捕获停止位置更新，幂等选路一次，不能等动画收尾。按当前源图选择入口；缺入口/无效快照回基础release并记录回退；无release回idle。schema1仍原行为，手动播放用基础frames。换包/模式/退出取消旧序列及快照，不残留旧包状态。

重抓立即取消release、开新pickup，保留现有neutral首项；这是明确的响应优先策略，不宣称重抓视觉连续。集成后必须实际观察；若出现阻断性跳变，由PM另行收敛，不能自行扩展通用动作图。普通松手过渡不解决所有身体/表情入口变化，需定向验证。

## 实施与验收

ART019只制作source候选/预览/来源证据。DEV007仅Host/Presentation、对应测试及工程说明实现此契约，使用诊断夹具先验证，最终读取ART019真实候选。禁止改正式素材或引入联动、持久化、自启、漂浮/待机新功能。

必要测试：schema1兼容/schema2校验降级；16源图首帧命中、各自期限前1ms/边界完成；跨时序边界但未绘制仍用旧提交帧；40ms及按下未绘制松手；任意release中重抓与旧完成隔离；捕获结束幂等、换包快照失效、自动/手动切换。QA独立检查候选与真实生产加载器/控制器，不重复无关DPI全套。

真实自有宿主版本/manifest/帧路径日志及退出是必要运行证据，但不能替代原生视觉。最后验证实际鼠标拖动、松手即停位移、失捕获和重抓；工具不具备时明确留用户验收。PM集成构建后通知用户，并等待人工验收，不自动进入下一阶段。
