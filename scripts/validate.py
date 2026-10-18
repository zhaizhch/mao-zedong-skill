#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""仓库自检：语料结构、生成物同步、SKILL.md 契约、示例标注。

    python3 scripts/validate.py

任何一项失败即以非零码退出，可直接用于 CI。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_index  # noqa: E402

TYPES = {"quote", "poem", "motto", "letter"}
REQUIRED = {"id", "type", "text", "source", "year", "themes", "note"}
errors: list[str] = []
warnings: list[str] = []


def check_corpus(data: dict) -> None:
    meta = data.get("meta", {})
    if not meta.get("version"):
        errors.append("corpus.meta.version 缺失")

    themes = data.get("themes", [])
    keys = [t.get("key") for t in themes]
    if len(keys) != len(set(keys)):
        errors.append("主题 key 重复")
    if not themes:
        errors.append("主题列表为空")

    entries = data.get("entries", [])
    if len(entries) < 100:
        warnings.append(f"语料仅 {len(entries)} 条，覆盖面可能不足")

    seen: dict[str, str] = {}
    usage: dict[str, int] = {k: 0 for k in keys}
    for e in entries:
        eid = e.get("id", "<no-id>")
        missing = REQUIRED - e.keys()
        if missing:
            errors.append(f"{eid}: 缺少字段 {sorted(missing)}")
            continue
        if eid in seen:
            errors.append(f"{eid}: id 重复")
        seen[eid] = e["text"]
        if e["type"] not in TYPES:
            errors.append(f"{eid}: 非法 type {e['type']}")
        if not re.fullmatch(r"\d{4}", str(e["year"])):
            errors.append(f"{eid}: year 应为 4 位年份，实际 {e['year']!r}")
        if not e["themes"]:
            errors.append(f"{eid}: themes 为空")
        for k in e["themes"]:
            if k not in usage:
                errors.append(f"{eid}: 未知主题 {k}")
            else:
                usage[k] += 1
        if e["type"] == "poem" and len(e["text"]) > 60:
            errors.append(f"{eid}: 诗词摘引过长（{len(e['text'])} 字），只收单句/对句，避免整首转载")
        if e.get("attribution") not in (None, "certain", "widely-attributed"):
            errors.append(f"{eid}: attribution 取值非法")

    for k, n in usage.items():
        if n < 3:
            warnings.append(f"主题 {k} 仅 {n} 条，建议补充")


def check_generated(data: dict) -> None:
    md = build_index.build_markdown(data)
    idx = json.dumps(build_index.build_index(data), ensure_ascii=False, indent=2) + "\n"
    if not build_index.MD.exists() or build_index.MD.read_text(encoding="utf-8") != md:
        errors.append("references/01-corpus.md 与语料不同步，运行 python3 scripts/build_index.py")
    if not build_index.INDEX.exists() or build_index.INDEX.read_text(encoding="utf-8") != idx:
        errors.append("assets/index.json 与语料不同步，运行 python3 scripts/build_index.py")


def check_skill_md() -> str:
    path = ROOT / "SKILL.md"
    if not path.exists():
        errors.append("SKILL.md 缺失")
        return ""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("SKILL.md 必须以 YAML frontmatter 开头")
        return text
    end = text.find("\n---", 4)
    if end == -1:
        errors.append("SKILL.md frontmatter 未闭合")
        return text
    fm = text[4:end]
    name = re.search(r"^name:\s*(.+)$", fm, re.M)
    desc = re.search(r"^description:\s*(.+)$", fm, re.M)
    if not name:
        errors.append("SKILL.md frontmatter 缺少 name")
    elif name.group(1).strip() != ROOT.name:
        errors.append(f"SKILL.md name（{name.group(1).strip()}）与目录名（{ROOT.name}）不一致")
    if not desc:
        errors.append("SKILL.md frontmatter 缺少 description")
    elif len(desc.group(1).strip()) > 1024:
        errors.append("SKILL.md description 超过 1024 字符")

    body = text[end:]
    for token in ("【收束】", "【仿写】", "出处", "不得"):
        if token not in body:
            errors.append(f"SKILL.md 正文缺少关键约束：{token}")
    return body


def check_refs_and_examples() -> None:
    for rel in (
        "references/02-poetics.md",
        "references/03-rhetoric.md",
        "references/04-scenarios.md",
        "references/05-redlines.md",
        "README.md",
        "LICENSE",
    ):
        if not (ROOT / rel).exists():
            errors.append(f"缺少文件 {rel}")

    examples = list((ROOT / "examples").glob("*.md"))
    if len(examples) < 2:
        errors.append("examples/ 至少需要 2 个示例")
    for f in examples:
        t = f.read_text(encoding="utf-8")
        if "【收束】" not in t:
            errors.append(f"{f.name}: 示例缺少【收束】区块")
        if "【仿写】" not in t:
            errors.append(f"{f.name}: 示例缺少【仿写】标注")


def main() -> int:
    with build_index.CORPUS.open(encoding="utf-8") as f:
        data = json.load(f)
    check_corpus(data)
    check_generated(data)
    body = check_skill_md()
    check_refs_and_examples()

    if body:
        for token in ("mao.py", "brief"):
            if token not in body:
                warnings.append(f"SKILL.md 未提及 {token}，运行时可能漏用脚本")

    for w in warnings:
        print(f"[warn] {w}")
    for e in errors:
        print(f"[error] {e}")
    if errors:
        print(f"\n自检失败：{len(errors)} 项错误，{len(warnings)} 项警告。")
        return 1
    print(f"自检通过：{len(data['entries'])} 条语料，{len(data['themes'])} 个主题，0 错误。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
