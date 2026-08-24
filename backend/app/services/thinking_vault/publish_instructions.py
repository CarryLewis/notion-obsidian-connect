"""Publish Notion AI standing instructions to a workspace page (not the Thinking DB).

Creates or updates a sibling page of the Thinking database so the text can be
@-mentioned in Notion AI without becoming a synced Thinking note.
"""

from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Any

import httpx

from ...config import PROJECT_ROOT
from .notion_client import NOTION_API_BASE, NOTION_VERSION, NotionAPIError

logger = logging.getLogger(__name__)

PAGE_TITLE = "Thinking Vault — Notion AI Instructions"
RICH_TEXT_LIMIT = 1900
CHILDREN_PER_REQUEST = 100
DELETE_PAUSE_SEC = 0.35

CAPTURE_RULES_REL = Path("docs/architecture/NOTION_AI_THINKING_CAPTURE_RULES_PROMPT.md")
CONTEXT_RULES_REL = Path("docs/architecture/NOTION_AI_CONTEXT_WIKILINK_PROMPT.md")


def extract_fenced_blocks(markdown: str, language: str = "text") -> list[str]:
    """Return fenced code blocks of a given language, in order."""
    pattern = rf"```{re.escape(language)}\s*\n(.*?)```"
    return [m.group(1).strip("\n") for m in re.finditer(pattern, markdown, re.S)]


def chunk_text(text: str, limit: int = RICH_TEXT_LIMIT) -> list[str]:
    raw = text or ""
    if not raw:
        return [""]
    return [raw[i : i + limit] for i in range(0, len(raw), limit)]


def _rich(text: str, *, bold: bool = False) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    for chunk in chunk_text(text):
        item: dict[str, Any] = {"type": "text", "text": {"content": chunk}}
        if bold:
            item["annotations"] = {"bold": True}
        parts.append(item)
    return parts


def _block(block_type: str, **payload: Any) -> dict[str, Any]:
    return {"object": "block", "type": block_type, block_type: payload}


def code_blocks(text: str, language: str = "plain text") -> list[dict[str, Any]]:
    """Notion code blocks cap rich_text at ~2000 chars; split if needed."""
    body = text or ""
    if not body:
        return [_block("code", rich_text=_rich(""), language=language)]
    out: list[dict[str, Any]] = []
    for chunk in chunk_text(body):
        out.append(_block("code", rich_text=_rich(chunk), language=language))
    return out


def paragraph(text: str) -> dict[str, Any]:
    return _block("paragraph", rich_text=_rich(text))


def heading(text: str, level: int = 2) -> dict[str, Any]:
    key = {1: "heading_1", 2: "heading_2", 3: "heading_3"}.get(level, "heading_2")
    return _block(key, rich_text=_rich(text))


def bulleted(text: str) -> dict[str, Any]:
    return _block("bulleted_list_item", rich_text=_rich(text))


def callout(text: str, emoji: str = "📌") -> dict[str, Any]:
    return _block(
        "callout",
        rich_text=_rich(text),
        icon={"type": "emoji", "emoji": emoji},
    )


def divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def load_instruction_docs(repo_root: Path | None = None) -> tuple[str, str, str]:
    root = repo_root or PROJECT_ROOT
    capture_md = (root / CAPTURE_RULES_REL).read_text(encoding="utf-8")
    context_md = (root / CONTEXT_RULES_REL).read_text(encoding="utf-8")
    capture_blocks = extract_fenced_blocks(capture_md)
    context_blocks = extract_fenced_blocks(context_md)
    if not capture_blocks:
        raise FileNotFoundError(f"No ```text prompt in {CAPTURE_RULES_REL}")
    if not context_blocks:
        raise FileNotFoundError(f"No ```text prompt in {CONTEXT_RULES_REL}")
    capture_prompt = max(capture_blocks, key=len)
    context_prompt = max(context_blocks, key=len)
    context_minimal = ""
    for block in context_blocks:
        if block != context_prompt and "Context 硬约束" in block:
            context_minimal = block
            break
    if not context_minimal:
        extras = [b for b in context_blocks if b != context_prompt]
        context_minimal = extras[-1] if extras else ""
    return capture_prompt, context_prompt, context_minimal


def instruction_page_blocks(repo_root: Path | None = None) -> list[dict[str, Any]]:
    capture_prompt, context_prompt, context_minimal = load_instruction_docs(repo_root)
    blocks: list[dict[str, Any]] = [
        callout(
            "把下面两段 Prompt 复制进 Notion AI custom instructions（或在 Thinking 对话里 @ 本页）。"
            "Context 硬约束：默认 1 个已有锚点，最多 2 个；禁止一次覆盖多个板块。"
        ),
        paragraph(
            "本页由仓库 docs/architecture/NOTION_AI_*_PROMPT.md 发布，不是 Thinking 数据库条目，不会同步进 Obsidian。"
        ),
        heading("How to use", 2),
        bulleted("打开 Notion AI custom instructions / standing instructions"),
        bulleted("粘贴「Capture Rules」整段，再粘贴「Context 专项」整段"),
        bulleted("之后每次捕捉时，Context 只从已有词表选 1 个锚点（例外才 2 个）"),
        divider(),
        heading("Capture Rules（standing instructions）", 2),
        paragraph("从这里复制到 Notion AI："),
        *code_blocks(capture_prompt),
        divider(),
        heading("Context 专项（必须一起粘贴）", 2),
        paragraph("Context 不是目录。一条思考默认只挂一个已有锚点。"),
        *code_blocks(context_prompt),
    ]
    if context_minimal:
        blocks.extend(
            [
                heading("Minimal Context add-on", 3),
                *code_blocks(context_minimal),
            ]
        )
    return blocks


