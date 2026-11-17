import tempfile
import unittest
from pathlib import Path

from runner.core import source_fingerprint


class SourceFingerprintTests(unittest.TestCase):
    def test_report_nested_source_and_path_changes_invalidate_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "report").mkdir()
            path = root / "report/a.py"
            path.write_bytes(b"original")
            first = source_fingerprint(root)
            self.assertEqual(first, source_fingerprint(root))
            (root / "report/cache.txt").write_bytes(b"not Python")
            self.assertEqual(first, source_fingerprint(root))
            path.write_bytes(b"changed")
            second = source_fingerprint(root)
            self.assertNotEqual(first, second)
            path.rename(root / "report/b.py")
            self.assertNotEqual(second, source_fingerprint(root))
            (root / "report/nested").mkdir()
            (root / "report/nested/c.py").write_bytes(b"extra")
            self.assertNotEqual(second, source_fingerprint(root))

    def test_partition_boundaries_prevent_concatenation_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_bytes(b"ab")
            (root / "b.py").write_bytes(b"c")
            first = source_fingerprint(root)
            (root / "a.py").write_bytes(b"a")
            (root / "b.py").write_bytes(b"bc")
            self.assertNotEqual(first, source_fingerprint(root))
