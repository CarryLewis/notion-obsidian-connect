# 在本机部署 Notion → Obsidian

这条流程把 Notion 数据库属性和页面正文导出到本地 Obsidian vault。Notion 是同步笔记的编辑入口。同步程序用 Notion 页面 ID（Markdown frontmatter 里的 `source_id`）识别同一条笔记，标题变化时更新文件名。Obsidian 中对同步文件的修改不会写回 Notion，后续同步可能覆盖这些修改。

以下命令适用于 macOS 和 Linux 的 Bash 或 Zsh，需要 Git 和 Python 3.12（仓库 Actions 使用的版本）。Obsidian 用来核对笔记和图谱。首轮使用独立的测试数据库、vault 和 SQLite 索引。

## 1. 获取代码和安装依赖

```bash
git clone https://github.com/CarryLewis/notion-obsidian-connect.git
cd notion-obsidian-connect
python3.12 --version
python3.12 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python -m pip check
if [ ! -e .env ]; then (umask 077; cp .env.example .env); fi
git check-ignore .env
```

`pip check` 应成功，最后一行应显示 `.env`。如果目录已有 checkout，从它的仓库根目录开始。安装失败时保留原报错，先修 Python 版本或依赖安装，再继续。

## 2. 创建专用 Notion 测试库

1. 新建一个只有一个数据源的完整页面数据库，例如 **Thinking Sync Test**。创建这些最小属性，属性名称用下列英文原名。
   - `Name` → Title
   - `Raw Thought` → Text
   - `Context` → Text
