#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""毛泽东语料库检索与“收束语料包”生成器（纯标准库，无第三方依赖）。

用法示例：
    python3 scripts/mao.py themes
    python3 scripts/mao.py search 调查
    python3 scripts/mao.py pick --scenario code
    python3 scripts/mao.py pick --scenario failure --type poem
    python3 scripts/mao.py brief --scenario code
    python3 scripts/mao.py brief --scenario learning --seed 7 --json

设计原则：脚本只负责“选料”和“给句式”，不代写仿写。
仿写必须由模型结合具体任务内容完成，并标注【仿写】。
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "assets" / "index.json"

SCENARIOS = {
    "code": {
        "label": "代码交付 / 修 bug",
        "themes": ["practice", "method", "investigation"],
        "hint": "把“跑通了什么、验证了什么、还差什么”讲实，别总结成口号。",
    },
    "research": {
        "label": "调研 / 分析",
        "themes": ["investigation", "contradiction", "learning"],
        "hint": "结论要能追溯到材料；说清主要矛盾是什么、被排除了什么。",
    },
    "writing": {
        "label": "写作 / 文档 / 汇报",
        "themes": ["writing", "method", "criticism"],
        "hint": "先问“写给谁看”，再检查有没有空话、装腔、开中药铺。",
    },
    "design": {
        "label": "设计 / 方案取舍",
        "themes": ["contradiction", "creation", "masses"],
        "hint": "讲清约束与权衡：满足了谁的什么需求，牺牲了什么。",
    },
    "launch": {
        "label": "上线 / 发布 / 攻坚",
        "themes": ["strategy", "courage", "time"],
        "hint": "战略上不怕，战术上报清风险与回滚；别只写“圆满完成”。",
    },
    "failure": {
        "label": "受挫 / 返工 / 事故",
        "themes": ["perseverance", "criticism", "contradiction"],
        "hint": "先认账，再给根因和修复动作；用“看到成绩、看到光明”的结构收尾。",
    },
    "learning": {
        "label": "学习 / 转型 / 补课",
        "themes": ["learning", "practice", "time"],
        "hint": "写清“原来不会什么、现在会到什么程度、下一步练什么”。",
    },
    "collab": {
        "label": "协作 / 跨部门",
        "themes": ["masses", "unity", "criticism"],
        "hint": "把功劳分出去，把分歧摆到桌面上，把下一步责任人写出来。",
    },
    "milestone": {
        "label": "里程碑 / 阶段完成",
        "themes": ["perseverance", "time", "youth"],
        "hint": "庆祝一句就够，重点写“这只是第一步”和下一段路。",
    },
    "startup": {
        "label": "从零搭建 / 重构 / 开源首发",
        "themes": ["creation", "strategy", "courage"],
        "hint": "强调“白纸优势”和“自己动手”，但别许诺没验证过的东西。",
    },
    "urgent": {
        "label": "抢工期 / 拖到最后",
        "themes": ["time", "method", "courage"],
        "hint": "只争朝夕要落到“今天先干哪一件”，否则就是新的空话。",
    },
    "review": {
        "label": "复盘 / 评审",
        "themes": ["criticism", "method", "contradiction"],
        "hint": "对事不对人，给出可复用的规则，而不是一份情绪清单。",
    },
}

PATTERNS = [
    ("纠偏式", "不是……，而是……。", "用来否定一个流行的错做法，再立起正确做法。"),
    ("断语式", "……，这就是……。", "把一段经验压缩成一个可命名的东西。"),
    ("排比收束", "……必须……，……必须……，……必须……。", "三句为限，多了就成口号。"),
    ("设问式", "……么？……呢？", "先替读者问出疑问，再回答。"),
    ("对比式", "战略上……，战术上……。", "一个态度配一个动作，防止空喊。"),
    ("递进式", "……，而且……，更重要的是……。", "把结论往深处推一层。"),
    ("比喻式", "好比……，……。", "用一个具体物象解释抽象机制（梨子、种子、土地、桥或船）。"),
    ("回望式", "……过去了，……。", "用时间尺度收束，适合里程碑与长项目。"),
]


def load() -> dict:
    if not INDEX.exists():
        raise SystemExit("缺少 assets/index.json，请先运行 python3 scripts/build_index.py")
    with INDEX.open(encoding="utf-8") as f:
        return json.load(f)


def cite(e: dict) -> str:
    flag = "（据传）" if e.get("attribution") == "widely-attributed" else ""
    text = e["text"].replace("“", "『").replace("”", "』")
    return f"“{text}”——{e['source']}（{e['year']}）{flag}"


def cmd_themes(data: dict, as_json: bool) -> int:
    if as_json:
        print(json.dumps(data["themes"], ensure_ascii=False, indent=2))
        return 0
    counts: dict[str, int] = {}
    for e in data["entries"]:
        counts[e["themes"][0]] = counts.get(e["themes"][0], 0) + 1
    print("主题（按第一主题计数）：")
    for t in data["themes"]:
        print(f"  {t['key']:<14} {t['name']:<8} {counts.get(t['key'], 0):>3} 条   {t['intro']}")
    print("\n场景：")
    for key, s in SCENARIOS.items():
        print(f"  {key:<14} {s['label']}（主线：{', '.join(s['themes'])}）")
    return 0


