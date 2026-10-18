# 贡献指南

## 可以贡献什么

- 新增语料条目（最欢迎，但要求最严）
- 修正出处、年份、文字错误
- 新增场景模板（`references/04-scenarios.md`）
- 改进脚本、校验规则、跨平台兼容
- 英文文档

## 新增语料：硬标准

1. **两个独立来源可核**，且至少一个是权威出版物（如《毛泽东选集》《毛泽东文集》《毛泽东诗词集》）。
2. 只收**短句**：一句话或一个对句。不收整段、整首、整篇。
3. 必须有明确的**篇名与年份**。只知“某次谈话”而不确定时间的，不要编年份。
4. 版本有异的，标 `"attribution": "widely-attributed"`，并在注释里写清分歧。
5. 每条都要写 `note`：**一句话说明“这条适合用来收束什么”**，不要复述原文。

## 数据格式

编辑 `assets/corpus.json`，在 `entries` 数组末尾追加：

```json
{
  "id": "q156",
  "type": "quote",
  "text": "原文。",
  "source": "《篇名》",
  "year": "1945",
  "themes": ["practice", "method"],
  "note": "一句话用法。",
  "attribution": "certain"
}
```

- `id`：递增，不复用，不删除已发布的 id。
- `type`：`quote`（文章/讲话）、`poem`、`motto`（题词）、`letter`。
- `themes`：第一个是主主题（决定它在 `01-corpus.md` 中的归位），可带 1–3 个。
- `attribution`：`certain` 可省略；不确定的必须写 `widely-attributed`。

## 提交前必须跑

```bash
python3 scripts/build_index.py
python3 scripts/validate.py
```

两条都通过再提 PR。CI 会跑同样的检查，`01-corpus.md` 与 `index.json` 未同步会直接失败。

## PR 描述请写清

- 新增/修改了哪几条，id 分别是多少
- 出处依据（书名、版次、页码，或可访问的权威链接）
- 是否影响已有场景模板

## 不接受

- 无法核实的“据说”“网上流传”
- 整首诗词、整篇文章
- 美化个人崇拜、政治动员类的条目
- 把仿写当原文提交

## 提交信息格式

```
feat(corpus): 新增 q156「……」(《篇名》1945)
fix(corpus): 修正 q042 年份 1944→1945
docs(scenarios): 补充 milestone 场景范例
```
