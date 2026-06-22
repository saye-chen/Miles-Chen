# Miles-Chen Codex Skills

Personal Codex skills for cross-border ecommerce category research, video content teardown, and repeatable AI workflows.

## Skills

### Category Investment Decision

Structured, evidence-driven category-entry decision reports for cross-border ecommerce. Covers investment decisions, ASIN/product-link reverse analysis, multi-candidate portfolio selection, country localization, trend/opportunity screening, and validation planning.

**Path:** `category-investment-decision/`

**Scopes supported (17+ scenarios):** category entry, link reverse analysis, multi-candidate portfolio, country localization (US/EU/UK/JP/SEA), trend/seasonal/opportunity screening, platform-specific analysis (Amazon, TikTok Shop, Temu, Shopify/DTC, Walmart, Etsy, eBay, Shopee/Lazada), product monitoring, store gap filling, SKU extension, profit calculation, and validation testing.

**Core model (CIDM-2026.06):** 7 dimensions × weighted scoring (100 pts), 5 pre-checks with redline priority, 4 decision tiers. Outputs include full reports, rapid screening cards, link reverse-analysis cards, portfolio comparison tables, country entry matrices, and phased validation plans.

**Files:**

| Path | Purpose |
|---|---|
| `SKILL.md` | Full decision framework, scenario routing, scoring model, execution checklist |
| `agents/openai.yaml` | OpenAI GPTs interface definition |
| `scripts/workspace_manager.py` | Create and clean marked temporary workspaces |
| `scripts/profit_model.py` | Deterministic per-unit profit and break-even ad rate calculator |
| `scripts/portfolio_selector.py` | Constrained portfolio selection under budget/SKU limits |
| `scripts/test_models.py` | Regression tests for profit model and portfolio selector |
| `references/scoring-model.md` | 7-dimension scoring anchors, confidence levels |
| `references/selection-scenarios.md` | 17 scenario routes with evidence priorities |
| `references/report-template.md` | Full report and rapid screening templates |
| `references/link-reverse-analysis.md` | 6-step ASIN/product link reverse analysis |
| `references/portfolio-decision.md` | Multi-candidate ranking and combinatorial selection |
| `references/country-localization.md` | US/EU/UK/JP/SEA localization checks |
| `references/validation-playbooks.md` | Phased testing plans and review framework |
| `references/evidence-and-finance.md` | Evidence grading, unit economics, sensitivity scenarios |
| `references/platform-playbooks.md` | Platform-specific analysis (Amazon, TikTok, Temu, etc.) |
| `references/scene-output-protocols.md` | Per-scene deliverable structure |
| `references/usage-guide.md` | Minimum input requirements, call examples |
| `references/source-routing.md` | Data source selection by question type |
| `references/error-and-fallback.md` | Degradation levels, partial completion, recovery |
| `references/input-schemas.md` | Bulk data input specifications |

### Video Link Breakdown

Analyzes short-form video links into structured content teardowns covering script structure, editing techniques, content quality, audience fit, replicable templates, and upgrade suggestions.

**Path:** `video-link-breakdown/`

**Supported platforms:** TikTok, YouTube Shorts, Instagram Reels, X/Twitter videos, Bilibili, Douyin.

**Analysis output:** basic video facts, strategic diagnosis, script structure (hook/setup/beats/payoff/CTA), editing techniques (pacing/jump-cuts/captions/transitions/sound/camera), content quality scores (hook/pacing/clarity/persuasion/originality/replication value), replicable beat-by-beat template, concrete upgrade suggestions, and rewritten script when useful.

**Files:**

| Path | Purpose |
|---|---|
| `SKILL.md` | Analysis framework, workflow, link handling, output templates |
| `agents/openai.yaml` | OpenAI GPTs interface definition |
| `scripts/prepare_video_link.py` | Video download via yt-dlp, metadata extraction, frame extraction, contact sheet generation |

## Repository Workflow

Use this repository as the source of truth for all skill changes.

**Sync to local Codex:** install or update these folders into `${CODEX_HOME:-$HOME/.codex}/skills` before relying on bundled script paths inside a skill. For example, `video-link-breakdown` resolves its script via `$SKILL_DIR/scripts/`, so the repository copy and installed copy must stay in sync after edits.

## Workspace Hygiene

After each skill modification, new skill creation, report generation, script run, or analysis task, clean up temporary files created during the work. Keep only intentional source changes and final deliverables.

Temporary files include scratch folders, caches, downloaded source media, extracted raw pages, one-off screenshots, intermediate exports, test artifacts, and disposable calculation files. If a task needs persistent evidence or reusable assets, store them deliberately in the relevant skill folder and document why they are kept.

Before finishing, check the workspace for unintended generated files. If cleanup cannot be completed, report the remaining files and the reason.

Conversation context and model reasoning state cannot be physically deleted from the workspace, but no local files should be kept merely to preserve intermediate thinking.

## Git Workflow

```bash
git add -A
git commit -m "description of changes"
git push origin main
```

## Adding a New Skill

1. Create `new-skill-name/SKILL.md` with YAML front matter (name, description).
2. Add `new-skill-name/agents/openai.yaml` if the skill has a GPTs-facing UI.
3. Add `new-skill-name/scripts/` for any helper scripts.
4. Add `new-skill-name/references/` for supporting documentation.
5. Update this README with a new entry in the Skills section.

