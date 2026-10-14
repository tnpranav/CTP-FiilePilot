import tempfile
import unittest
from pathlib import Path

from file_tools import scan_folder, organize_files, get_file_type


class FileToolTests(unittest.TestCase):
    def test_exact_duplicates_are_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("same content", encoding="utf-8")
            (root / "b.txt").write_text("same content", encoding="utf-8")
            (root / "c.txt").write_text("different content", encoding="utf-8")
            records, groups, errors = scan_folder(root)
            self.assertEqual(len(records), 3)
            self.assertEqual(len(groups), 1)
            self.assertEqual(len(groups[0]["files"]), 2)
            self.assertEqual(errors, [])

    def test_organize_preview_does_not_move_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "notes.txt"
            source.write_text("hello", encoding="utf-8")
            result = organize_files(root, dry_run=True)
            self.assertEqual(result["planned"], 1)
            self.assertTrue(source.exists())
            self.assertFalse((root / "Documents" / "notes.txt").exists())

    def test_organize_execute_moves_to_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "notes.txt"
            source.write_text("hello", encoding="utf-8")
            result = organize_files(root, dry_run=False)
            self.assertEqual(result["moved"], 1)
            self.assertFalse(source.exists())
            self.assertTrue((root / "Documents" / "notes.txt").exists())

    def test_unknown_extension_is_other(self):
        self.assertEqual(get_file_type("sample.customext"), "Other")


if __name__ == "__main__":
    unittest.main()
