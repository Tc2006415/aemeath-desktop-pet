# ART-003 首批角色素材制作记录

状态：基准原图已交付，待外观评审及技术转换授权；不属于可加载角色包。2026-09-16。

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
