# 架构与现有模块

- [Thinking Vault 同步架构](THINKING_VAULT_ARCHITECTURE.md) 和 [字段清单](NOTION_THINKING_DATABASE_CHECKLIST.md) 说明 Notion 数据怎么变成本地 Markdown。
- [Obsidian 库约定](OBSIDIAN_CONSTITUTION_V1_1.md) 说明本地知识目录和链接的组织方式。
- [Research Brief Studio 原有架构](../ARCHITECTURE.md) 与 [产品说明](../PRODUCT_v1.md) 记录采集、存储、图谱和研究简报模块。下面保留这些模块的运行入口。

## Optional GitHub Actions mirror

GitHub Actions can mirror Notion → the repository vault (hourly + manual). Use this path only when the synced content is intended for the repository and any connected site.

1. Repo Settings → Secrets and variables → Actions → add:
   - `NOTION_TOKEN`
   - `NOTION_THINKING_DATABASE_ID`
2. Workflow: [`.github/workflows/thinking-sync.yml`](../../.github/workflows/thinking-sync.yml)
3. Writes into the repo’s [`vault/`](../../vault/) and commits when notes change.
4. Actions → **Thinking Vault Sync** → Run workflow (optional manual trigger).

SQLite sync index is cached across runs; if the cache is cold, sync hydrates identity from on-disk `source_id` / `.thinking-folder` sidecars.

## Public website (Quartz + Cloudflare)

Publish the Obsidian-style garden from `vault/` with Quartz:

- Code: [`site/`](../../site/)
- Guide: [`docs/architecture/QUARTZ_CLOUDFLARE_DEPLOY.md`](QUARTZ_CLOUDFLARE_DEPLOY.md)
- Connect the repo to **Cloudflare Pages** (root directory `site`, build `npm ci && npm run build`, output `public`), then bind your existing domain.

AI proposes relationships; humans accept meaningful links. No Inbox dump. No domain folder taxonomy.

## Optional Research Brief Studio commands

```bash
cd backend && source .venv/bin/activate

# Capture → Lake + KO; Library/save writes Information/ notes
python -m app.cli.collect --job ../jobs/nature_migraine.yaml --no-media

# Lifecycle (backend; not daily vault bureaucracy)
python -m app.cli.lifecycle backfill
python -m app.cli.lifecycle evaluate --notebook nb_xxx
python -m app.cli.lifecycle proposals

# Workspace sync → Thinking / Research cognitive folders
python -m app.cli.workspace sync --notebook nb_xxx --vault ../vault

# Cognitive graph (portable JSON — propose-only AI links)
python -m app.cli.graph sync --notebook nb_xxx
python -m app.cli.graph view --view research --notebook nb_xxx --fresh
python -m app.cli.graph neighborhood --ko ko_xxx --depth 2
python -m app.cli.graph metrics --notebook nb_xxx
python -m app.cli.graph suggest-links --notebook nb_xxx

# API
python -m uvicorn app.main:app --reload --port 8000
```

### Vault layout (Constitution V1.1)

```text
Information/            # world memory (readable captures)
Thinking/               # Notion-synced + personal fragments
Research/               # synthesis / briefs
Archive/                # cold legacy + Digests
90_Meta/
```
