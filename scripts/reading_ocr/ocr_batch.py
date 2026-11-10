#!/usr/bin/env python3
"""Audit new or changed text excerpts and print only aggregate counts."""
from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import json
import os
import stat
import sys
from collections import Counter
from pathlib import Path

from ocr_audit import audit, load_rules, model_audit, save_report


def batch(root: Path, engine: str, model: str | None):
    inbox, reports = root / "inbox", root / "reports"
    for directory in (root, inbox, reports):
        try:
            mode = directory.lstat().st_mode
        except FileNotFoundError:
            directory.mkdir(mode=0o700, exist_ok=True)
        else:
            if not stat.S_ISDIR(mode):
                raise NotADirectoryError(errno.ENOTDIR, "Expected a directory", directory)
    rule_path = root / "rules.json"
    rules = load_rules(rule_path if rule_path.exists() else None)
    signature = [engine, model, rules]
    stats = Counter(dict(processed=0, unchanged=0, failed=0, draft_edits=0, suggestions=0))
    operations = Counter(dict(插入=0, 替换=0, 删除=0))

    fd = os.open(root / ".batch.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "rb") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for path in sorted(inbox.glob("*.txt")):
            if path.is_symlink() or not path.is_file():
                continue
            output = reports / (path.name + ".json")
            try:
                text = path.read_bytes().decode("utf-8-sig")
                digest = hashlib.sha256(json.dumps([text, signature], ensure_ascii=False).encode()).hexdigest()
                if output.is_file():
                    try:
                        previous = json.loads(output.read_text(encoding="utf-8"))
                        if isinstance(previous, dict) and previous.get("batch_digest") == digest:
                            stats["unchanged"] += 1
                            continue
                    except (ValueError, OSError):
                        pass
                candidates = model_audit(text, engine, model, "") if model else []
                report = audit(text, rules, candidates)
                save_report(output, {"batch_digest": digest, "engine": engine, "model": model, **report})
            except (OSError, ValueError):
                stats["failed"] += 1
                continue
            stats["processed"] += 1
            for edit in report["edits"]:
                operations[edit["operation"]] += 1
                status = "draft_edits" if edit["status"] == "已写入草稿" else "suggestions"
                stats[status] += 1

        summary = {"engine": engine, **stats, "operations": dict(operations)}
        save_report(root / "latest-summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Private data directory outside the repository")
    parser.add_argument("--ollama-model", help="Use a model already running on local Ollama")
    args = parser.parse_args()
    try:
        summary = batch(args.root, "ollama" if args.ollama_model else "rules", args.ollama_model)
    except BlockingIOError:
        print("校对批处理已在运行。", file=sys.stderr)
        return 1
    except OSError as error:
        name = Path(error.filename).name if error.filename else ""
        operation = {
            ".batch.lock": "打开批处理锁", "inbox": "访问摘录目录", "reports": "访问报告目录",
            "local-ocr": "访问工作目录", "rules.json": "读取规则", "latest-summary.json": "保存汇总",
        }.get(name, "写入汇总临时文件" if name.startswith(".ocr-audit-") else "执行本地文件操作")
        code = errno.errorcode.get(error.errno, "UNKNOWN")
        print(f"校对批处理失败。{operation}返回 {code}。", file=sys.stderr)
        return 1
    except ValueError:
        print("无法读取校对规则，请检查 JSON 格式和规则内容。", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False))
    return int(summary["failed"] > 0)


if __name__ == "__main__":
    sys.exit(main())
