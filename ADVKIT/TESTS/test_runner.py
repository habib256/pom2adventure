"""Contrat du lanceur : sélection, échecs et rapports sans lancer les bancs."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import run as harness


class RunnerTests(unittest.TestCase):
    def invoke(self, args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return harness.main(args)

    def test_profiles_do_not_start_external_services(self):
        self.assertEqual(harness.select(["quick", "node"]), ["python", "node", "native"])
        self.assertFalse(set(harness.select(["all"])) & {"http", "browser"})
        node = harness.commands("node", "python")
        self.assertTrue(node)
        self.assertFalse(any(Path(cmd[-1]).name in harness.INTEGRATION for cmd, _ in node))
        python = harness.commands("python", "python")
        self.assertTrue(any("test_midi_to_mb.py" in cmd[-1] for cmd, _ in python))
        self.assertFalse(any("test_image_" in cmd[-1] for cmd, _ in python))

    def test_failure_is_preserved_and_other_tests_continue(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "report.json"
            with patch.object(harness, "commands", return_value=[(["a"], False), (["b"], False)]), \
                 patch.object(harness.subprocess, "run", side_effect=[
                     subprocess.CompletedProcess(["a"], 7), subprocess.CompletedProcess(["b"], 0),
                 ]) as run:
                self.assertEqual(self.invoke(["node", "--report", str(report)]), 1)
            self.assertEqual(run.call_count, 2)
            self.assertEqual(run.call_args.kwargs["cwd"], harness.ROOT)
            data = json.loads(report.read_text())
            self.assertEqual(data["failed"], ["node"])
            self.assertEqual([c["returncode"] for c in data["commands"]], [7, 0])

    def test_missing_prerequisite_blocks_only_its_suite(self):
        with patch.object(harness, "commands", side_effect=[
            [(["missing"], True), (["dependent"], False)], [(["next"], False)],
        ]), patch.object(harness.subprocess, "run", side_effect=[
            FileNotFoundError("missing"), subprocess.CompletedProcess(["next"], 0),
        ]) as run:
            self.assertEqual(self.invoke(["images", "node"]), 1)
            self.assertEqual([c.args[0] for c in run.call_args_list], [["missing"], ["next"]])

    def test_timeout_is_a_failure(self):
        with patch.object(harness, "commands", return_value=[(["slow"], False)]), \
             patch.object(harness.subprocess, "run", side_effect=subprocess.TimeoutExpired("slow", 1)):
            self.assertEqual(self.invoke(["node", "--timeout", "1"]), 1)

    def test_dry_run_neither_executes_nor_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "absent.json"
            with patch.object(harness.subprocess, "run") as run:
                self.assertEqual(self.invoke(["all", "--dry-run", "--report", str(report)]), 0)
                run.assert_not_called()
            self.assertFalse(report.exists())

    def test_invalid_suite_fails_before_running(self):
        with patch.object(harness.subprocess, "run") as run:
            with self.assertRaises(SystemExit) as exc:
                self.invoke(["typo"])
            self.assertEqual(exc.exception.code, 2)
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
