"""CLI: publish Notion AI standing instructions to a Notion page.

Usage:
  python -m app.cli.publish_notion_instructions
"""

from __future__ import annotations

import argparse
import json
import sys

from ..config import get_settings
from ..services.thinking_vault.notion_client import NotionAPIError
from ..services.thinking_vault.publish_instructions import (
    WRITE_DENIED_HINT,
    publish_instruction_page,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Publish Thinking Vault Notion AI instructions to a Notion page"
    )
    args = parser.parse_args(argv)
    del args

    settings = get_settings()
    token = (settings.notion_token or "").strip()
    database_id = (settings.notion_thinking_database_id or "").strip()
    if not token:
        print("NOTION_TOKEN is not configured", file=sys.stderr)
        return 2
    if not database_id:
        print("NOTION_THINKING_DATABASE_ID is not configured", file=sys.stderr)
        return 2

    try:
        result = publish_instruction_page(token=token, database_id=database_id)
    except NotionAPIError as exc:
        denied = exc.status_code == 403 or "restricted_resource" in str(exc)
        payload = {
            "ok": False,
            "error": "restricted_resource" if denied else "notion_api_error",
            "message": str(exc),
            "hint": WRITE_DENIED_HINT if denied else "",
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 3 if denied else 1

    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