2. 建一条测试记录。标题填 `Sync Smoke Test`，Raw Thought 填 `Original sample sentence.`，Context 填 `Clinical communication`。在这条记录的页面正文写 `This is the sample reflection.`。
3. 由工作区所有者创建 [Notion internal integration](https://developers.notion.com/guides/authorization/overview#internal-connection-auth-flow-set-up)，启用 **Read content**。在源数据库页面的菜单里打开 **Connections**，添加该 integration。
4. 在本机编辑仓库根目录下的 `.env`，填写 `NOTION_TOKEN` 和 `NOTION_THINKING_DATABASE_ID`。数据库 ID 是源数据库链接路径中的 32 位十六进制 ID，可带连字符。链接里 `?v=` 后面是视图 ID。当前客户端使用 Notion API `2022-06-28` 的 database query，部署使用单数据源数据库。[Notion 数据源版本说明](https://developers.notion.com/docs/upgrade-guide-2025-09-03)
5. 在终端以外的本地编辑器填写 token。保留 `.env` 在本机，运行下列步骤时无需在聊天、命令参数或 GitHub Secrets 中提交它。若配置了同名环境变量，进程环境会优先于 `.env`，请确认终端使用的是测试库配置。

使用更多字段时，见 [Notion 数据库字段清单](architecture/NOTION_THINKING_DATABASE_CHECKLIST.md)。测试库只需要上面三个属性。

## 3. 在空白 vault 运行检查和首次同步

从仓库根目录执行，并在同一个终端保留 `TEST_VAULT` 和 `DATA_DIR`。

```bash
TEST_VAULT="$(mktemp -d "$HOME/notion-obsidian-test.XXXXXX")"
export DATA_DIR="$(mktemp -d "${TMPDIR:-/tmp}/notion-obsidian-index.XXXXXX")"
printf 'Test vault: %s\n' "$TEST_VAULT"
cd backend
../.venv/bin/python -m app.cli.thinking_sync --check --vault "$TEST_VAULT"
```

检查成功时，输出中的 `vault_directory`、`notion_query`、`sample_properties` 和 `sample_body_access` 都是 `ok`。`--check` 只读一条 Notion 记录并试读该记录的正文块，检查目标目录存在且当前进程有访问权限。它不生成 Markdown、不更新 SQLite 同步索引。完整同步还需要读取库中的其余记录。

检查成功后，在同一个终端执行两次：

```bash
../.venv/bin/python -m app.cli.thinking_sync --vault "$TEST_VAULT" --no-archive-missing
../.venv/bin/python -m app.cli.thinking_sync --vault "$TEST_VAULT" --no-archive-missing
```

- 首次运行应有 `created: 1` 和 `errors: []`。查看 `$TEST_VAULT/Thinking/Sync Smoke Test.md`，应包含 `source_id`、原始句子、`[[Clinical communication]]` 和 `Extended Reflection` 下的样例正文。如果没有生成 Markdown、命令报错或日志显示正文读取失败，先停在测试 vault。
- 第二次运行应有 `unchanged: 1`、`created: 0`、`updated: 0` 和 `errors: []`。
- 在 Obsidian 里用 **Open folder as vault** 打开测试目录，核对正文和 Context 链接。若图谱只显示已有文件，先在测试 vault 里创建同名笔记，或关闭图谱的 **Existing files only**，再确认连接。[Obsidian 图谱帮助](https://obsidian.md/help/plugins/graph)

## 4. 切换到自己的库

先备份目标 vault，再将 `.env` 切换到自己的数据库。在 Obsidian 的 vault 管理中确认实际路径。为每组数据库和 vault 使用独立的 `DATA_DIR`，同一组之后一直使用它，例如 `./data/my-thinking`（相对于仓库根目录）。在 `backend/` 中执行，先把示例路径换成实际 vault 路径：

```bash
REAL_VAULT='/absolute/path/to/your/vault'
export DATA_DIR=./data/my-thinking
../.venv/bin/python -m app.cli.thinking_sync --check --vault "$REAL_VAULT"
```

检查通过后执行：

```bash
../.venv/bin/python -m app.cli.thinking_sync --vault "$REAL_VAULT" --no-archive-missing
```

`--no-archive-missing` 会跳过缺失条目的软归档，仍会创建、更新或重命名对应的笔记。去掉它后，未出现在 Notion 查询结果里的已跟踪笔记可能移到 `Archive/Thinking/`。同步管理的笔记以 Notion 为准，独立的 Obsidian 草稿可放在另一个目录。

本地部署无需启用 GitHub Actions、Quartz、后端服务或 LLM 密钥。仓库的定时 Actions 会提交生成的 `vault/` 内容，适合有意使用该发布流程的场景。私人笔记使用仓库外的目标路径，保持生成的 Markdown 和同步日志留在本机。

## 常见失败

- **找不到 Python 或模块**：确认当前在仓库的 `backend/`，调用的是 `../.venv/bin/python`，并已在同一环境安装依赖。
- **HTTP 401**：检查本机 `NOTION_TOKEN` 是否有效，确认终端没有覆盖 `.env` 的旧值。
- **HTTP 403 或 404**：检查 integration 的 Read content 权限和源数据库 Connections。核对用的是数据库 ID，不是视图、普通页面或数据源 ID。
- **HTTP 400**：核对数据库 ID 和单数据源条件。遇到多数据源错误时，先用独立的单数据源测试数据库复现。
- **属性缺失或类型不符**：按错误输出核对数据库属性，或者检查 `backend/configs/workspace.yaml` 的名称映射。
- **路径或网络错误**：确认 vault 目录存在且当前进程可写。遇到超时、TLS 或连接错误时检查网络和终端代理，修复后重跑 `--check`。

## 图谱链接从哪里来

`Context` 写纯文本锚点，多个用中文分号分开。只有确实想在图谱里反复回到的概念才放在这里。确认要关联某条已有记录时，使用 `Related Information` 的 Notion Relation。同步器分别把它们渲染为 Context 和 Connections 的双链。正文里提到「临床沟通」时用普通文字或加粗。手写 `[[临床沟通]]` 会被 Obsidian 当成链接。让 Notion AI 在保存前清掉它新增的装饰性双链，保留用户原话、代码示例和有意保留的链接。

## 双向同步设计

现有 CLI 负责 Notion → Obsidian。未来如果支持从 Obsidian 写回，第一步可限定为用户显式提交某个现有笔记的一段可编辑内容。保留 `source_id`，记录上次成功同步的基准内容和版本，分别比较 Notion 与本地 Markdown 的变化。若只有本地改动，先生成字段级预览，经确认后写回。若同一字段两端都改了，保留两份并交给用户解决。删除、重命名、重新运行和部分失败要单独验证。上线前用测试库验收双端改动、重复提交和回滚，并把写入授权与目前的只读集成分开。

## 可以直接交给部署 AI 的指令

> 在我的电脑上按本页第 1–3 节部署。每一步完成后核对预期结果，失败时先定位并修复该步。需要我创建数据库、连接 integration 或填 token 时，指出操作位置，让我在 Notion 或本机编辑器里完成。使用独立测试库、vault 和索引，保持凭据、日志与生成的笔记在本机。首次同步前必须通过 `--check`；同步两次并核对样例 Markdown、正文与链接。报告使用的 Python 版本、测试 vault 路径、两次同步计数和仍待确认的项目。在我指定真实库和 vault 之前，停在已验收的测试环境。
