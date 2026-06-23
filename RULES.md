# Repository Rules

Maintenance conventions for this repository. This file is not loaded automatically when a Skill runs. Put every runtime-critical rule in the relevant `SKILL.md`.

## 1. Source of Truth

Treat this repository as the single source of truth for Skill changes. Edit here first. The local Codex installation should point to these directories with symlinks.

## 2. Skill Structure

```text
skill-name/
|-- SKILL.md          # Required Skill definition
|-- agents/           # Optional Codex UI metadata
|   `-- openai.yaml
|-- scripts/          # Optional deterministic helpers
|-- references/       # Optional supporting documentation
`-- assets/           # Optional reusable output assets
```

Keep runtime instructions inside the Skill. Do not add per-Skill README, changelog, installation guide, or other auxiliary documentation.

## 3. Source File Safety

- Treat user-provided files as read-only. Do not overwrite, rename, move, delete, or modify their metadata.
- Transform or analyze copies only when needed.
- Never store user data, downloaded pages, reports, or task output inside a Skill directory.

## 4. Temporary Workspaces

Create intermediate files only when the task needs them. Use one of these two modes and document the selected mode in the relevant `SKILL.md`.

### Managed mode

Use for complex, resumable, or multi-step tasks.

- Store work under `${TMPDIR:-/tmp}/<skill-name>/<YYYYMMDD-HHMMSS>-<task-slug>/`.
- Add `.task-owner.json` with the Skill name, task ID, and creation time.
- On resume, clean only directories whose marker matches the known task ID.
- Delete the task directory at completion and verify that it no longer exists.

### Ephemeral mode

Use for short, single-run tasks such as video download and frame extraction.

- Create a unique directory with `mktemp` under `${TMPDIR:-/tmp}`.
- Retain the exact path in a task-local variable and delete only that path.
- Delete the directory at completion and verify that it no longer exists.
- Do not use broad cleanup commands or guess ownership during recovery.

In both modes, report the exact remaining path and reason if cleanup fails.

## 5. Final Deliverables

- Save final deliverables to `$HOME/Downloads` unless the user specifies another directory.
- Use `<Country>_<Platform>_<CategoryOrObject>_<Scenario>_<YYYY-MM-DD>.<ext>` when the active Skill defines no more specific naming rule.
- Replace unsafe filename characters with hyphens and keep the extension intact.
- Before writing, ask the user how to handle an existing file: overwrite, version, or rename. Never choose automatically.
- Return a clickable absolute path for every delivered local file.

## 6. Local Codex Installation

Use symlinks so repository edits take effect immediately:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"

ln -sfn "$PWD/category-investment-decision" \
  "${CODEX_HOME:-$HOME/.codex}/skills/category-investment-decision"

ln -sfn "$PWD/video-link-breakdown" \
  "${CODEX_HOME:-$HOME/.codex}/skills/video-link-breakdown"
```

Do not use `cp -r` as an update mechanism; existing destinations can retain stale files or produce nested directories.

## 7. Validation

After modifying a Skill:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" category-investment-decision
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" video-link-breakdown
python3 category-investment-decision/scripts/test_models.py
git diff --check
git status --short
```

Also verify that:

- every local link from `SKILL.md` resolves;
- `agents/openai.yaml` still represents the Skill accurately;
- README file inventories match the repository;
- no caches, downloads, screenshots, or test artifacts remain.

## 8. Git Workflow

Review the exact changed files before staging. Do not use broad staging when unrelated user changes are present.

```bash
git add <changed-files>
git commit -m "Describe the Skill change"
git push origin main
```

## 9. Adding a Skill

1. Use `skill-creator` to initialize and validate the Skill.
2. Keep the Skill self-contained and add only required resources.
3. Add `agents/openai.yaml` with accurate UI metadata.
4. Add the Skill to both language sections of `README.md`.
5. Add its symlink command and any Skill-specific validation command to this file.

---

# 仓库规则

本文件用于维护本仓库，不会在 Skill 执行时自动加载。所有运行时必须遵守的规则都应写入对应的 `SKILL.md`。

