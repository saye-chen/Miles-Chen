# 连续追问下的报告谱系、增量证据与重基线协议

## 最高优先级不变量

用户在首份报告后补充卖家类型、资源、成本、供应商、国家、平台、数据、限制或经营玩法时，禁止把新信息简单追加到末尾。每轮必须先判断新信息对现有结论的影响，再决定继承、修订、重算、重基线或新建决策对象。

连续对话只能提高证据密度、模型贴合度、行动精度和可审计性；不得因为追问次数增加而降低研究模块、隐藏冲突、缩短推理、混合口径或让多个互相矛盾的结论同时有效。

每个规范决策对象在任何时点只允许一个 `Current Effective Decision`。多对象组合可以同时引用各子对象的唯一 Current，并拥有一个独立的组合 Current；不得把某个子对象结论冒充全局唯一结论。历史版本完整保留用于审计，但不得继续作为执行依据，除非当前版本明确继承对应动作。

## 报告状态模型

每份正式报告或决策卡记录：

- `decision_object_id`：产品×国家×平台×生命周期×核心经营目标的规范对象。
- `report_id` 与 `report_version`：例如 `CIDM-R-001 / v1.0`。
- `parent_report_id`：直接父版本；首版为空。
- `runtime_version`、证据截止日、币税和成本口径。
- `information_state`：卖家画像、资源、数据与关键假设的完整快照哈希。
- `effective_status`：`current / superseded / historical / blocked`。
- `change_class`、影响模块、重算 ID、批准人与生效时间。

同一决策对象形成有向无环谱系。禁止覆盖原文件、删除旧结论或让版本产生循环依赖。

正式维护使用 `references/report-lineage-schema.json`、`scripts/validate_report_lineage.py` 和 `scripts/build_current_decision_state.py`。不得只凭自然语言声称谱系安全。

## 每轮新增信息的五级分类

| 级别 | 触发条件 | 必须动作 | 旧版状态 |
|---|---|---|---|
| Addendum | 只增加解释、来源或不改变判断的细节 | 追加证据/说明，检查冲突 | 仍 current，可附加补遗 |
| Revision | 改变证据强度、置信度或表述边界，但不改变计算和档位 | 更新 Ledger、置信度、限制和措辞 | 新小版本 current，父版 superseded |
| Recalculation | 改变成本、价格、费率、销量、退款、预算、评分输入或门槛状态 | 运行确定性脚本，生成新输入/输出哈希与差异表 | 新版本 current，旧计算 historical |
| Rebase | 改变卖家类型、关键资源、经营玩法、生命周期、战略目标或执行拓扑 | 从产品基础结论开始重建卖家可行域、路线、资源和行动计划 | 新主版本 current，旧执行计划 superseded |
| New Decision Object | 产品、目标国家、目标平台、核心商品身份或主要决策问题改变到不可直接比较 | 新建对象和谱系，可引用旧证据但不得继承结论 | 原对象继续独立存在 |

分类按最高影响级别执行。一次补充同时触发多个级别时不得拆低处理。例如“我们是精品大卖，拿到独家成本并准备德国站”至少触发 Rebase；若德国站改变对象边界，则为 New Decision Object 或父子对象组合。

## 新信息摄取合同

每条新增信息先生成 `Information Delta Card`：

| 字段 | 内容 |
|---|---|
| delta_id | 本轮新增信息编号 |
| received_at | 接收时间与业务截点 |
| statement | 用户原始陈述的忠实摘要 |
| evidence_state | confirmed / partial / user-asserted / conflicting / rejected |
| affected_object | 影响哪个规范对象 |
| replaces | 替换哪些假设、输入或证据 ID |
| affected_modules | 门槛、评分、利润、供应、玩法、拓扑、行动等 |
| likely_change_class | Addendum 至 New Object |
| decision_materiality | 是否可能改变进不进、投多少、怎么切、何时停 |
| verification | 需要的文件、后台、报价、合同、样品或实验 |

用户陈述是有效输入，但不自动等于已验证事实。卖家说“我供应链强”只能形成资源主张；提供合同、产能、良率、阶梯报价和目标对象批次后才能逐项升级。

## 影响传播与最小重算集

新增信息不能只改它出现的章节。按依赖关系传播：

```text
卖家/资源变化
→ 约束解除合同与 Seller-specific Feasibility
→ 供应、成本、组织容量、玩法和拓扑
→ 利润/现金/库存/风险
→ 生命周期动作上限与资本释放
→ 0→1 主计划、成功/停止/回滚
```

```text
成本或费率变化
→ 三场景利润与保本线
→ 利润评分与置信度
→ 广告/采购/库存上限
→ 决策档位和行动计划
```

每轮输出 `Impact Set`：必须重算、必须复核、可以继承、明确不受影响四类。没有完成必须重算项时，新结论保持 `proposed` 或 `inconclusive`，不得宣称报告已经更新完成。

