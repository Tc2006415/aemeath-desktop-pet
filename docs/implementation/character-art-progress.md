# 首批角色素材制作记录

状态：基准原图已交付，待外观评审及技术转换授权；不属于可加载角色包。2026-09-16。

最新候选：ART-004-H 的 v2 头饰修订见本文末节；仍待用户外观确认，v1保留。下列ART-003记录为历史制作证据，不表示已获转换或动画扩展授权。

## 基线、范围和产物

已执行 `git fetch origin` 并在原 `codex/animation-spec` 分支合并 PM 基准 `77fa5c0e056e45d8e5c9872195ce86ea91b9e9fd`，结果为 fast-forward；已读 AGENTS、README、ADR0003 和现行素材契约。本轮仅制作中性基准，不扩展动作、不改加载器或契约。

- 生成原图：[neutral-generated-v1.png](../../assets/characters/aemeath-v1/source/neutral-generated-v1.png)。单角色、睁眼正向、小幅中性微笑；这是待评审的角色基准原图，不是96×104成品帧。
- 完整实际提示词：[neutral-generated-v1.prompt.txt](../../assets/characters/aemeath-v1/source/neutral-generated-v1.prompt.txt)。提示词明确要求96×104、真正透明、8-bit RGBA及二值alpha，但生成结果未满足全部技术约束。
- 没有创建manifest或frames目录，避免误把不合规原图交给加载器。没有用重复帧凑齐动作，六动作均未宣称交付完成。

## 生成来源与视觉检查

使用 `imagegen` 技能及内置 `image_gen.imagegen`，无需API key；没有调用CLI/API回退。生成前使用 `view_image` 查看已选 `assets/concepts/aemeath-game-style-v2.png`；该图作为造型参考，要求以左侧睁眼姿态生成单独中性角色、删除灰背景，保留粉色紧凑发型、蓝色尖顶头饰、深浅服饰和两侧低位羽饰。

工具原始输出：`C:/Users/bigxi/.codex/generated_images/01a0abdf-e294-78d3-a6b8-eb0cef96a2a9/exec-1ac90a62-5b82-44e2-8b6c-12924fcbfc1c.png`。以 `Copy-Item -LiteralPath` 原样复制到项目source目录，保留工具原件；没有缩放、裁剪、去背景、阈值化、调色或程序绘图。模型具体版本不由本次工具参数选择，不编造生成种子。

已通过 `view_image` 实际查看保存后的原图，并在任务中inline展示：单角色正面、睁开的金色眼睛、粉发、蓝冠、紧凑小身体及低位羽饰均可辨认；没有回到第一版高挑长发造型。画面呈块状像素风，但边缘/色块是否适合96×104仍未验证；透明通道检查也不等于最终外观认可。用户尚未确认该新基准外观，不扩展idle或拖动姿态。

## 实际格式检查

首次只读检查命令 `from PIL import Image` 失败：本机Python没有Pillow。本轮未安装依赖；随后通过Python标准库 `struct/zlib` 读取PNG块、核对CRC、解压IDAT并逆PNG行过滤，统计原始alpha通道。该检查仅解码读取，没有写回或改变图片。

| 项目 | 实际结果 | 契约判断 |
| --- | --- | --- |
| 尺寸 | 1205×1305 | 不符合96×104 |
| PNG位深/色彩类型 | 8 / 6（RGBA） | 符合8-bit RGBA |
| PNG静态性/CRC | 未见acTL；所有块CRC通过 | 静态PNG，读取完整 |
| 文件大小 | 778921 bytes | 超过单PNG 256 KiB上限；仅作为source保存 |
| alpha=0像素数 | 987626 | 确实包含透明背景像素，不是只有灰底的RGB图 |
| alpha=255像素数 | 1628 | 存在完全不透明像素 |
| alpha=1…254像素数 | 583271 | 不符合二值alpha；共256种alpha值 |
| 任意非零alpha边界（含端点） | (0,53)–(1188,1304) | 存在接近画布边缘的非零alpha，不可直接把此边界当成角色裁剪框 |
| SHA-256 | `251add4c2c0384f2d0ed58a3f4ca2cfc6c67b7dfd2cf6cb1c65f3dd276dea815` | 用于原图一致性核对 |

图片没有独立锚点元数据；尚未创建manifest，不声称脚部已对齐(48,94)。本轮未运行宿主、加载器或播放测试：已知尺寸/alpha/字节数不合规，不能把“PNG可解析”称为“可用包”。提交前另执行 `git diff --cached --check`、基线后允许路径检查和原件/项目副本SHA-256一致性核对，实际结果随交接回报。

