import unittest
import shutil
from pathlib import Path
from src.notes_app.notes.models import Note
from src.notes_app.notes import storage


class TestSearchAndFilter(unittest.TestCase):

    def setUp(self):
        """Isolated test folder, with a few known notes pre-created."""
        self.test_dir = Path("/tmp/notes_app_search_test")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)

        self.original_build_path = storage.build_note_file_path
        self.original_ensure_dir = storage.ensure_notes_directory_exists

        def fake_build_path(filename):
            return self.test_dir / "notes" / filename

        def fake_ensure_dir():
            (self.test_dir / "notes").mkdir(parents=True, exist_ok=True)

        storage.build_note_file_path = fake_build_path
        storage.ensure_notes_directory_exists = fake_ensure_dir

        # Create a few known notes to search/filter against
        storage.save_note(Note("Grocery List", "Vijay", content="Milk and eggs", tags=["shopping"]))
        storage.save_note(Note("Meeting Notes", "Vijay", content="Discuss the budget", tags=["work"]))
        storage.save_note(Note("Random Thoughts", "Vijay", content="No tags here", tags=[]))

    def tearDown(self):
        storage.build_note_file_path = self.original_build_path
        storage.ensure_notes_directory_exists = self.original_ensure_dir
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_search_matches_title(self):
        results = storage.search_notes_by_keyword(self.test_dir, "Grocery")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1].title, "Grocery List")

    def test_search_matches_content(self):
        results = storage.search_notes_by_keyword(self.test_dir, "budget")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1].title, "Meeting Notes")

    def test_search_is_case_insensitive(self):
        results = storage.search_notes_by_keyword(self.test_dir, "MILK")
        self.assertEqual(len(results), 1)

    def test_search_no_match_returns_empty_list(self):
        results = storage.search_notes_by_keyword(self.test_dir, "nonexistent-word-xyz")
        self.assertEqual(results, [])

    def test_filter_by_tag_finds_correct_note(self):
        results = storage.filter_notes_by_tag(self.test_dir, "shopping")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1].title, "Grocery List")

    def test_filter_by_tag_is_case_insensitive(self):
        results = storage.filter_notes_by_tag(self.test_dir, "SHOPPING")
        self.assertEqual(len(results), 1)

    def test_filter_by_tag_no_match_returns_empty_list(self):
        results = storage.filter_notes_by_tag(self.test_dir, "nonexistent-tag")
        self.assertEqual(results, [])

    def test_get_all_tags_returns_sorted_unique_list(self):
        all_tags = storage.get_all_tags(self.test_dir)
        self.assertEqual(all_tags, ["shopping", "work"])


if __name__ == "__main__":
    unittest.main()