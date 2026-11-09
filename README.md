# Personal Knowledge Bridge · 个人知识库联动

我用这个仓库记录 Notion、Obsidian 和印象笔记之间的内容怎么流动，以及这套工作流怎样在本机部署。这里放连接器、同步规则、运行环境和验收步骤。资料的原件留在各自的平台，需要沉淀的内容再经过整理，进入独立的个人知识库。

## 各平台的职责

- **Notion** 用于捕捉和整理思考。Thinking Vault 中的属性和正文是同步笔记的编辑来源。
- **Obsidian** 用于本地 Markdown 阅读、链接和图谱探索。当前可运行的链路是 **Notion → Obsidian**。
- **印象笔记** 保存历史笔记与剪藏。先从少量 ENEX 导出开始，核对内容、附件和来源，再决定哪些材料值得迁入知识库。这条接入路径仍在设计。

[平台联动、数据边界与接入状态](docs/platforms/README.md)

## 从哪里开始

1. **部署与复现**。从 [部署环境](docs/deployment/README.md) 了解 macOS、Python、本地 vault 和 SQLite 的角色，再按 [本地部署与验收](docs/LOCAL_SETUP.md) 跑一个隔离样例。
2. **交给 AI**。让 AI 先读 [AGENTS.md](AGENTS.md)，再按 [AI 阅读入口](docs/ai/README.md) 选择部署、故障排查或平台接入任务。
3. **查看实现**。从 [架构与现有模块](docs/architecture/README.md) 找到同步字段、Markdown 生成、可选的镜像与网站发布。

## 仓库分区

- `docs/platforms/` 记录平台职责、数据方向和各链路的实现状态。
- `docs/deployment/` 记录机器环境、部署方式、配置项和验证结果。
- `docs/ai/` 提供给编程 AI 的任务入口和验收口径。
- `docs/architecture/` 记录数据契约、模块关系及原 Research Brief Studio 的运行入口。
- `backend/`、`scripts/` 和 `.github/workflows/` 存放同步实现、本地脚本和 GitHub 工作流。`extension/`、`jobs/`、`site/` 保留原有的采集和发布能力，`vault/` 是仓库中的镜像目录。

这个仓库是公开的。本地部署时，请把私人 vault、印象笔记原始导出、凭据和同步索引留在仓库外或 Git 忽略目录中。GitHub Actions 镜像会提交 Markdown 到 `vault/`，适用于明确选择公开的内容。
