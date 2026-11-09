# Personal Knowledge Bridge

这个仓库维护个人知识库的跨平台连接、部署说明和可复现的验收流程。先阅读 [README](README.md)，按任务选择入口。

- 平台职责、数据来源、当前实现状态 → [平台联动](docs/platforms/README.md)
- 本机硬件与软件、目录、配置项 → [部署环境](docs/deployment/README.md)
- 首次安装、`--check` 和同步验收 → [本地部署](docs/LOCAL_SETUP.md)
- 同步字段、处理顺序与发布模块 → [架构与现有模块](docs/architecture/README.md)

当前同步方向为 Notion → Obsidian。印象笔记 ENEX 接入和 Obsidian 写回 Notion 属于设计。以实际代码和测试判断能力，不从路线图推断运行状态。

首次部署用独立的测试数据库、空白 vault 和 SQLite 索引。先运行 `--check`，再同步两次，核对正文、Context 链接和重复运行结果。涉及实际账户、数据库或 vault 时，先确认用户指定的目标和数据方向。

配置说明只记录字段名和示例值。凭据、真实笔记、ENEX、附件、SQLite 和日志留在本机。使用合成样例验证；结论分开记录自动化测试、模拟 API 和真实平台实测。
