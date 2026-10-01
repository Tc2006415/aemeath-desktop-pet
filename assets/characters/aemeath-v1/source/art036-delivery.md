# ART036 schema3 / 0.5.0 候选交付

依据 PM 冻结提交 `15b2c32` 的 ADR0005 顶部条款。候选目录：`assets/characters/aemeath-v1/source/art036-package/`，仅 manifest.json 与 frames/64PNG。没有替换正式0.4、修改宿主或共享契约，没有公开发布或推进漂浮。

## 来源与制包

- 素材固定 `2c31b27c99550f9002662cfb6f55181bd9fc0deb`；清单固定 `651c7d0dd32fec9d3c31a4f5ec6aea20291410e8` 的 art035-handoff.json。
- `art036-package.py` 直接读取固定Git blob并逐字节写入，不使用图像库。0生成、0改像素、0重编码；64逻辑键各保留独立path，包括相同字节与transition别名。
- 完整来源映射为ART035 assets逐项对应：源=`assets[].path`；目的=`frames/` + key将冒号替换连字符并转小写 + `.png`。manifest behavior.images逐键登记目的path和原SHA；脚本逐项比较固定源blob、候选字节、清单SHA，禁止SHA去重。
- 原有顶层元数据和actions origin从PM固定manifest取得；只设schemaVersion=3、packageVersion=0.5.0并重建六动作与behavior。neutral单帧1000ms沿用现行规范。

## 冻结配置

profile=layered-idle-drag-v1；45组合完整。翼1400、衣摆1400、blink240、wink1200；blink等待4000..7000闭区间，wink50000..69999闭区间。优先级和原生源提交/取消语义由ADR005及DEV实现，此包不新增描述字段或脚本。

pickup源首60ms+五项尾，共700ms；hold1400ms持续循环；release源首60ms+5类共用四项尾，每条540ms。64全路由由ART035完整序列逐项反推，normal、left-panic、right-panic、annoyed、transition各保留身份。620–700ms使用无怒筋transition C，放下260ms换normal-half-B移除符号。重抓首60ms仍保留实际源。

手动六动作：neutral循环单帧；idle-soft循环open/base A400 B150 C150 C400 B150 A150；idle-smile单次A/base mid250 wink450 mid350 open150；drag-pickup单次neutral60+panic尾；drag-hold循环恼怒翼；drag-release单次neutral60+normal尾。不含旧entrySequences或旧15秒自动笑脸配置。

## 实测与验证命令

仓库根使用 `C:/Users/bigxi/AppData/Local/Programs/Python/Python312/python.exe`：

1. `python assets/characters/aemeath-v1/source/art036-package.py`：制作后定向校验，退出0。
2. `python assets/characters/aemeath-v1/source/art036-package.py --check`：只读重复核对最终交付包，退出0。
3. `git diff --cached --check`：提交前检查。

| 项目 | 实测 |
| --- | --- |
| PNG独立文件/不同SHA | 64 / 60 |
| PNG总压缩字节 | 524130 |
| manifest UTF-8字节 | 29882（低于65536） |
| manifest SHA256 | 95cf8f8102f9631d0a02ae40a46fa497f61d9d423ff350191a399104a0a4b182 |
| JSON容器深度 | 7（上限8） |
| 待机组合 / 释放路由 / 尾序列 | 45 / 64 / 5 |
| behavior / 手动 / 总时序项 | 51 / 27 / 78（总上限256） |

校验包括重复JSON属性拒绝、固定配置相等、路径规范与独立性、固定源原字节/SHA、45组合、64路首源+540ms与原清单逐项一致、引用完备、所有轨道边界与手动帧、项数/单图/总图/manifest/深度上限。制包与check不读取历史全量保护文件、不重跑浏览器或旧视觉。此为制包脚本核对，不是DEV真实decoder/loader或宿主运行证明。

## 限制与交接

手部读感、wink/闭眼入口回正、衣摆回基础及有限帧接缝、原翼透明点均保留。用户已认可观感，不代表任意入口无缝或原生验收。DEV需显式加载固定候选，提供真实加载与受影响测试；QA/PM另行验收。请仅选择性提取art036-package目录及交付/制包脚本，不整分支合并历史正式资源。交PM和DEV后停止，自动跟进继续暂停。
