from __future__ import annotations

import json

import httpx
import pytest

from app.cli import thinking_sync
from app.config import Settings
from app.services.thinking_vault import NotionClient

DATABASE_ID = "12345678-1234-1234-1234-123456789abc"
PAGE_ID = "23456789-1234-1234-1234-123456789abc"


@pytest.mark.parametrize(
    ("context_type", "block_status", "expected_exit", "expected_error"),
    [
        ("rich_text", 200, 0, ""),
        ("select", 200, 1, "Context (rich_text)"),
        ("rich_text", 403, 1, "HTTP 403"),
    ],
)
def test_check_validates_notion_without_writing(
    tmp_path, monkeypatch, capsys, context_type, block_status, expected_exit, expected_error
):
    calls = []
    settings = Settings(
        _env_file=None, notion_token="fake-test-token", notion_thinking_database_id=DATABASE_ID
    )
    monkeypatch.setattr(thinking_sync, "get_settings", lambda: settings)
    monkeypatch.setattr(thinking_sync, "init_db", lambda: pytest.fail("Check opened the sync index"))

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, request.url.path))
        if request.url.path == f"/v1/databases/{DATABASE_ID}/query":
            assert json.loads(request.content) == {"page_size": 1}
            return httpx.Response(
                200,
                json={
                    "results": [{
                        "id": PAGE_ID,
                        "properties": {
                            "Name": {"type": "title"},
                            "Raw Thought": {"type": "rich_text"},
                            "Context": {"type": context_type},
                        },
                    }],
                },
            )
        assert request.url.path == f"/v1/blocks/{PAGE_ID}/children"
        assert request.url.params["page_size"] == "1"
        return httpx.Response(block_status, json={"results": []})

    with httpx.Client(
        base_url="https://api.notion.com/v1", transport=httpx.MockTransport(handler)
    ) as client:
        monkeypatch.setattr(
            thinking_sync.thinking_vault_svc, "NotionClient",
            lambda token: NotionClient(token, client=client),
        )
        assert thinking_sync.main(["--check", "--vault", str(tmp_path)]) == expected_exit

    assert calls[0] == ("POST", f"/v1/databases/{DATABASE_ID}/query")
    assert len(calls) == (1 if context_type == "select" else 2)
    assert list(tmp_path.iterdir()) == []
    captured = capsys.readouterr()
    if expected_error:
        assert expected_error in captured.err
        assert not captured.out
    else:
        assert set(json.loads(captured.out).values()) == {"ok"}
