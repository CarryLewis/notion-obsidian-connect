# 部署环境

## 当前参考环境

- **主机**：Apple Silicon（arm64），macOS 26.3。检查时本机安装了 Notion、Obsidian 和印象笔记客户端。
- **同步运行时**：Python 3.12。已用独立的 Python 3.12.12 环境安装仓库依赖并运行后端测试。
- **数据位置**：Notion 是 Thinking 数据库来源。同步将 Markdown 写到显式指定的本地 Obsidian vault，SQLite 索引由 `DATA_DIR` 指定。使用 iCloud vault 时，从 Obsidian 确认目录已经下载且可写。印象笔记 ENEX 原件单独存放。
- **可选入口**：本地命令为首轮验收入口。macOS 快捷指令、LaunchAgent 和 GitHub Actions 分别有独立说明，启用前先确认目标路径、运行身份和是否会把笔记写进 Git 仓库。

这是部署参考和已核对的环境信息。真实工作区的授权、正在使用的调度入口和 Obsidian 图谱显示，需要在实际部署时单独核对。

## 首次部署顺序

按 [本地部署与验收](../LOCAL_SETUP.md) 安装环境、创建测试数据库、检查连接、同步两次。把测试目录与日常 vault 分开，验收后再切到指定的真实数据库和 vault。遇到环境问题，先检查本机架构、Python 版本、目标目录的可写性和可用空间，再看网络与 Notion 权限。当前流程用 Python、磁盘和网络，基础同步无需 GPU。

## 配置从哪里读

- `NOTION_TOKEN` 与 `NOTION_THINKING_DATABASE_ID` 通过仓库根目录 `.env` 或进程环境提供，同名进程变量优先。[配置样例](../../.env.example)
- `--vault` 显式指定输出位置，省略时读取 `DEFAULT_VAULT_PATH`。将数据库、vault 和 SQLite 索引作为一组管理，为每组设置独立的 `DATA_DIR`。
- 属性映射与 `Thinking/`、`Archive/Thinking/` 目录约定见 [workspace.yaml](../../backend/configs/workspace.yaml)。
- [macOS 调度说明](../architecture/MAC_SHORTCUTS_DAILY_SYNC.md) · [本地脚本说明](../architecture/LOCAL_NOTION_OBSIDIAN_SYNC.md) · [可选 GitHub Actions 镜像](../../.github/workflows/thinking-sync.yml)
