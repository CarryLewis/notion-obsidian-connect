"""CLI: Thinking Vault Notion → Obsidian sync.

Usage:
  python -m app.cli.thinking_sync
  python -m app.cli.thinking_sync --vault /path/to/vault
  python -m app.cli.thinking_sync --check --vault /path/to/vault
  python -m app.cli.thinking_sync --status
  python -m app.cli.thinking_sync --no-archive-missing
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ..config import get_settings
from ..db import SessionLocal, init_db
from ..services import thinking_vault as thinking_vault_svc
from ..services.thinking_vault.normalizer import property_names
from ..services.thinking_vault.writer import thinking_vault_cfg
from ..utils import workspace_config_dict


def check_setup(vault: str, token: str, database_id: str) -> int:
    """Check the local target and read one sample without writing notes or SQLite."""
    target = Path(vault).expanduser()
    if not target.is_dir() or not os.access(target, os.W_OK | os.X_OK):
        print("Vault must be an existing, writable directory.", file=sys.stderr)
        return 2

    names = property_names(thinking_vault_cfg(workspace_config_dict()))
    required = {
        names["title"]: "title",
        names["raw_thought"]: "rich_text",
        names["context"]: "rich_text",
    }
    try:
        with thinking_vault_svc.NotionClient(token) as notion:
            sample = notion.query_database(database_id, page_size=1).get("results") or []
            if not sample or not sample[0].get("id"):
                print(
                    "Create a sample page in the connected Notion database, then retry.",
                    file=sys.stderr,
                )
                return 1
            props = sample[0].get("properties") or {}
            mismatches = [
                f"{name} ({kind})"
                for name, kind in required.items()
                if (props.get(name) or {}).get("type") != kind
            ]
            if mismatches:
                print(
                    f"Missing or mismatched Notion properties: {', '.join(mismatches)}",
                    file=sys.stderr,
                )
                return 1
            notion.list_block_children(sample[0]["id"], page_size=1)
    except thinking_vault_svc.NotionAPIError as exc:
        detail = f"HTTP {exc.status_code}" if exc.status_code else "network request failed"
        print(f"Notion setup check failed ({detail}). See docs/LOCAL_SETUP.md.", file=sys.stderr)
        return 1

    print(json.dumps({
        "vault_directory": "ok",
        "notion_query": "ok",
        "sample_properties": "ok",
        "sample_body_access": "ok",
    }))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sync Notion Thinking Database → Obsidian Thinking/"
    )
    parser.add_argument("--vault", default="", help="Obsidian vault path")
    parser.add_argument(
        "--no-archive-missing",
        action="store_true",
        help="Do not soft-archive Obsidian notes missing from Notion",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--status",
        action="store_true",
        help="Print sync index status and exit",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Check the vault and Notion sample access without syncing",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    if not args.status:
        vault = (args.vault or settings.default_vault_path or "").strip()
        if not vault:
            print("vault path required (--vault or DEFAULT_VAULT_PATH)", file=sys.stderr)
            return 2
        token = (settings.notion_token or "").strip()
        database_id = (settings.notion_thinking_database_id or "").strip()
        if not token:
            print("NOTION_TOKEN is not configured", file=sys.stderr)
            return 2
        if not database_id:
            print("NOTION_THINKING_DATABASE_ID is not configured", file=sys.stderr)
            return 2
        if args.check:
            return check_setup(vault, token, database_id)

    init_db()
    db = SessionLocal()
    try:
        if args.status:
            print(json.dumps(thinking_vault_svc.last_sync_status(db), ensure_ascii=False, indent=2))
            return 0
        result = thinking_vault_svc.sync_from_notion(
            db,
            vault_path=vault,
            token=token,
            database_id=database_id,
            soft_archive_missing=not args.no_archive_missing,
        )
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 1 if result.errors else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
