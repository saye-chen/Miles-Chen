#!/usr/bin/env python3
"""Validate repository conventions that the generic Skill validator cannot enforce.

Covers RULES.md section 7 checks:
- Frontmatter keys = {name, description}
- Runtime version declaration present
- Broken local links in SKILL.md and reference files
- VLB e-commerce weights sum to 100
- agents/openai.yaml has required fields
- README file inventory matches repo
- No __pycache__ or .pyc artifacts
- Cross-skill version consistency
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^运行时版本：`([A-Z][A-Z0-9-]*-\d{4}\.\d{2})`。$", re.MULTILINE)
LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    text = skill_file.read_text(encoding="utf-8")

    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return [f"{skill_file}: invalid frontmatter"]
    keys = {
        line.split(":", 1)[0].strip()
        for line in match.group(1).splitlines()
        if ":" in line and not line.startswith((" ", "\t"))
    }
    if keys != {"name", "description"}:
        errors.append(f"{skill_file}: frontmatter keys must be exactly name and description")
    if not VERSION_RE.search(text):
        errors.append(f"{skill_file}: missing runtime version declaration")

    # Check links in SKILL.md
    for target in LINK_RE.findall(text):
        if "://" in target or target.startswith("#"):
            continue
        local_target = target.split("#", 1)[0]
        if local_target and not (skill_dir / local_target).exists():
            errors.append(f"{skill_file}: broken local link {target}")

    # Check links in all reference files
    for ref_file in (skill_dir / "references").glob("*.md"):
        ref_text = ref_file.read_text(encoding="utf-8")
        for target in LINK_RE.findall(ref_text):
            if "://" in target or target.startswith("#"):
                continue
            local_target = target.split("#", 1)[0]
            if local_target and not (ref_file.parent / local_target).exists():
                errors.append(f"{ref_file.relative_to(ROOT)}: broken local link {target}")

    return errors


def validate_video_weights() -> list[str]:
    skill_file = ROOT / "video-link-breakdown" / "references" / "scoring-model.md"
    text = skill_file.read_text(encoding="utf-8")
    table_rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in text.splitlines()
        if line.startswith("|")
    ]
    header = next((row for row in table_rows if "电商成交" in row), None)
    if header is None:
        return [f"{skill_file}: could not locate e-commerce weight column"]
    column = header.index("电商成交")
    rows = [row for row in table_rows if len(row) > column and re.fullmatch(r"\d+", row[column])]
    total = sum(int(row[column]) for row in rows)
    return [] if total == 100 else [f"{skill_file}: e-commerce weights total {total}%, expected 100%"]


def validate_agents_yaml() -> list[str]:
    """Check agents/openai.yaml has required fields."""
    errors: list[str] = []
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        yaml_file = skill_dir / "agents" / "openai.yaml"
        if not yaml_file.exists():
            continue
        text = yaml_file.read_text(encoding="utf-8")
        skill_name = skill_dir.name
        required_fields = ["display_name", "short_description", "default_prompt"]
        for field in required_fields:
            if field not in text:
                errors.append(f"{yaml_file.relative_to(ROOT)}: missing required field '{field}'")
        # Check version or runtime field exists
        if "version" not in text and "runtime" not in text:
            errors.append(
                f"{yaml_file.relative_to(ROOT)}: missing 'version' or 'runtime' field"
            )
    return errors


def validate_readme_inventory() -> list[str]:
    """Check README mentions all skill directories and key files."""
    errors: list[str] = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    # Check all skill directories are mentioned
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        if skill_dir.name not in readme:
            errors.append(f"README.md: missing skill directory '{skill_dir.name}'")

    # Check RULES.md and LICENSE are mentioned
    for required_file in ["RULES.md", "LICENSE"]:
        if required_file not in readme:
            errors.append(f"README.md: missing reference to '{required_file}'")

    # Check model versions in README match SKILL.md
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        version_match = re.search(r"`([A-Z][A-Z0-9-]*-\d{4}\.\d{2})`", skill_text)
        if version_match and version_match.group(1) not in readme:
            errors.append(
                f"README.md: model version {version_match.group(1)} from "
                f"{skill_dir.name}/SKILL.md not found"
            )

    return errors


def validate_no_artifacts() -> list[str]:
    """Check no __pycache__, .pyc, or other artifacts remain."""
    errors: list[str] = []
    for pycache in ROOT.rglob("__pycache__"):
        if ".git" not in pycache.parts:
            errors.append(f"artifact: {pycache.relative_to(ROOT)} directory exists")
    for pyc in ROOT.rglob("*.pyc"):
        if ".git" not in pyc.parts:
            errors.append(f"artifact: {pyc.relative_to(ROOT)} exists")
    return errors


def validate_cross_skill_versions() -> list[str]:
    """Check model versions are consistent between SKILL.md and RULES.md."""
    errors: list[str] = []
    rules_text = (ROOT / "RULES.md").read_text(encoding="utf-8")

    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        version_match = re.search(r"`([A-Z][A-Z0-9-]*-\d{4}\.\d{2})`", skill_text)
        if version_match:
            version = version_match.group(1)
            # Version should appear in at least one of README or RULES
            readme = (ROOT / "README.md").read_text(encoding="utf-8")
            if version not in readme and version not in rules_text:
                errors.append(
                    f"{skill_dir.name}: version {version} not found in README.md or RULES.md"
                )
    return errors


def validate_reference_routing() -> list[str]:
    """Check every reference file is routed to from SKILL.md.

    Scans SKILL.md for mentions of each reference file name.
    A reference file is considered 'routed' if its filename appears
    anywhere in SKILL.md (in a link, table, or text).
    """
    errors: list[str] = []
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        skill_file = skill_dir / "SKILL.md"
        skill_text = skill_file.read_text(encoding="utf-8")
        ref_dir = skill_dir / "references"
        if not ref_dir.exists():
            continue
        for ref_file in sorted(ref_dir.glob("*.md")):
            filename = ref_file.name
            # Check if the filename appears anywhere in SKILL.md
            if filename not in skill_text:
                errors.append(
                    f"{skill_dir.name}: reference file '{filename}' is not "
                    f"referenced in SKILL.md — may be unreachable dead code"
                )
    return errors

def validate_change_impact_manifest() -> list[str]:
    errors: list[str] = []
    path = ROOT / "governance/change-impact-manifest.json"
    if not path.exists():
        return ["governance/change-impact-manifest.json is required"]
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"owner", "authoritative_sources", "consumers", "validators", "tests", "evaluations"}
    for cid, spec in data.get("contracts", {}).items():
        missing = required - set(spec)
        if missing:
            errors.append(f"impact contract {cid}: missing {sorted(missing)}")
        for key in required - {"owner"}:
            for target in spec.get(key, []):
                if not (ROOT / target).exists():
                    errors.append(f"impact contract {cid}: missing target {target}")
    return errors

def validate_domain_contract_entrypoints() -> list[str]:
    errors = []
    for skill_dir in sorted(path.parent for path in ROOT.glob("*/SKILL.md")):
        entry = skill_dir / "scripts/validate_decision_contract.py"
        if not entry.exists():
            errors.append(f"{skill_dir.name}: missing decision contract validator")
        elif "validate_decision_contract.py" not in (skill_dir / "SKILL.md").read_text(encoding="utf-8"):
            errors.append(f"{skill_dir.name}: decision contract validator is not routed")
    return errors


def main() -> int:
    skill_dirs = sorted(path.parent for path in ROOT.glob("*/SKILL.md"))
    errors: list[str] = []

    # Core skill validation
    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir))

    # Weight validation
    errors.extend(validate_video_weights())

    # agents/openai.yaml validation
    errors.extend(validate_agents_yaml())

    # README inventory sync
    errors.extend(validate_readme_inventory())

    # Artifact detection
    errors.extend(validate_no_artifacts())

    # Cross-skill version consistency
    errors.extend(validate_cross_skill_versions())

    # Reference routing completeness
    errors.extend(validate_reference_routing())
    errors.extend(validate_change_impact_manifest())
    errors.extend(validate_domain_contract_entrypoints())

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Repository validation passed for {len(skill_dirs)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
