"""Sampling failures and cancellation must not become fabricated load values."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from collector.host_load import HostLoadSampler


class HostLoadTests(unittest.TestCase):
    def test_context_stops_on_failure_and_preserves_boundary_samples(self):
        with tempfile.TemporaryDirectory() as tmp:
            sampler = HostLoadSampler(tmp)
            with patch("collector.host_load.Path.read_text", return_value="0.1 0.2 0.3 1/77 999"):
                with self.assertRaisesRegex(RuntimeError, "fixture"):
                    with sampler:
                        raise RuntimeError("fixture")
            self.assertFalse(sampler.thread.is_alive())
            records = [json.loads(line) for line in sampler.path.read_text().splitlines()]
            self.assertEqual(len(records), 2)
            self.assertTrue(all(r["loadavg"] == [0.1, 0.2, 0.3] and r["error"] is None for r in records))
            self.assertEqual(sampler.metadata()["samples"], 2)
            self.assertEqual(sampler.metadata()["path"], "host-load.jsonl")

    def test_unavailable_or_malformed_load_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            sampler = HostLoadSampler(tmp)
            for error in (OSError("denied"), None):
                with patch("collector.host_load.Path.read_text", side_effect=error, return_value="nan 1 2"):
                    sampler.sample()
            records = [json.loads(line) for line in Path(sampler.path).read_text().splitlines()]
            self.assertTrue(all(r["loadavg"] is None and r["error"] for r in records))
            self.assertEqual(len(sampler.errors), 2)

    def test_write_failure_is_reported_without_changing_execution_status(self):
        sampler = HostLoadSampler("/unused")
        with patch("collector.host_load.Path.read_text", return_value="0 0 0"), \
                patch("collector.host_load.Path.open", side_effect=OSError("fixture disk error")):
            sampler.sample()
        self.assertEqual(sampler.samples, 0)
        self.assertIn("fixture disk error", sampler.errors)
