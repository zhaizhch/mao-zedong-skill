# 毛泽东语料库 · 收束 skill

> 给刚干完的活，配一句有出处的定调、一句标明的仿写、一句落到动作的鞭策。

这是一个 **Agent Skill**：装进 Claude Code、DeepSeek Harness、Cursor 等支持 `SKILL.md` 的智能体后，它会在任务收尾时用毛泽东的语料与文风，写一段**不空、不假、不颂圣**的总结。

不是语录合集，是**收束工具**。语料只是弹药，准头在方法。

---

## 它解决三个具体问题

| 痛点 | 常见写法 | 这个 skill 的做法 |
|---|---|---|
| 总结写成八股 | “在……领导下，圆满完成各项任务” | 先写事实，再找机制，最后才修辞 |
| 引用张冠李戴 | “毛主席说过：‘世上无难事，只怕有心人’” | 154 条可考语料，标 ⚠ 的自动降级为“据传” |
| 鼓励变成鸡汤 | “加油，你一定行！” | 指到具体动作、具体标准，对事不对人 |

---

## 30 秒上手

```bash
git clone https://github.com/zhaizhch/mao-zedong-skill.git
cd mao-zedong-skill
./install.sh                 # 装到 ~/.dsh/skills 和 ~/.agents/skills

python3 scripts/mao.py brief --scenario code
```

然后把技能目录交给你的智能体，或者在对话里直接说：

> 用 mao-zedong 这个 skill，给刚才这次排障写个收束。

---

## 输出长什么样

```
【收束】
原文：“调查就像‘十月怀胎’，解决问题就像‘一朝分娩’。”——《反对本本主义》（1930）
仿写：两周翻日志、两天复现，看着慢；可正是这两天，把“偶发”摁成了“必现”。【仿写】
鞭策：趁根因还热，把这条复现路径写成脚本进 CI——下次它再冒头，五分钟摁死。
```

三行，各司其职：**原文定调，仿写落地，鞭策指路**。

再看一个反例，体会差别：

```
【收束】
正如毛主席所说：“世上无难事，只怕有心人。”这次成功充分体现了团队的强大战斗力！
```

问题有三：出处是假的、没有一个字对应本次任务、全是形容词。这正是本 skill 要帮你删掉的东西。

---

## 安装

### DeepSeek Harness

```bash
# 用户级（所有项目可用）
ln -sfn "$PWD" ~/.dsh/skills/mao-zedong

# 或项目级
mkdir -p .dsh/skills && ln -sfn "$PWD" .dsh/skills/mao-zedong
```

### Claude Code / 兼容 Agent Skills 的工具

```bash
ln -sfn "$PWD" ~/.claude/skills/mao-zedong
```

### 通用

任何扫描 `<root>/<name>/SKILL.md` 的加载器都可以用。把整个目录放进去即可，无需构建、无第三方依赖（只要 Python 3.8+）。

---

## 用法

### 智能体自动触发

任务收尾、复盘、里程碑、写作结语时，skill 会按 `SKILL.md` 的四步流程工作：判定场景 → 选料 → 仿写 → 自检。

### 命令行

| 命令 | 作用 |
|---|---|
| `python3 scripts/mao.py themes` | 列出 15 个主题与 12 类场景 |
| `python3 scripts/mao.py search 调查` | 全文 / 主题检索 |
| `python3 scripts/mao.py pick --scenario code` | 按场景抽一条 |
| `python3 scripts/mao.py pick --scenario failure --type poem` | 只抽诗词 |
| `python3 scripts/mao.py brief --scenario learning` | **推荐**：生成收束语料包（候选原文 + 句式 + 提示） |

`--seed` 可复现抽取结果，`--json` 便于二次处理。

### 12 类场景

`code` · `research` · `writing` · `design` · `launch` · `failure` · `learning` · `collab` · `milestone` · `startup` · `urgent` · `review`

每类场景的完整范例见 [`references/04-scenarios.md`](references/04-scenarios.md)。

---

## 语料库

**154 条**，全部短句摘引，按 **15 个主题**编排：

