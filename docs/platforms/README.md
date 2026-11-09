# 平台联动与内容整理

## 已实现 · Notion → Obsidian

Notion 负责捕捉和维护原始思考。同步器以只读连接读取 Thinking 数据库的属性和正文，用 Notion 页面的 `source_id` 识别记录，再在 Obsidian vault 里生成 Markdown。SQLite 保存同步状态，供后续更新、重命名和软归档使用。

`Context` 里填写打算长期复用的纯文本锚点，已确认的记录关联放在 `Related Information`。同步器把这两处转换成 Obsidian 链接。普通正文用纯文本或常规格式，避免双中括号把普通词变成图谱节点。

- [数据库字段与链接规则](../architecture/NOTION_THINKING_DATABASE_CHECKLIST.md)
- [Notion AI 录入规则](../architecture/NOTION_AI_THINKING_CAPTURE_RULES_PROMPT.md)
- [本地部署及同步验收](../LOCAL_SETUP.md)

## 待接入 · 印象笔记 → 本地整理

第一步是用印象笔记客户端按笔记本导出 ENEX，在仓库外保留原件。先选少量样例，检查标题、正文、时间、标签、原始链接和附件。整理过程中给每条材料记录来源、批次和稳定的去重标识。内容和附件核对通过后，再决定是留在原笔记本、生成 Obsidian Markdown，还是收录到个人知识库。[印象笔记官方导出说明](https://help.yinxiang.com/hc/articles/63080)

首批验收至少覆盖普通文字、带附件的笔记和重复导出的笔记。这里记录的是接入思路，导入程序与真实批次验收待完成。

## 设计中 · Obsidian → Notion

写回以单篇笔记和明确允许编辑的字段为起点。通过 `source_id` 找到原页，分别比较两端与上次成功同步时的内容，先给出改动预览。遇到同一字段两边都改了，保留两个版本，由用户决定。写入权限与当前只读集成分开，删除、冲突、重复提交和部分失败各自验收。[双向同步设计](../LOCAL_SETUP.md#双向同步设计)

## 进入个人知识库

各平台保留原件。只有经过筛选、能追溯出处的材料才进入独立知识库。整理后的条目应能回答三个问题：原始内容在哪里、这次做了什么变换、谁确认可以收录。GitHub 仓库记录流程、代码和脱敏示例。
