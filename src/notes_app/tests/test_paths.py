import unittest
import os
import shutil
from pathlib import Path
from src.notes_app.config import paths


class TestPaths(unittest.TestCase):

    def setUp(self):
        """Point NOTES_HOME at a temporary test folder for the duration of each test."""
        self.test_home = Path("/tmp/notes_app_paths_test")
        if self.test_home.exists():
            shutil.rmtree(self.test_home)

        self.original_notes_home = os.environ.get("NOTES_HOME")
        os.environ["NOTES_HOME"] = str(self.test_home)

    def tearDown(self):
        """Restore the original environment and clean up the test folder."""
        if self.original_notes_home is not None:
            os.environ["NOTES_HOME"] = self.original_notes_home
        else:
            os.environ.pop("NOTES_HOME", None)

        if self.test_home.exists():
            shutil.rmtree(self.test_home)

    def test_get_notes_home_directory_respects_env_var(self):
        result = paths.get_notes_home_directory()
        self.assertEqual(result, self.test_home)

    def test_ensure_notes_directory_exists_creates_folder(self):
        notes_subfolder = self.test_home / "notes"
        self.assertFalse(notes_subfolder.exists())

        paths.ensure_notes_directory_exists()

        self.assertTrue(notes_subfolder.exists())

    def test_get_absolute_path_to_notes_home_is_absolute(self):
        result = paths.get_absolute_path_to_notes_home()
        self.assertTrue(result.is_absolute())

    def test_build_note_file_path_joins_notes_subfolder(self):
        result = paths.build_note_file_path("hello.md")
        self.assertTrue(str(result).endswith("notes/hello.md"))


if __name__ == "__main__":
    unittest.main()