| 主题 | 条数 | 主题 | 条数 |
|---|---:|---|---:|
| 实践与认识 | 6 | 工作方法 | 11 |
| 调查研究 | 11 | 批评与复盘 | 7 |
| 矛盾与本质 | 8 | 时间与紧迫 | 5 |
| 战略与战术 | 13 | 青年与希望 | 7 |
| 困难与坚持 | 22 | 团结与同心 | 5 |
| 群众与协作 | 11 | 胆略与气势 | 17 |
| 学习与本领 | 13 | 文风与表达 | 8 |
| 创造与创业 | 10 | | |

类型：文章讲话 106 · 诗词 40 · 题词 6 · 书信 2。

每条都有：原文、篇名、年份、主题、一句话用法。
**9 条**属“流传广但版本不一”，在语料与生成文档中统一标 ⚠，引用时强制降级为“据传”。

数据源是 [`assets/corpus.json`](assets/corpus.json)，Markdown 由脚本生成，不允许手改——这样引用与索引永远一致。

---

## 仓库结构

```
SKILL.md                     # 主入口：四步流程 + 输出契约 + 硬约束
references/
  01-corpus.md               # 154 条语料（自动生成）
  02-poetics.md              # 诗词意象、场合速查、诗性短句仿写
  03-rhetoric.md             # 六个句法装置、四段结构、三段对照改写
  04-scenarios.md            # 12 类场景的完整收束范例
  05-redlines.md             # 边界：不伪造、必标注、不崇拜、不政治
assets/
  corpus.json                # 唯一数据源
  index.json                 # 检索索引（自动生成）
scripts/
  mao.py                     # 检索 / 抽签 / 语料包
  build_index.py             # 生成 Markdown 与索引
  validate.py                # 自检（CI 使用）
examples/                    # 两个完整示例，含“为什么选这条”与反例
```

---

## 四条设计原则

1. **原文必须真。** 只能从语料库取，或取确知出处的名句；标 ⚠ 的必须写“据传”。
2. **仿写必须标。** 独立成行标【仿写】，不得混入引文，不得写成“毛泽东说”。
3. **不搞个人崇拜。** 禁用“伟大领袖”“最高指示”一类词；语气是同志式的，不是颂圣的。
4. **不碰现实政治。** 不评价现实政治人物、政策与历史争议；不把“敌我”框架用于真实的人。

完整边界见 [`references/05-redlines.md`](references/05-redlines.md)。

---

## 常见问题

**Q：这是不是把毛泽东的话拿来搞笑？**
不是。语料只取可考出处，仿写全部标注，语气克制。它更像一个“中文议论文写作教练”，只是选了一个句法特征极其鲜明的范本。

**Q：为什么不直接让模型自由发挥？**
自由发挥的常见结果是：假引用、空口号、形容词通胀。这个 skill 用**结构化语料 + 强制标注 + 六步仿写法**把这三个坑堵住。

**Q：能改成其他作者的风格吗？**
能。把 `assets/corpus.json` 换成目标语料、把 `SKILL.md` 的边界与句式说明改写即可，脚本与校验逻辑通用。

**Q：为什么不收录整首诗、整篇文章？**
版权，以及用法。收束只需要一句；整篇转载既无必要，也不合适。

**Q：会不会每轮都强行加一段？**
不会。`SKILL.md` 明确要求：只在任务真正告一段落、或用户点名要时收束，且一轮只出现一次。

---

## 贡献

见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。新增条目必须满足：**两个独立来源可核**，否则标 `widely-attributed`。

```bash
python3 scripts/build_index.py   # 改完语料后重新生成
python3 scripts/validate.py      # 提交前自检
```

---

## 许可

- 整理、注释、脚本、文档：**CC BY 4.0**
- 原文引用：仅作评论、教学与写作示范之用，权利归权利人所有。

详见 [`LICENSE`](LICENSE)。

---

## 免责声明

本项目是**写作方法**工具，不构成对任何历史人物、事件、政治主张的评价或背书。使用者应自行确保输出内容符合所在平台与地区的法律法规。请勿将本工具用于制作政治动员材料、人身攻击或伪造引文。
