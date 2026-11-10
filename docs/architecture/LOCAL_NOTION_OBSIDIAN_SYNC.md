# 本地 Notion → Obsidian 同步

本地脚本从 Notion 读取数据库内容，并写入指定 vault 的 `Thinking/`。可选的 GitHub Actions 镜像会把 Markdown 写入仓库的 `vault/`，供已选择公开的内容使用。

## 手动验证

1. 先按 [本地部署与验收](../LOCAL_SETUP.md) 准备 Python、测试数据库和独立 SQLite 目录。
2. 在 Obsidian 的 **Manage vaults** 查看目标 vault 的绝对路径。首次使用空白测试 vault。
3. 在仓库根目录运行。替换路径占位符，在本机配置 `NOTION_TOKEN` 和 `NOTION_THINKING_DATABASE_ID`。

```bash
export OBSIDIAN_VAULT="/path/to/test-vault"
export DATA_DIR="/path/to/test-sync-state"
bash scripts/sync-to-local-obsidian.sh
```

脚本从自身位置找到 checkout，可用 `RESEARCH_BRIEF_REPO` 覆盖。目标优先使用已设定的 `OBSIDIAN_VAULT` 或 `DEFAULT_VAULT_PATH`，也可在本机 `.env` 提供。日志在 macOS 默认写到 `~/Library/Logs/thinking-vault-sync.log`，Linux 默认写到 `~/.cache/thinking-vault-sync.log`，可用 `SYNC_LOG` 覆盖。退出码为 0 且日志含 `OK: Notion synced` 后，核对 `Thinking/` 的输出和第二次同步的结果。同步可能按 `source_id` 更新现有文件。

## 调度

按 [macOS 调度说明](MAC_SHORTCUTS_DAILY_SYNC.md) 选择快捷指令或 LaunchAgent。其他调度器可执行同一脚本。每个任务应明确解释器、checkout、vault、SQLite 目录和执行身份。对同一 vault 只启用一种调度方式。
