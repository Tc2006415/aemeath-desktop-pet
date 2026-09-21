# QA-007：ART-011 中间交接

状态：格式与不依赖新羽饰的控制器定向检查通过；**整体验收未关闭，等待ART-012中等幅度扇翅候选**。PM在本轮进行中转达用户新增幅度要求，因此停止旧hold视觉验收，未推广0.4.0或改正式0.3.0。

## 固定输入与隔离

- 唯一目标为 `C:/Users/bigxi/.codex/worktrees/eaf8/桌宠/assets/characters/aemeath-v1/source/art011-package`，ART提交 `395fce2504bde5e792739a4e9d83a0544300a4dd`，含表情0.4.0。body-only只作为局部合成来源证据读取，未作为验收包或宿主目标。
- 最新生产基线为PM `164856a2d5c362d23ec3c2bc2949382a8f6755cd`，包含DEV d80c302；PM确认后续03fe48f仅文档变化。开工工作树干净。
- QA分支与PM合并遇到旧0.2.0正式资源冲突，立即 `git merge --abort`；没有解决或提交正式资源冲突。PM认可改用 `git archive` 固定快照到 `artifacts/qa007-production-164856a`，ART source证据固定到 `artifacts/qa007-art-395fce2`。候选每个文件与指定eaf8目录逐字节比较一致。
- manifest SHA-256：`b76f67cee1464425c3881f3f401217a2c44e3b5e43bcd245bd4a4bc6915beedb`。未使用旧QA宿主作当前产品结论。

## 已完成证据

| 命令 | 结果 |
| --- | --- |
| `python -B scripts/qa/check_art011.py` | 退出0；独立PNG/CRC读取、mask、来源、预览及保留动作检查通过，详见下文 |
| `& $sdkExe restore artifacts/qa007-production-164856a/src/Aemeath.Host/Aemeath.Host.csproj --locked-mode` | 退出0；仅隔离快照还原 |
| `& $sdkExe publish artifacts/qa007-production-164856a/src/Aemeath.Host/Aemeath.Host.csproj -c Release -r win-x64 --self-contained true --no-restore -p:PublishTrimmed=false -p:PublishSingleFile=false -o artifacts/qa007-host-164856a` | 退出0；当前生产快照发布到独立QA目录，未替换旧产物或正式资源。尚未运行此产物 |
| `./scripts/qa/Test-Art011Controller.ps1` | 退出0；独立临时项目引用上述当前生产Host/Presentation，真实加载候选后4组检查通过，未运行无关完整套件 |
| `git diff --cached --check`、`git diff --cached --name-only` | 提交前无空白错误，仅scripts/qa与本报告 |

`$sdkExe` 为 `$env:LOCALAPPDATA/Aemeath/toolchains/dotnet/10.0.401/dotnet.exe`。检查源文件不执行ART生成/合成脚本；PNG只读解码器为 `scripts/qa/png_readonly.py`，结果为 `artifacts/qa007-pixels.json`。QA临时控制器项目位于 `artifacts/qa007-controller`，源模板 `scripts/qa/Art011ControllerChecks.cs.txt` 不混入旧QA项目编译。

格式结果：12张候选均静态96×104 RGBA8，二值alpha、非全透明、CRC通过且小于256KiB，冠顶y22，轮廓不触画布边；anchor(48,94)。PM正式0.3.0五PNG逐字节不变，原三动作对象不变。三段均4项，360ms once / 720ms loop / 460ms once；hold包含3个不同PNG，非仅重复同图。pickup尾/hold首/release首路径一致，release末为neutral。

七张新表情/身体合成的显式并集mask与脸部、身体mask并集一致，mask外RGBA差分均0；脸部合成对身体来源的整图alpha变化均0，mask内表情像素逐一等于对应来源。惊讶源图至donor的像素中心最近邻、alpha128、偏移(0,+5)经独立读取核对一致。预览HTML内嵌manifest及12PNG与最终候选字节一致。本轮尚未据此宣称预览视觉通过。

| 新帧 | neutral相对RGBA变化 | 并集mask像素 | mask外差分 | 脸部RGBA变化 / alpha变化 |
| --- | --- | --- | --- | --- |
| hold-half | 668 | 820 | 0 | 217 / 0 |
| hold-light-half | 931 | 1194 | 0 | 217 / 0 |
| hold-peak-closed | 948 | 1212 | 0 | 219 / 0 |
| hold-surprise | 660 | 820 | 0 | 209 / 0 |
| pickup-surprise | 664 | 820 | 0 | 209 / 0 |
| release-closed | 424 | 452 | 0 | 219 / 0 |
| release-half | 422 | 452 | 0 | 217 / 0 |

控制器实际加载6动作12图、无停用项。pickup各帧边界至360ms进入hold、hold720ms循环边界通过；15个松手时点为0/40/79/80/159/160/259/260/359/360/400/540/720/900/1080ms，均立即进入release、逐项走完460ms后回idle。release在0/40/80/180/300/459ms重抓均开新pickup实例，旧release期限不覆盖新动作；40ms失捕获等价EndDrag API和重复EndDrag不重启release；旧pickup完成不覆盖release，完成仅一次。这里是API输入，不是原生捕获丢失测试。

## 风险、未验与后续差分范围

40ms快松手发生在pickup首帧neutral的80ms内，因此可跳过惊讶；release固定从hold-half开始。release期间重抓固定进入pickup首帧neutral，没有插值。时序与安全恢复已验证，但是否产生不可接受的视觉突变尚待新候选检查，不把逻辑通过等同视觉接受。

旧hold每720ms眨眼一次（闭眼180ms）；用户新要求中等幅度扇翅已使旧hold小幅方案不再满足最终目标。因此没有继续重复旧hold节奏、浅深1×/3×动态或原生拖动验收，没有启动宿主过程检查，也没有推广该包。原生透明窗口、真实按下/松手/重抓/失捕获均仍未验；浏览器/日志不得替代。羽饰3px和内羽1px回摆为旧版本已披露限制，新翅膀应按实际变化重新核对。

等待ART-012后，只对新增/修改PNG、mask、预览嵌入及循环/三段端点差分复验；控制器/时长未改时复用本轮边界证据。届时再检查新包版本/manifest哈希/实际宿主帧日志与退出，以及可用条件下的原生交互。程序问题交PM派DEV，素材问题交ART；本轮未发现需要修改生产代码的逻辑故障。

完成中间交接即停止，不发布、联动、自启或创建新任务；定时跟进仍暂停。正式0.3.0保持，等待新候选及继续验收指令。