---

# Miles-Chen Codex 技能库

跨境电商品类研究与视频内容拆解的 Codex 技能库，供 AI 工作流重复使用。

## 技能

### 品类投资决策

面向跨境的、证据驱动的品类进入决策报告。覆盖投资决策、商品链接/ASIN 反查、多候选组合决策、国家本地化、趋势/机会筛选和测款验证。

**路径：** `category-investment-decision/`

**支持场景（17+）：** 品类进入、链接反查、多候选组合、国家本地化（美国/欧盟/英国/日本/东南亚）、趋势/季节/机会筛选、平台专项分析（Amazon、TikTok Shop、Temu、Shopify/DTC、Walmart、Etsy、eBay、Shopee/Lazada）、竞品监控、店铺补品、老品扩展、利润核算、测款验证。

**核心模型（CIDM-2026.06）：** 七维加权评分（100 分制）、五道前置门槛（红线优先）、四档决策阈值。交付物包括完整报告、快速初筛卡、链接反查卡、组合对比表、国家进入矩阵和分阶段验证计划。

**文件清单：**

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 完整决策框架、场景路由、评分模型、执行自检 |
| `agents/openai.yaml` | OpenAI GPTs 界面定义 |
| `scripts/workspace_manager.py` | 安全创建与清理任务临时目录 |
| `scripts/profit_model.py` | 确定性单件利润与盈亏平衡广告率计算 |
| `scripts/portfolio_selector.py` | 预算/SKU 约束下的组合优化选择 |
| `scripts/test_models.py` | 利润模型与组合选择器的回归测试 |
| `references/scoring-model.md` | 七维评分锚点与置信度定义 |
| `references/selection-scenarios.md` | 17 个场景的路由与取证重点 |
| `references/report-template.md` | 完整报告与快速初筛模板 |
| `references/link-reverse-analysis.md` | ASIN/商品链接六步反查 |
| `references/portfolio-decision.md` | 多候选排名与组合选择 |
| `references/country-localization.md` | 美/欧/英/日/东南亚本地化检查 |
| `references/validation-playbooks.md` | 分阶段测款与复盘框架 |
| `references/evidence-and-finance.md` | 证据分级、单位经济模型、敏感性场景 |
| `references/platform-playbooks.md` | 各平台分析剧本（Amazon、TikTok、Temu 等） |
| `references/scene-output-protocols.md` | 各场景交付物结构 |
| `references/usage-guide.md` | 最小输入要求、调用示例 |
| `references/source-routing.md` | 按问题类型选择数据源 |
| `references/error-and-fallback.md` | 降级等级、部分完成、中断恢复 |
| `references/input-schemas.md` | 批量数据输入规范 |

### 视频链接拆解

将短视频链接拆解为结构化分析报告，覆盖脚本结构、剪辑手法、内容质量、受众匹配、可复刻模板和优化建议。

**路径：** `video-link-breakdown/`

**支持平台：** TikTok、YouTube Shorts、Instagram Reels、X/Twitter 视频、Bilibili、抖音。

**分析输出：** 基础信息、一句话诊断、脚本结构（钩子/铺垫/节奏/收尾/CTA）、剪辑手法（节奏/跳切/字幕/转场/音效/镜头）、内容质量评分（钩子/节奏/清晰度/说服力/原创性/复刻价值）、可复刻模板、具体优化建议、以及改写脚本（如适用）。

**文件清单：**

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 分析框架、工作流、链接处理、输出模板 |
| `agents/openai.yaml` | OpenAI GPTs 界面定义 |
| `scripts/prepare_video_link.py` | 视频下载（yt-dlp）、元数据提取、关键帧提取、联系表生成 |

## 仓库工作流

以本仓库作为所有技能变更的唯一真实来源。

**同步到本地 Codex：** 更新文件后，将文件夹安装或同步到 `${CODEX_HOME:-$HOME/.codex}/skills`，因为技能中的脚本路径依赖此位置。例如 `video-link-breakdown` 通过 `$SKILL_DIR/scripts/` 获取脚本，仓库副本与安装副本必须保持一致。

## 工作空间清洁

每次技能修改、新建技能、报告生成、脚本运行或分析任务后，清理过程中产生的临时文件。只保留有意的源文件变更和最终交付物。

临时文件包括临时目录、缓存、下载的源媒体、提取的原始页面、一次性截图、中间导出、测试产物和一次性计算文件。如果任务需要保留证据或可复用的资产，有意识地存入相关技能目录并说明保留原因。

结束前检查工作空间是否存在非预期的生成文件。若无法完成清理，报告残留文件及原因。

对话上下文和模型推理状态无法从工作空间物理删除，但不得仅因保留中间推理而保留本地文件。

## Git 工作流

```bash
git add -A
git commit -m "变更说明"
git push origin main
```

## 新增技能

1. 创建 `新技能名称/SKILL.md`，包含 YAML 前置元数据（name、description）。
2. 若有 GPTs 界面需求，添加 `新技能名称/agents/openai.yaml`。
3. 若有辅助脚本，添加 `新技能名称/scripts/`。
4. 若有支持文档，添加 `新技能名称/references/`。
5. 在本 README 的 Skills 节中新增条目。
