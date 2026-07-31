import unittest
import shutil
from pathlib import Path
from src.notes_app.notes.models import Note
from src.notes_app.notes import storage


class TestStorage(unittest.TestCase):

    def setUp(self):
        """Runs before every test: use a temporary, isolated notes folder."""
        self.test_dir = Path("/tmp/notes_app_test")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)

        # Point storage functions at our temporary folder instead of ~/.notes
        self.original_build_path = storage.build_note_file_path
        self.original_ensure_dir = storage.ensure_notes_directory_exists

        def fake_build_path(filename):
            return self.test_dir / "notes" / filename

        def fake_ensure_dir():
            (self.test_dir / "notes").mkdir(parents=True, exist_ok=True)

        storage.build_note_file_path = fake_build_path
        storage.ensure_notes_directory_exists = fake_ensure_dir

    def tearDown(self):
        """Runs after every test: restore originals and clean up."""
        storage.build_note_file_path = self.original_build_path
        storage.ensure_notes_directory_exists = self.original_ensure_dir
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_save_and_load_round_trip(self):
        note = Note("Test Note", "Vijay", content="Hello there", tags=["x", "y"])
        path = storage.save_note(note)

        loaded = storage.load_note(path)
        self.assertEqual(loaded.title, "Test Note")
        self.assertEqual(loaded.author, "Vijay")
        self.assertEqual(loaded.content, "Hello there")
        self.assertEqual(loaded.tags, ["x", "y"])

    def test_update_note_changes_only_given_fields(self):
        note = Note("Original", "Vijay", content="Original content", tags=["a"])
        path = storage.save_note(note)

        storage.update_note(path, title="Updated Title")

        reloaded = storage.load_note(path)
        self.assertEqual(reloaded.title, "Updated Title")
        self.assertEqual(reloaded.content, "Original content")  # unchanged
        self.assertEqual(reloaded.tags, ["a"])  # unchanged

    def test_delete_note_removes_file(self):
        note = Note("To Delete", "Vijay")
        path = storage.save_note(note)
        self.assertTrue(path.exists())

        result = storage.delete_note(path)
        self.assertTrue(result)
        self.assertFalse(path.exists())

    def test_delete_nonexistent_note_returns_false(self):
        fake_path = self.test_dir / "notes" / "does-not-exist.md"
        result = storage.delete_note(fake_path)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()