## 所需最小转换与下一步门槛

内置生成没有产出精确小画布或二值alpha。建议在用户认可外观后，由PM明确授权一次确定性导出：将该原图以最近邻方式映射到96×104画布，把alpha按明确阈值二值化（建议128作为起点），只做整数像素位置对齐以满足固定锚点(48,94)和脚部基线；导出8-bit RGBA PNG并检查大小、留白和羽饰/头饰完整性。不可据任意非零alpha包围盒直接自动裁剪，不改变角色造型，不用程序画新姿态。映射及阈值可能丢失细节或留下杂边，需对转换结果再次视觉检查，必要时回imagegen编辑；本轮没有执行任何这些步骤。

这是唯一请求的范围补充：允许针对已生成原图做尺寸、alpha及整数对齐转换，输出仍在 `assets/characters/aemeath-v1/`，不改加载器或契约。若不授权，可继续用内置imagegen尝试技术修正，但不能保证精确尺寸/alpha，也不把重复生成视为已解决问题。

在外观确认及导出方式获准前，停在这张基准图。PM可先展示本文件链接的原图给用户；下一步才是合规neutral导出、视觉检查，以及按后续授权扩展六动作。真实播放与首角色包验收另行进行。

## ART-004-H：v2头饰外观候选

状态：文件归档及视觉检查待PM验收；**外观等待用户确认，尚未满足正式像素帧规范**。2026-09-16。本轮不重新生成、不做缩放或alpha转换、不进入动画扩展。

来源：PM提供集成工作区 `C:/Users/bigxi/Documents/ChatGPT/桌宠/assets/characters/aemeath-v1/source/` 下的两个新文件。随附提示词记录为PM使用内置imagegen编辑v1，并以指定游戏视频正面截图作为参考，响应用户“头饰更贴近游戏原版正面”的要求。本任务没有再次调用imagegen或重新考据视频，没有把PM生成操作称作本任务生成。

- [v2原图：neutral-generated-v2-headpiece.png](../../assets/characters/aemeath-v1/source/neutral-generated-v2-headpiece.png)
- [PM原始提示词及来源记录](../../assets/characters/aemeath-v1/source/neutral-generated-v2-headpiece.prompt.txt)

使用 `view_image` 实际检查该候选：头冠改为较细的蓝白尖拱，冠弧与粉发上沿之间可见留空；画面右侧头部蓝白羽饰明显缩小并贴近鬓侧。下方两侧羽状装饰仍保留，不能把“侧羽饰缩小”误记成下方羽翼被要求缩小。粉发、金色睁眼、小身体和正面中性姿态仍可辨认。冠尖、冠弧外沿及头部周围存在蓝色/青色零散边缘噪点，不能称为干净的最终像素轮廓；其余部位也未做逐像素一致性证明，不能因提示词要求保留就声称与v1完全相同。是否足够贴近游戏正面由用户评审，不在本任务中代为通过。

实际检查与结果：

| 检查 | 结果 |
| --- | --- |
| PM给定PNG SHA-256与源文件核对 | 一致：`6E78FAA19B4ED324B34938E85F18CECFEB48C02C6814E4ABFD1C2D91ED6CE26E` |
| `Copy-Item -LiteralPath` 后两文件逐一 `Get-FileHash -Algorithm SHA256` | 项目副本与PM源文件逐字节一致；未覆盖v1 |
| 提示词副本SHA-256 | `239DAD952B6A84B3BB28BE2AF980D43426A06FCC28D2B142DBD3F5F855D5E0DA` |
| Python标准库读取PNG签名与IHDR | 1205×1306，8-bit，色彩类型6（RGBA）；仅只读检查 |
| 文件大小 | 716536 bytes，超过单正式帧256 KiB限制；只存source |
| 96×104及固定锚点 | 尺寸不符；未生成manifest或做锚点对齐，不能宣称通过 |
| alpha、像素成品和实机播放 | 本轮未统计完整alpha分布或验证二值alpha，未做像素清理、正式帧或运行验收；边缘噪点已视觉确认 |

本轮只新增上述PNG、提示词并补充本记录，提交前检查 `git diff --cached --check` 与暂存路径。没有改代码、接口、manifest或其他图帧。到此停止，等待外观反馈；之前提出的确定性转换建议仍未因本轮复制归档而获得授权。