字段影响使用 `references/decision-impact-graph.json` 和 `scripts/analyze_report_delta.py` 计算传递闭包。输入字段未映射时状态为 `BLOCKED`，先补影响图，不能靠临时直觉跳过二阶和三阶影响。

## 继承、替换与撤销矩阵

新版本逐项处理父版本：

| 项目 | 允许状态 | 要求 |
|---|---|---|
| 证据 | inherited / added / superseded / rejected | 保留原 ID、来源和原因 |
| 假设 | unchanged / narrowed / replaced / falsified | 写明新假设与推翻条件 |
| 计算输入 | inherited / changed | changed 必须触发新计算哈希 |
| 门槛/评分 | inherited / recalculated / blocked | 说明影响链和版本 |
| 结论 | confirmed / strengthened / weakened / changed | 不允许无理由跳档 |
| 动作 | continue / modify / pause / revoke / completed | 被替换动作必须明确撤销 |
| 成功/停止/回滚 | inherited / changed | 动作改变时必须同步复核 |

禁止使用“其他内容同前”绕过关键模块。只有被列入 `Impact Set: unaffected` 且口径仍一致的内容才可继承，并回指父版本位置。

动作执行状态细分为 `planned / approved / committed / in_progress / irreversible / paused / revoked / completed / recovery_required`。已 committed、in_progress 或 irreversible 的动作不能用“撤销”当作现实恢复；必须列出可回收成本、沉没成本、恢复计划、负责人和截止日。

## 当前有效结论页

每次 Revision、Recalculation 或 Rebase 后，报告开头必须先给唯一的当前有效页：

1. 当前对象、报告版本、父版本、运行时和证据截止日。
2. 当前唯一有效结论、置信度和最大动作强度。
3. 本轮新增信息及验证状态。
4. 相比父版本发生了什么变化，为什么。
5. 被继承、替换、撤销和新增的结论/动作。
6. 已重算的评分、利润、门槛和输入/输出哈希。
7. 当前行动计划、责任人、预算/库存上限和观察窗。
8. 当前成功、停止、回滚和仍缺失的数据。
9. 历史版本状态与禁止继续执行的旧动作。

如果用户只问局部问题，也先用一段短状态声明指出：本轮是解释、局部修订还是会触发完整 Rebase。不能在没有处理父版本的情况下直接给新的重仓建议。

## 深度累积规则

报告版本只能“展示压缩”，不能“研究降级”。新版本至少保留父版本所有仍决定结论的专业模块，并增加：

- 新证据与反对证据；
- 新资源的容量、成本和失效条件；
- 新旧口径的可比性；
- 冲突解决或未解决状态；
- 更精确的行动、责任、节奏和回收机制。

若新信息推翻旧结论，必须解释旧结论在当时信息集下为何合理，以及哪个新证据触发改变。禁止把旧结论描述成模型错误来掩盖信息状态变化，也禁止事后改写旧报告让其看起来一直正确。

机器校验比较父子版本的决定性模块、证据、反对证据、假设、计算和动作合同数量。任一深度指标下降必须提供可审计理由（例如重复证据合并并保留谱系）；没有理由则阻断发布。篇幅变长不等于深度增加。

## 多轮合并与定期整编

连续出现三个以上 Addendum/Revision，或用户要求“给我当前完整方案”时，必须生成 Consolidated Report：

- 合并所有 current 证据和假设；
- 删除展示层重复，但保留谱系引用；
- 重新运行适用计算和合同校验；
- 输出单一当前结论与完整计划；
- 把此前零散补遗标记为 historical/superseded。

不得让用户自行从多轮消息中拼接当前执行方案。

## 冲突、撤回与错误更正

- 新信息与旧证据冲突：标记 `conflicting`，降低置信度，优先补证；不能自动采用最新说法。
- 用户更正先前信息：保留原陈述和撤回原因，新输入触发 Recalculation/Rebase。
- 发现计算或事实错误：发布 Correction，不把它伪装成普通版本演进；列出受影响决策和已执行动作的恢复方案。
- 新资源后来失效：回退到失效资源之前的可行域，但使用当前市场和成本重新计算，不能简单恢复旧版本数字。

## 对话中断与恢复

恢复任务时先重建 `Current Decision State`：当前对象、有效版本、未完成 Gate、待补证、活跃动作和停止条件。无法确认当前有效版本时，只能提供状态审计，不得继续释放预算、库存或跨平台动作。

## 必要输出与校验

正式连续追问场景必须输出 Information Delta Card、change class、Impact Set、继承/替换/撤销矩阵、当前有效结论页和谱系记录。涉及 Recalculation/Rebase/New Object 时运行全部适用确定性脚本、`scripts/validate_decision_contract.py` 与 `scripts/validate_report_lineage.py`，并用 `scripts/build_current_decision_state.py` 生成恢复快照。

报告交付前检查：只有一个 current 版本；所有旧动作有状态；所有 changed 输入有新计算；所有被推翻结论有原因；所有 inherited 内容口径兼容；所有缺失项说明决策影响。
