# 命令参考

## 原则

命令入口用于降低场景误判；自然语言入口与命令等价。命令不能跳过证据、风险偏好、国家、平台、置信度和红线判断。

若命令参数缺失但不影响方向，使用显式假设继续；若缺失会推翻结论，先问用户。

## 命令表

| 命令 | 场景 | 输出 |
|---|---|---|
| `/enter {产品} {国家} {平台}` | 品类进入评估 | 完整 STEP1-STEP8 投决报告 |
| `/screen {产品} {国家}` | 快速初筛 | 五道门槛、七维评分、风险和验证动作 |
| `/reverse {ASIN/链接} {国家}` | 链接反查 | 页面、流量、评论、利润、供应链、风险卡 |
| `/compare {候选1} {候选2} ...` | 多候选组合 | 横向排名、预算组合、候补和淘汰原因 |
| `/monitor {ASIN/品牌}` | 竞品监控 | 当前快照、监控点、告警、下次检查 |
| `/diagnose {ASIN}` | 老品诊断 | 流量、转化、竞品、评论、广告、季节排查 |
| `/review-test {实验ID}` | 测款复盘 | Go/Iterate/Stop/Inconclusive 和评分回写 |
| `/reverse-funnel {输入JSON}` | 反向漏斗/达人端口测算 | 盈亏平衡订单、最低点击、最低曝光和固定成本承受线 |
| `/portfolio-breakeven {输入JSON}` | 测品组合盈亏平衡 | 最低成功率、预期利润、预算可测数量和敏感性 |
| `/voc {ASIN/评论文件}` | VOC 深挖 | 痛点编码、市场空白、切入楔子 |
| `/keywords {ASIN/品类} {站点}` | 关键词策略 | 八维分类、机会词、否定词和应用动作 |
| `/country {产品} {国家/区域} {平台}` | 国家本地化 | 国家进入矩阵、本地化准备度和进入顺序 |
| `/platform {产品} {国家} {平台}` | 平台适配 | 平台类型、流量逻辑、费用履约和测款指标 |
| `/post-launch {ASIN/SKU}` | 上市后巡检 | Scale/Maintain/Review/Reduce/Stop 决策 |
| `/exit-review {ASIN/SKU}` | 退出复盘 | 假设对照、损失核算、可复用学习 |
| `/report-demo {场景}` | 报告压测 | 本地 Markdown 样例报告和对话摘要 |

## 路由规则

- `/enter` 和“完整报告/市场进入/投委会”同义。
- `/screen` 和“快速判断/初筛/粗看”同义。
- `/monitor` 默认使用完整报告骨架；未触发重新评分时可压缩 STEP1-STEP8 展示，但必须保留专业判断闭环。
- `/diagnose` 默认读取上市后经营闭环和竞品监控，不把老品诊断写成新品进入报告。
- `/review-test` 使用事先门槛；没有事先门槛时先披露数据局限，不倒推成功标准。
- `/reverse-funnel` 用于 TikTok Shop 达人寄样、视频投流、小批量或其他需要从利润反推曝光/点击/订单的场景；没有 CTR/CVR 证据时必须写成假设区间。
- `/portfolio-breakeven` 用于月度测品池、候选组合预算和成功率门槛；结果只判断测品系统是否经济可持续，不替代七维评分。
- `/keywords` 必须把关键词结论回连到评分、Listing、广告或内容动作。
- `/country` 遇到区域请求必须拆成具体国家，不把区域当成统一税务或合规市场。
- `/platform` 遇到未知平台必须先归类平台类型，不硬套 Amazon/TikTok/Temu 逻辑。
- `/report-demo` 默认落本地 Markdown 文件，并使用专业报告模板与 Evidence/Assumption Ledger。

## 确定性计算命令

单件利润和批次盈亏平衡：

```bash
python3 scripts/profit_model.py --price 39.99 --product 7 --fulfillment 6 --commission-rate 0.06 --promo-rate 0.1 --payment 0.8 --batch-fixed-costs 330
```

反向漏斗：

```bash
python3 scripts/reverse_funnel.py standard input.json
python3 scripts/reverse_funnel.py creator input.json
```

测品组合最低成功率：

```bash
python3 scripts/portfolio_break_even.py input.json
```

这些脚本只计算用户提供或报告明确假设的输入，不自动补行业阈值。输出必须回写到利润、验证动作、停止条件或组合决策中。
