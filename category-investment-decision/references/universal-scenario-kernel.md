# 全场景通用内核

## 定位

本文件只在主 Skill 轻量路由表和 `selection-scenarios.md` 都无法明确判断时使用，用于兜底未被覆盖的国家、平台、商品、业务阶段或用户表达。完整决策类型、对象类型和输出格式路由表见 `selection-scenarios.md`；本文件只提供通用问题框架和兜底规则。

不要因为场景表没有完全匹配就输出泛泛建议；必须把任务归入“决策类型 × 对象类型 × 输出格式”。

若任务包含进入、投资、上架、放量或放弃建议，默认输出仍使用完整专业报告骨架；通用内核只决定挂载模块和补数清单。用户明确要求快速、卡片、清单、月报，或任务不产生新的投资判断时，可以压缩展示，但仍要保留专业判断闭环。

## 六个通用问题

1. **这次要做什么决策？**
   Enter、Screen、Reverse、Compare、Monitor、Diagnose、Scale、Maintain、Reduce、Stop、Review。

2. **输入对象是什么？**
   Category、Product、ASIN/Link、Store、Keyword、Country、Platform、Portfolio、Experiment、Supplier、Creative、Review/VOC。

3. **哪些证据必须有？**
   需求、竞争、利润、合规、供应链、流量、VOC、国家本地化、平台规则、经营数据。

4. **哪些未知会推翻结论？**
   合规/IP/安全红线、利润压力场景、不可验证需求、供应商报价、物流尺寸、平台准入、样本不足。

5. **应该挂载哪些模块？**
   Full Report 骨架下挂载 Reverse、Matrix、Country、Platform、VOC、Keyword、Experiment、Operating、Exit 或 Checklist 模块。

6. **下一步动作是什么？**
   验证、进入、监控、修复、加码、收缩、停止、复核、补数。

## 兜底规则

- 未知国家：读取 `country-routing-universal.md`，按当前官方来源核验，不凭内置经验断言。
- 未知平台：读取 `platform-routing-universal.md`，先归类平台流量逻辑，再决定证据和利润口径。
- 未知品类：先做风险分类，再决定是否需要合规/IP/安全人工复核。
- 数据不足：输出可执行补数清单；不得为了完整报告编造精确数字。
- 多场景叠加：以最终商业决策为主场景，其他模块作为附录或补充表。
