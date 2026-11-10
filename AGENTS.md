# Personal Knowledge Bridge

这个仓库提供可复用的个人知识库连接和校对工具。先读 [README](README.md) 与 [AI 部署入口](docs/ai/README.md)，选择要运行的链路，并核对它的配置、输入输出和验收条件。

- 平台职责、数据来源、当前实现状态 → [平台联动](docs/platforms/README.md)
- 运行环境、目录和配置项 → [部署环境](docs/deployment/README.md)
- 首次安装、`--check` 和同步验收 → [本地部署](docs/LOCAL_SETUP.md)
- 同步字段、处理顺序与发布模块 → [架构与现有模块](docs/architecture/README.md)

当前平台同步方向为 Notion → Obsidian。阅读摘录 OCR 是独立的本地校对工具。印象笔记 ENEX 接入和 Obsidian 写回 Notion 属于设计。以实际代码和测试判断能力，不从路线图推断运行状态。

Notion 同步首次部署用测试数据库、空白 vault 和独立 SQLite 索引。先运行 `--check`，再同步两次，核对正文、Context 链接和重复运行结果。OCR 首次部署用合成文本和仓库外临时目录，检查原文、草稿和重复运行计数。真实账户、目标目录、调度和外部模型由部署者提供或确认。

配置说明使用变量名和清楚标注的占位符。使用仓库相对路径定位代码，由部署者提供实际账号、数据库 ID、目录和任务标签。凭据、真实笔记、ENEX、附件、SQLite 和日志留在本机。使用合成样例验证；结论分开记录自动化测试、模拟 API 和真实平台实测。
