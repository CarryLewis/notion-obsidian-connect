# 在 macOS 定时同步 Notion → Obsidian

先按 [本地同步说明](LOCAL_NOTION_OBSIDIAN_SYNC.md) 用隔离的测试库、vault 和索引完成一次手动同步，再选择一种调度方式。下文的 06:00 是每日调度的示例时间。

## Apple 快捷指令

1. 新建快捷指令，添加「运行 Shell 脚本」，选择 `/bin/bash`。将以下路径换成当前部署的绝对路径。
2. 先在编辑页手动执行一次，确认写入指定的 vault。按需要授予访问选定目录的权限。
3. 添加「一天中的时间」自动化并选择要执行的快捷指令，按需要设置时间、频率和运行方式。触发一次后检查日志和输出目录。

```bash
export OBSIDIAN_VAULT="/path/to/selected-vault"
export DATA_DIR="/path/to/sync-state"
exec /bin/bash "/path/to/checkout/scripts/macos/run-thinking-sync.command"
```

## LaunchAgent

从当前 checkout 的根目录运行以下命令，把变量中的占位符换成已核对的绝对路径。示例使用每日模板。可修改副本里的 `StartCalendarInterval`，或选择同目录的 15 分钟模板。每个任务使用唯一的 `Label`。如果已有同步到同一 vault 的旧任务，先核对其本机标签并暂停，避免重复写入。

```bash
repo_dir="$(pwd -P)"
vault_dir="/path/to/selected-vault"
state_dir="/path/to/sync-state"
label="io.personal-knowledge-bridge.thinking-sync-daily"
plist="$HOME/Library/LaunchAgents/$label.plist"

mkdir -p "$HOME/Library/LaunchAgents"
cp -n "$repo_dir/scripts/macos/$label.plist.example" "$plist"
plutil -replace ProgramArguments.1 -string "$repo_dir/scripts/sync-to-local-obsidian.sh" "$plist"
plutil -replace EnvironmentVariables.OBSIDIAN_VAULT -string "$vault_dir" "$plist"
plutil -replace EnvironmentVariables.DATA_DIR -string "$state_dir" "$plist"
plutil -lint "$plist"
launchctl bootstrap "gui/$(id -u)" "$plist"
launchctl kickstart "gui/$(id -u)/$label"
```

命令适用于首次安装。更新已有任务时，先确认当前标签与 plist 路径对应，再用 `launchctl bootout "gui/$(id -u)/$label"` 停止并重新加载。使用诊断脚本检查任务和退出状态，可用 `THINKING_LAUNCHAGENT_LABEL` 指定标签。日志留在本机。

```bash
THINKING_LAUNCHAGENT_LABEL="$label" OBSIDIAN_VAULT="$vault_dir" \
  bash scripts/macos/check-local-sync.sh
```

手动触发成功后，验证一次实际定时触发，并记录时间、运行身份和退出码。暂停时关闭对应的快捷指令自动化，或对对应 LaunchAgent 执行 `bootout`。