def cmd_search(data: dict, query: str, as_json: bool) -> int:
    q = query.lower()
    theme_names = {t["key"]: t["name"] for t in data["themes"]}
    hits = [
        e for e in data["entries"]
        if q in e["text"].lower()
        or q in e["source"].lower()
        or q in e["note"].lower()
        or any(q in theme_names.get(k, "").lower() or q in k for k in e["themes"])
    ]
    if as_json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
        return 0
    if not hits:
        print(f"未找到与“{query}”相关的条目。试试主题名，如：实践、调查、矛盾、战略、困难、群众、学习、方法、复盘、时间、青年、团结、胆略、文风、创造。")
        return 1
    print(f"找到 {len(hits)} 条：\n")
    for e in hits:
        print(f"[{e['id']}] {cite(e)}")
        print(f"      主题：{' / '.join(theme_names.get(k, k) for k in e['themes'])}｜用法：{e['note']}")
    return 0


def _pool(data: dict, themes: list[str], types: list[str] | None) -> list[dict]:
    pool = [
        e for e in data["entries"]
        if any(t in e["themes"] for t in themes)
        and (not types or e["type"] in types)
    ]
    # 可考出处优先，再按主题命中数排序
    pool.sort(key=lambda e: (e.get("attribution") == "widely-attributed", -sum(t in e["themes"] for t in themes)))
    return pool


def cmd_pick(data: dict, scenario: str, types: list[str] | None, seed: int | None, as_json: bool) -> int:
    if scenario not in SCENARIOS:
        raise SystemExit(f"未知场景 {scenario}，可选：{', '.join(SCENARIOS)}")
    s = SCENARIOS[scenario]
    pool = _pool(data, s["themes"], types)
    if not pool:
        raise SystemExit("没有匹配条目，放宽 --type 再试。")
    rng = random.Random(seed if seed is not None else random.randrange(1 << 30))
    top = pool[: max(1, len(pool) // 2)]  # 只在较好的半数里抽，避免抽到边缘条目
    e = rng.choice(top)
    if as_json:
        print(json.dumps(e, ensure_ascii=False, indent=2))
    else:
        print(cite(e))
        print(f"主题：{' / '.join(e['themes'])}｜用法：{e['note']}")
    return 0


def cmd_brief(data: dict, scenario: str, seed: int | None) -> int:
    if scenario not in SCENARIOS:
        raise SystemExit(f"未知场景 {scenario}，可选：{', '.join(SCENARIOS)}")
    s = SCENARIOS[scenario]
    theme_names = {t["key"]: t["name"] for t in data["themes"]}
    rng = random.Random(seed if seed is not None else 20261018)

    quotes = _pool(data, s["themes"], ["quote", "motto", "letter"])[:6]
    poems = _pool(data, s["themes"], ["poem"])[:4]
    rng.shuffle(quotes)
    rng.shuffle(poems)
    quotes = quotes[:3]
    poems = poems[:2]
    pats = rng.sample(PATTERNS, 3)

    print(f"【语料包】场景：{s['label']}")
    print(f"主线：{' → '.join(theme_names.get(t, t) for t in s['themes'])}")
    print()
    print("候选原文（可考出处优先，挑一句即可，不要堆）")
    for i, e in enumerate(quotes, 1):
        print(f"  {i}. {cite(e)}")
        print(f"     用法：{e['note']}")
    if poems:
        print()
        print("诗性备选（需要一点气势时用，全文只引一句）")
        for i, e in enumerate(poems, 1):
            print(f"  {i}. {cite(e)}")
            print(f"     用法：{e['note']}")
    print()
    print("可套句式")
    for name, form, why in pats:
        print(f"  · {name}：{form}")
        print(f"    {why}")
    print()
    print(f"场景提示：{s['hint']}")
    print()
    print("收束约束：原文 ≤1 句；仿写 1 句并标【仿写】；鞭策 1 句，落到下一步动作；总长 ≤6 行。")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="毛泽东语料库检索工具")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("themes", help="列出主题与场景")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("search", help="全文/主题检索")
    p.add_argument("query")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("pick", help="按场景抽一条")
    p.add_argument("--scenario", required=True)
    p.add_argument("--type", default=None, help="quote/poem/motto/letter，逗号分隔")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("brief", help="生成收束语料包（推荐）")
    p.add_argument("--scenario", required=True)
    p.add_argument("--seed", type=int, default=None)

    args = ap.parse_args()
    data = load()
    if args.cmd == "themes":
        return cmd_themes(data, args.json)
    if args.cmd == "search":
        return cmd_search(data, args.query, args.json)
    if args.cmd == "pick":
        types = [t.strip() for t in args.type.split(",")] if args.type else None
        return cmd_pick(data, args.scenario, types, args.seed, args.json)
    if args.cmd == "brief":
        return cmd_brief(data, args.scenario, args.seed)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
