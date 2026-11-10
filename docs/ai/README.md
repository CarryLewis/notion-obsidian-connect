# AI 部署入口

先读 [AGENTS.md](../../AGENTS.md) 和 [平台状态](../platforms/README.md)。按用户目标选择一条链路，核对该链路的入口、依赖、输入、输出及权限，再开始安装或接入数据。

## 阅读摘录 OCR · 已实现

- **入口**：仓库根目录下的 `scripts/reading_ocr/ocr_audit.py`（单篇）和 `scripts/reading_ocr/ocr_batch.py`（批量）。使用 Python 3.12+，默认离线。
- **输入**：UTF-8 文本。批处理的 `--root` 指向仓库外的工作目录，读取 `inbox/*.txt`。可选 `rules.json`。
- **输出**：工作目录下的 `reports/` 和 `latest-summary.json`。报告保留原文、草稿和行列坐标。批处理标准输出只有计数。退出码 `0` 表示处理成功或无新文件，`1` 表示运行失败或存在失败文件，`2` 表示命令行参数错误。
- **验证**：按 [OCR 部署说明](../platforms/READING_OCR.md) 运行测试和合成样例。检查首次有处理结果，第二次跳过未修改文本。启用调度前，用同一运行身份手动执行一次。
- **外部服务**：语义模式需显式选择。模型建议保存在报告中。使用云模型会发送摘录正文，部署前确认数据允许发送。

## Notion → Obsidian · 已实现

- **入口**：[本地部署](../LOCAL_SETUP.md) 中的 `app.cli.thinking_sync`。先安装后端依赖。
- **输入**：拥有读取权限的测试数据库，以及本机配置的 `NOTION_TOKEN`、`NOTION_THINKING_DATABASE_ID`。由部署者填入真实值。
- **输出**：通过 `--vault` 指向空白测试 vault，通过 `DATA_DIR` 指定独立的 SQLite 目录。
- **验证**：先运行 `--check`，再同步两次，检查正文、Context 链接和第二次运行结果。部署日常任务时，另行选择目标、频率和运行身份。[运行环境与调度入口](../deployment/README.md)
- **发布**：GitHub Actions 镜像会将 `vault/` 提交到仓库。仅对明确选择公开的数据启用。

## 印象笔记导入和 Obsidian 写回 · 设计中

按 [平台状态](../platforms/README.md) 评估来源字段、附件和去重方式。用脱敏样例验证准备接入的数据。当前 OCR 入口接收已有的纯文本，完整 ENEX 导入和 Obsidian → Notion 写回需独立实现与验收。

## 交付记录

汇报所选链路、实际入口、配置字段名、数据去向和验收结果。分开记录代码测试、模拟 API、真实平台和定时触发。用占位符表示用户路径和标识。凭据、原文、完整报告及个人运行日志留在本机。