## 1. 唯一真实来源

将本仓库作为 Skill 变更的唯一真实来源。先在这里修改；本地 Codex 安装目录通过软链接指向本仓库。

## 2. Skill 目录结构

```text
skill-name/
|-- SKILL.md          # 必需：Skill 定义
|-- agents/           # 可选：Codex 界面元数据
|   `-- openai.yaml
|-- scripts/          # 可选：确定性辅助脚本
|-- references/       # 可选：支持文档
`-- assets/           # 可选：可复用交付资产
```

运行规则写入 Skill 本身。不要在单个 Skill 内添加 README、更新日志、安装指南等辅助文档。

## 3. 源文件安全

- 将用户提供的文件视为只读，不覆盖、重命名、移动、删除或修改元数据。
- 只有任务需要时才使用副本进行转换或分析。
- 不把用户数据、下载页面、业务报告或任务交付物存入 Skill 目录。

## 4. 临时工作目录

只有任务需要中间文件时才创建临时目录。每个 Skill 在 `SKILL.md` 中明确使用以下哪一种模式。

### 受管模式

适用于复杂、可恢复或多步骤任务。

- 路径使用 `${TMPDIR:-/tmp}/<skill-name>/<YYYYMMDD-HHMMSS>-<task-slug>/`。
- 创建 `.task-owner.json`，记录 Skill 名称、任务 ID 和创建时间。
- 恢复任务时，只清理标记与已知任务 ID 完全匹配的目录。
- 完成后删除任务目录，并验证目录不再存在。

### 短生命周期模式

适用于视频下载、抽帧等单次短任务。

- 使用 `mktemp` 在 `${TMPDIR:-/tmp}` 下创建唯一目录。
- 在当前任务变量中保存精确路径，只删除该路径。
- 完成后删除目录，并验证目录不再存在。
- 禁止宽泛清理；恢复时无法确认归属的目录不得删除。

两种模式下，若清理失败，都必须报告准确的残留路径和原因。

## 5. 最终交付物

- 用户未指定目录时，保存到 `$HOME/Downloads`。
- 当前 Skill 没有更具体规则时，使用 `<国家>_<平台>_<品类或对象>_<场景>_<YYYY-MM-DD>.<扩展名>`。
- 将不安全字符替换为连字符，并保持扩展名完整。
- 写入前检查同名文件；必须让用户选择覆盖、版本号或改名，不得擅自决定。
- 最终回复提供可点击的绝对路径。

## 6. 本地 Codex 安装

统一使用软链接，让仓库修改即时生效：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"

ln -sfn "$PWD/category-investment-decision" \
  "${CODEX_HOME:-$HOME/.codex}/skills/category-investment-decision"

ln -sfn "$PWD/video-link-breakdown" \
  "${CODEX_HOME:-$HOME/.codex}/skills/video-link-breakdown"
```

不要使用 `cp -r` 更新 Skill；目标已存在时可能保留旧文件或产生嵌套目录。

## 7. 校验

每次修改 Skill 后运行：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" category-investment-decision
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" video-link-breakdown
python3 category-investment-decision/scripts/test_models.py
git diff --check
git status --short
```

同时检查：

- `SKILL.md` 中的本地链接全部存在；
- `agents/openai.yaml` 与 Skill 实际能力一致；
- README 文件清单与仓库一致；
- 没有残留缓存、下载文件、截图或测试产物。

## 8. Git 工作流

暂存前检查具体变更文件。存在无关用户改动时，不使用宽泛暂存命令。

```bash
git add <变更文件>
git commit -m "说明 Skill 变更"
git push origin main
```

## 9. 新增 Skill

1. 使用 `skill-creator` 初始化并校验 Skill。
2. 保持 Skill 自包含，只添加必要资源。
3. 添加与能力一致的 `agents/openai.yaml`。
4. 在 `README.md` 中英文部分都登记该 Skill。
5. 在本文件加入软链接命令及该 Skill 特有的校验命令。