def _normalize_id(value: str) -> str:
    raw = (value or "").strip().replace("-", "")
    if len(raw) == 32 and all(c in "0123456789abcdefABCDEF" for c in raw):
        return f"{raw[0:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:32]}"
    return (value or "").strip()


def page_url(page_id: str) -> str:
    return f"https://www.notion.so/{_normalize_id(page_id).replace('-', '')}"


def _title_plain(page: dict[str, Any]) -> str:
    props = page.get("properties") or {}
    for value in props.values():
        if not isinstance(value, dict) or value.get("type") != "title":
            continue
        parts = []
        for item in value.get("title") or []:
            if isinstance(item, dict) and item.get("plain_text"):
                parts.append(str(item["plain_text"]))
        return "".join(parts).strip()
    return ""


class NotionInstructionPublisher:
    """Write-capable helper on top of the read-only Thinking Vault client."""

    def __init__(self, token: str, *, timeout: float = 45.0) -> None:
        if not (token or "").strip():
            raise NotionAPIError("NOTION_TOKEN is empty")
        self.token = token.strip(        )
        self._client = httpx.Client(
            base_url=NOTION_API_BASE,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> NotionInstructionPublisher:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        resp = self._client.request(method, path, **kwargs)
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except Exception:  # noqa: BLE001
                body = resp.text
            raise NotionAPIError(
                f"Notion API {resp.status_code} for {method} {path}",
                status_code=resp.status_code,
                body=body,
            )
        if not resp.content:
            return {}
        return resp.json()

    def retrieve_database(self, database_id: str) -> dict[str, Any]:
        return self._request("GET", f"/databases/{_normalize_id(database_id)}")

    def search_pages(self, query: str) -> list[dict[str, Any]]:
        data = self._request(
            "POST",
            "/search",
            json={
                "query": query,
                "filter": {"value": "page", "property": "object"},
                "page_size": 20,
            },
        )
        return list(data.get("results") or [])

    def find_instruction_page(self) -> dict[str, Any] | None:
        for page in self.search_pages(PAGE_TITLE):
            if _title_plain(page) == PAGE_TITLE:
                return page
        return None

    def create_page(self, parent: dict[str, Any], children: list[dict[str, Any]]) -> dict[str, Any]:
        first, rest = children[:CHILDREN_PER_REQUEST], children[CHILDREN_PER_REQUEST:]
        created = self._request(
            "POST",
            "/pages",
            json={
                "parent": parent,
                "properties": {
                    "title": {
                        "title": [{"type": "text", "text": {"content": PAGE_TITLE}}]
                    }
                },
                "children": first,
            },
        )
        page_id = str(created.get("id") or "")
        if rest and page_id:
            self.append_children(page_id, rest)
        return created

    def append_children(self, block_id: str, children: list[dict[str, Any]]) -> None:
        bid = _normalize_id(block_id)
        for i in range(0, len(children), CHILDREN_PER_REQUEST):
            batch = children[i : i + CHILDREN_PER_REQUEST]
            self._request("PATCH", f"/blocks/{bid}/children", json={"children": batch})

    def iter_direct_children(self, block_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        cursor: str | None = None
        while True:
            params: dict[str, Any] = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            data = self._request(
                "GET",
                f"/blocks/{_normalize_id(block_id)}/children",
                params=params,
            )
            results.extend(data.get("results") or [])
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
            if not cursor:
                break
        return results

    def replace_children(self, page_id: str, children: list[dict[str, Any]]) -> None:
        existing = self.iter_direct_children(page_id)
        for block in existing:
            bid = str(block.get("id") or "")
            if not bid:
                continue
            self._request("DELETE", f"/blocks/{_normalize_id(bid)}")
            time.sleep(DELETE_PAUSE_SEC)
        self.append_children(page_id, children)

    def parent_for_sibling_of_database(self, database_id: str) -> dict[str, Any]:
        db = self.retrieve_database(database_id)
        parent = db.get("parent") or {}
        ptype = parent.get("type")
        if ptype == "page_id" and parent.get("page_id"):
            return {"type": "page_id", "page_id": parent["page_id"]}
        if ptype == "block_id" and parent.get("block_id"):
            return {"type": "page_id", "page_id": parent["block_id"]}
        if ptype == "workspace":
            return {"type": "workspace", "workspace": True}
        # Last resort: create under the database's wrapping page id.
        db_id = str(db.get("id") or database_id)
        return {"type": "page_id", "page_id": _normalize_id(db_id)}


def publish_instruction_page(
    *,
    token: str,
    database_id: str,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Create or update the standing-instructions page. Returns id/url/action."""
    blocks = instruction_page_blocks(repo_root)
    with NotionInstructionPublisher(token) as publisher:
        existing = publisher.find_instruction_page()
        if existing and existing.get("id"):
            page_id = str(existing["id"])
            publisher.replace_children(page_id, blocks)
            action = "updated"
        else:
            parent = publisher.parent_for_sibling_of_database(database_id)
            created = publisher.create_page(parent, blocks)
            page_id = str(created.get("id") or "")
            action = "created"
        url = page_url(page_id)
        logger.info("Notion AI instructions page %s: %s", action, url)
        return {
            "action": action,
            "page_id": page_id,
            "url": url,
            "title": PAGE_TITLE,
            "block_count": len(blocks),
        }
