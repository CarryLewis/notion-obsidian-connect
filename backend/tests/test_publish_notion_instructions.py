from __future__ import annotations

from app.services.thinking_vault.publish_instructions import (
    PAGE_TITLE,
    chunk_text,
    code_blocks,
    extract_fenced_blocks,
    instruction_page_blocks,
    load_instruction_docs,
)


def test_extract_fenced_blocks_keeps_order():
    md = "intro\n```text\nFIRST\n```\nmid\n```text\nSECOND\n```\n"
    assert extract_fenced_blocks(md) == ["FIRST", "SECOND"]


def test_chunk_text_respects_limit():
    assert chunk_text("abcdef", 3) == ["abc", "def"]
    assert chunk_text("") == [""]


def test_code_blocks_split_long_prompt():
    body = "x" * 4000
    blocks = code_blocks(body)
    assert len(blocks) == 3
    assert all(b["type"] == "code" for b in blocks)


def test_instruction_docs_load_from_repo():
    capture, context, minimal = load_instruction_docs()
    assert "单一归属" in capture
    assert "默认只写 1 个锚点" in capture or "默认 1 个" in capture
    assert "已有 Context 词表" in context
    assert "禁止一次覆盖多个板块" in context
    assert "默认只写 1 个已有锚点" in minimal


def test_instruction_page_blocks_include_both_prompts():
    blocks = instruction_page_blocks()
    types = [b["type"] for b in blocks]
    assert types.count("code") >= 2
    assert any(
        "Context 硬约束" in "".join(
            t.get("text", {}).get("content", "")
            for t in (b.get("callout") or {}).get("rich_text") or []
        )
        for b in blocks
        if b["type"] == "callout"
    )
    joined = json_text(blocks)
    assert PAGE_TITLE
    assert "Capture Rules" in joined
    assert "Patient language" in joined
    assert "Clinical reasoning" in joined


def json_text(blocks: list[dict]) -> str:
    parts: list[str] = []
    for block in blocks:
        payload = block.get(block["type"]) or {}
        for item in payload.get("rich_text") or []:
            parts.append(str(item.get("text", {}).get("content") or ""))
    return "\n".join(parts)
