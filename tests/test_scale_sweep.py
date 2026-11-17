import tempfile
import unittest
from pathlib import Path

from experiments.scale_sweep import parse_peak_rss


class PeakMemoryTests(unittest.TestCase):
    def test_valid_and_invalid_peak_memory_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rss.txt"
            path.write_text("12345\n")
            self.assertEqual(parse_peak_rss(path), 12345)
            for text in ("", "nan", "-1", "1.5", "1\n2", "１２３"):
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ValueError):
                    parse_peak_rss(path)
