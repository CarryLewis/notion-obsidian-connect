import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ocr_audit
from ocr_audit import DEMO, audit, load_rules, model_audit

SCRIPT = Path(ocr_audit.__file__)
BATCH_SCRIPT = SCRIPT.with_name("ocr_batch.py")


class OCRAuditTests(unittest.TestCase):
    def test_rule_based_draft_preserves_original_and_exact_coordinates(self):
        text = DEMO.replace("\n", "\r\n")
        result = audit(text, load_rules(None))
        self.assertEqual(result["original"], text)
        self.assertIn("海马体参与记忆形成。\r\n", result["draft"])
        self.assertIn("神经可塑性", result["draft"])
        self.assertEqual(
            [(e["line"], e["column"], e["old"], e["new"]) for e in result["edits"]],
            [(2, 1, "", "海"), (3, 4, "朔", "塑")],
        )

    def test_rules_leave_normal_text_unchanged_and_require_line_start(self):
        text = "人人都可以看看这条马体参与记忆的示例。"
        self.assertEqual(audit(text, load_rules(None))["draft"], text)
        self.assertEqual(audit(text, load_rules(None))["edits"], [])

    def test_semantic_edits_are_suggestions_and_must_have_exact_unique_anchors(self):
        text = "马体与学习有关。\n看看，看看。\n经系统评估，数字为12。"
        model_edits = [
            {"line": 1, "before": "马体与学习", "after": "海马体与学习"},
            {"line": 2, "before": "看看", "after": "看"},
            {"line": 3, "before": "数字为12", "after": "数字为13"},
            {"line": 3, "before": "未出现的锚点", "after": "出现的锚点"},
            {"line": 3, "before": "经系统评估", "after": "这一经过评估"},
            {"line": True, "before": "马体", "after": "海马体"},
        ]
        result = audit(text, [], model_edits)
        self.assertEqual(result["draft"], text)
        self.assertEqual(result["discarded_model_edits"], 5)
        self.assertEqual(len(result["edits"]), 1)
        self.assertEqual(result["edits"][0]["status"], "建议")

    def test_conflicting_rules_keep_original(self):
        text = "甲己。"
        result = audit(text, [{"before": "甲己", "after": "甲乙"}, {"before": "己", "after": "丙"}])
        self.assertEqual(result["draft"], text)
        self.assertEqual({item["status"] for item in result["edits"]}, {"规则冲突"})

    def test_model_api_modes(self):
        edits = [{"line": 1, "before": "马体", "after": "海马体"}]
        content = json.dumps({"edits": edits})
        for engine, response, expected_url in [
            ("deepseek", {"choices": [{"finish_reason": "stop", "message": {"content": content}}]},
             "https://api.deepseek.com/chat/completions"),
            ("ollama", {"done": True, "message": {"content": content}}, "http://127.0.0.1:11434/api/chat"),
        ]:
            with self.subTest(engine=engine), patch.object(ocr_audit, "build_opener") as builder:
                opener = builder.return_value
                opener.open.return_value = io.StringIO(json.dumps(response))
                self.assertEqual(model_audit("马体参与记忆", engine, "test-model", "test-token"), edits)
                request = opener.open.call_args.args[0]
                self.assertEqual(request.full_url, expected_url)
                self.assertEqual("Authorization" in request.headers, engine == "deepseek")
                self.assertIn("马体参与记忆", json.loads(json.loads(request.data)["messages"][1]["content"])[0]["text"])

    def test_incomplete_api_output_is_an_error(self):
        with patch.object(ocr_audit, "build_opener") as builder:
            builder.return_value.open.return_value = io.StringIO(json.dumps({
                "choices": [{"finish_reason": "length", "message": {"content": '{"edits":[]}'}}],
            }))
            with self.assertRaisesRegex(ValueError, "没有返回完整"):
                model_audit("马体", "deepseek", "test-model", "test-token")

    def test_cli_file_report_and_source_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "scan.txt"
            output = Path(directory) / "report.json"
            source.write_text(DEMO, encoding="utf-8")
            command = [sys.executable, "-B", str(SCRIPT), "--file", str(source), "--output"]
            subprocess.run([*command, str(output)], check=True, capture_output=True)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["input_sha256"], hashlib.sha256(DEMO.encode()).hexdigest())
            self.assertEqual(len(report["edits"]), 2)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            rejected = subprocess.run([*command, str(source)], capture_output=True)
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual(source.read_text(encoding="utf-8"), DEMO)

    def test_watch_reprocesses_changes_without_manual_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "scan.txt"
            output = Path(directory) / "report.json"
            source.write_text(DEMO, encoding="utf-8")

            def advance(_interval):
                report = json.loads(output.read_text(encoding="utf-8"))
                if report["original"] == DEMO:
                    source.write_text("神经可朔性。", encoding="utf-8")
                else:
                    raise KeyboardInterrupt

            with (
                patch.object(sys, "argv", [str(SCRIPT), "--file", str(source), "--output", str(output), "--watch"]),
                patch.object(ocr_audit.time, "sleep", side_effect=advance),
                patch("sys.stdout", new_callable=io.StringIO),
            ):
                self.assertEqual(ocr_audit.main(), 130)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["draft"], "神经可塑性。")

    def test_batch_processes_changed_files_and_preserves_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "private"
            inbox = root / "inbox"
            inbox.mkdir(parents=True)
            source = inbox / "scan.txt"
            source.write_text(DEMO, encoding="utf-8")
            command = [sys.executable, "-B", str(BATCH_SCRIPT)]

            missing_root = subprocess.run(command, capture_output=True)
            self.assertEqual(missing_root.returncode, 2)
            command.extend(["--root", str(root)])

            first = subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(json.loads(first.stdout)["draft_edits"], 2)
            report = root / "reports" / "scan.txt.json"
            self.assertEqual(json.loads(report.read_bytes())["original"], DEMO)
            self.assertEqual(source.read_text(encoding="utf-8"), DEMO)

            second = subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(json.loads(second.stdout)["unchanged"], 1)

            source.write_text("神经可朔性。", encoding="utf-8")
            invalid = inbox / "invalid.txt"
            invalid.write_bytes(bytes([255]))
            third = subprocess.run(command, capture_output=True)
            self.assertEqual(third.returncode, 1)
            summary = json.loads(third.stdout)
            self.assertEqual((summary["processed"], summary["failed"]), (1, 1))
            self.assertEqual(json.loads(report.read_bytes())["draft"], "神经可塑性。")
            self.assertEqual(source.read_text(encoding="utf-8"), "神经可朔性。")
            self.assertFalse((root / "reports" / "invalid.txt.json").exists())
