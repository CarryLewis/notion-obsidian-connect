# Notion AI Prompt — Context as Obsidian Wikilink Vocabulary

`Context` is not free prose. It is a **small set of reusable thinking anchors** that sync into Obsidian as Wikilinks:

```text
[[Clinical reasoning]]; [[Patient language]]
```

Sync rule: terms separated by `;` / `；` become `[[term]]` under `## Context`.

**Constraint (locked):** one capture belongs to **one** thinking node. Do not cover multiple topic boards in a single Context field.

Paste the prompt below into Notion AI standing instructions (or use together with the main capture rules).

---

## Prompt (copy from here)

```text
【Context 字段专项规则】

Context 不是场景描写句，也不是目录，也不是摘要。
它只回答：这条思考以后要反复回到哪一个节点。
同步后形态：
[[锚点A]]
或（例外）
[[锚点A]]; [[锚点B]]

你在填写【Context】时，必须遵守下面硬约束：

0) 单一归属（最重要）
- 默认只写 1 个锚点。
- 只有同一思考明显同时挂在两个「已有」节点时，才写第 2 个。
- 禁止 3 个及以上。禁止一次覆盖多个板块/领域/场景。
- 相关但次要的主题不要塞进 Context；放到 Observation / Interpretation / Page Body，或等确认后进 Related Information。

1) 概括性（短概念名，不是情景句）
- 每个词条是可反复回来想的概念名，不是当下细节。
- 好：Clinical reasoning / Patient language / Medical learning workflow
- 差：这个病人说头晕 / 今晚三点的事 / 我觉得奇怪
- 「概括」不等于「打开一整块学科目录」。不要为了覆盖面去补 Clinical communication、Night shift、Vestibular categories 这类旁系板块。

2) 词表复用（禁止近义新造）
- 必须从下面【已有 Context 词表】里选，沿用原词，不要近义改写。
- 找不到足够接近的：Context 写「（空）」，或另起一行标【候选新锚点：…】等我确认。禁止直接写入新词。
- 只有我明确说「这是新锚点，写入词表」时，才允许新增，并保持可长期复用。

3) 形态
- 每个锚点用 2–6 个词（中文可 4–12 字）压成一个可复用概念名。
- 一个锚点 = 一个可反复回来思考的节点，不是一句话解释。

4) 分隔格式
- 若有第 2 个锚点，只用分号断开：中文「；」或英文「;」
- 不要用逗号、顿号、换行列表作为主分隔
- 不要在 Context 里写 [[ ]]（系统同步时会自动加）
- 不要在 Context 里写解释性长句

【已有 Context 词表 — 只能从这里选】
Clinical reasoning
Clinical workflow
Diagnostic closure
Observation before diagnosis
Patient language
Risk sensemaking
Medical learning workflow
Distant knowledge
Learning as reconstruction
Learning system design
Deep work training
Feedback loop
AI-assisted learning
Thinking system
Reading as trigger
Public methodology
Knowledge observatory
Personal identity architecture
Public narrative

近义对照（见到这些想法时，用右边已有词，不要另造）：
- 临床沟通 / 夜班推理 / 诊断猜病 → Clinical reasoning
- 病人怎么说头晕 / vestibular language → Patient language
- 先看现象再下诊断 → Observation before diagnosis
- 学习流程 / 主题日 / 标准化训练 → Medical learning workflow
- 远距离知识 / 读文献触发 → Distant knowledge
- 思考库 / Thinking Vault 方法 → Thinking system

【Context 输出格式】
【Context】
锚点A
（默认一个；例外才「锚点A；锚点B」；找不到写「（空）」）

【自检清单】写完 Context 后默默检查：
- 是不是只挂了这一条思考真正所属的节点，而不是多个板块？
- 是否从已有词表原词复用，而不是新造近义词？
- 是否短、稳、可做笔记名？
- 是否默认 1 个、最多 2 个、用分号分隔？

【与其它字段分工】
- Context：这条思考连到哪一个已有节点（未来变成 [[wikilink]]）
- Observation / Interpretation：这一次的具体内容
- Page Body：更细致的反思展开
- Tags：怎么筛（medicine / neurology），不是思考锚点
- Related Information：已确认关联的页面（Relation），不是 Context 的替代品

【示例】
用户想法：今天夜班病人一直说头晕，但我不认为是 vertigo。

好的 Context（只挂主节点）：
Patient language

也可（同一思考确实也是临床推理时，最多再加一个已有词）：
Patient language；Clinical reasoning

不好的 Context（一次覆盖多个板块）：
Patient language of dizziness；Clinical communication；Vestibular clinical categories；Night shift observation

不好的 Context（情景句）：
夜班时有个病人反复说头晕让我很困惑，可能不是眩晕
```

---

## Minimal add-on (if you only want a short insert)

```text
Context 硬约束：默认只写 1 个已有锚点，最多 2 个；禁止一次覆盖多个板块；必须从已有词表原词复用，找不到就留空或标【候选新锚点】等确认；不要写长句；系统会同步成 [[锚点]]。
```
