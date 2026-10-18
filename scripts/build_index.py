#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 assets/corpus.json 生成 references/01-corpus.md 与 assets/index.json。

用法：
    python3 scripts/build_index.py            # 生成
    python3 scripts/build_index.py --check    # 只检查是否已同步（CI 用）
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "assets" / "corpus.json"
INDEX = ROOT / "assets" / "index.json"
MD = ROOT / "references" / "01-corpus.md"

TYPE_LABEL = {"quote": "文·讲话", "poem": "诗词", "motto": "题词", "letter": "书信"}


def quote(text: str) -> str:
    """用中文引号包裹原文，内部引号降级为『』，避免嵌套引号。"""
    return "“" + text.replace("“", "『").replace("”", "』") + "”"


def load() -> dict:
    with CORPUS.open(encoding="utf-8") as f:
        return json.load(f)


def build_markdown(data: dict) -> str:
    themes = data["themes"]
    entries = data["entries"]
    by_key = {t["key"]: t for t in themes}

    # 每条按第一主题归位，保证全库不重复
    grouped: dict[str, list] = {t["key"]: [] for t in themes}
    for e in entries:
        grouped[e["themes"][0]].append(e)
    for lst in grouped.values():
        lst.sort(key=lambda x: (x["year"], x["id"]))

    out: list[str] = []
    out.append("# 毛泽东语料库")
    out.append("")
    out.append("> 本文件由 `scripts/build_index.py` 从 `assets/corpus.json` 自动生成，请勿手工编辑。")
    out.append(f"> 共 {len(entries)} 条 · {len(themes)} 个主题 · 语料版本 {data['meta']['version']}")
    out.append("")
    out.append("**图例**：`文·讲话` = 文章、报告、讲话；`诗词` = 旧体诗词；`题词` = 题词、校训；`书信` = 书信。")
    out.append("带 ⚠ 的条目属于**流传广但版本不一**，引用时应说明“据传/通行说法”，不要当作可考原文硬引。")
    out.append("")
    out.append("**引用格式**：`“原文。”——《篇名》（年份）`。仿写一律另起一行并标注【仿写】。")
    out.append("")

    out.append("## 主题索引")
    out.append("")
    out.append("| 主题 | 条目 | 适合收束 |")
    out.append("|---|---:|---|")
    for t in themes:
        out.append(f"| [{t['name']}](#{t['key']}) | {len(grouped[t['key']])} | {t['intro'].split('。')[0]} |")
    out.append("")
    out.append("---")
    out.append("")

    for t in themes:
        key = t["key"]
        out.append(f'<a id="{key}"></a>')
        out.append("")
        out.append(f"## {t['name']}（{len(grouped[key])} 条）")
        out.append("")
        out.append(f"> {t['intro']}")
        out.append("")
        for e in grouped[key]:
            flag = " ⚠" if e.get("attribution") == "widely-attributed" else ""
            cross = "、".join(by_key[k]["name"] for k in e["themes"][1:] if k in by_key)
            out.append(f"**{e['id']}**｜{TYPE_LABEL.get(e['type'], e['type'])}{flag}")
            meta = f"——{e['source']}（{e['year']}）"
            if cross:
                meta += f"　·　另见：{cross}"
            out.append(f"{quote(e['text'])}{meta}")
            out.append(f"用法：{e['note']}")
            out.append("")
        out.append("---")
        out.append("")

    out.append("## 出处与版权说明")
    out.append("")
    out.append("1. 原文引用仅用于评论、教学与写作示范，单条均为短句摘引，不收录整篇作品。")
    out.append("2. 标 ⚠ 的条目版本不一，写作时应降级为“据传”或直接换用可考条目。")
    out.append("3. 仿写不是原文。任何仿写都必须标注【仿写】，不得混入引文，不得伪造成“毛泽东说”。")
    out.append("4. 语料整理与注释部分以 CC BY 4.0 授权；原文权利归权利人所有。")
    out.append("")
    return "\n".join(out)


def build_index(data: dict) -> dict:
    return {
        "meta": data["meta"],
        "themes": data["themes"],
        "entries": [
            {
                "id": e["id"],
                "type": e["type"],
                "text": e["text"],
                "source": e["source"],
                "year": e["year"],
                "themes": e["themes"],
                "note": e["note"],
                "attribution": e.get("attribution", "certain"),
            }
            for e in data["entries"]
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只校验生成物是否与语料同步")
    args = ap.parse_args()

    data = load()
    md = build_markdown(data)
    idx = json.dumps(build_index(data), ensure_ascii=False, indent=2) + "\n"

    if args.check:
        ok = True
        if not MD.exists() or MD.read_text(encoding="utf-8") != md:
            print(f"[stale] {MD.relative_to(ROOT)} 与语料不同步，请运行 python3 scripts/build_index.py", file=sys.stderr)
            ok = False
        if not INDEX.exists() or INDEX.read_text(encoding="utf-8") != idx:
            print(f"[stale] {INDEX.relative_to(ROOT)} 与语料不同步，请运行 python3 scripts/build_index.py", file=sys.stderr)
            ok = False
        if ok:
            print("索引与语料同步。")
        return 0 if ok else 1

    MD.parent.mkdir(parents=True, exist_ok=True)
    MD.write_text(md, encoding="utf-8")
    INDEX.write_text(idx, encoding="utf-8")
    print(f"已生成 {MD.relative_to(ROOT)}（{len(data['entries'])} 条）与 {INDEX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
