import unittest
from src.notes_app.notes.models import Note
from src.notes_app.notes.validation import validate_title, is_valid_note


class TestNoteCreation(unittest.TestCase):

    def test_valid_note_has_correct_fields(self):
        note = Note("My Title", "Vijay", content="Some content", tags=["a", "b"])
        self.assertEqual(note.title, "My Title")
        self.assertEqual(note.author, "Vijay")
        self.assertEqual(note.content, "Some content")
        self.assertEqual(note.tags, ["a", "b"])

    def test_empty_title_raises_value_error(self):
        with self.assertRaises(ValueError):
            Note("", "Vijay")

    def test_whitespace_only_title_raises_value_error(self):
        with self.assertRaises(ValueError):
            Note("   ", "Vijay")

    def test_default_content_is_empty_string(self):
        note = Note("Title Only", "Vijay")
        self.assertEqual(note.content, "")

    def test_default_tags_is_empty_list(self):
        note = Note("Title Only", "Vijay")
        self.assertEqual(note.tags, [])

    def test_two_notes_do_not_share_the_same_tags_list(self):
        # Regression test for the tags=None list-aliasing bug we discussed
        note1 = Note("Note One", "Vijay")
        note2 = Note("Note Two", "Vijay")
        note1.tags.append("urgent")
        self.assertEqual(note2.tags, [])

    def test_modified_defaults_to_same_as_created(self):
        note = Note("Title Only", "Vijay")
        self.assertEqual(note.created, note.modified)

    def test_generate_filename_contains_sanitized_title(self):
        note = Note("Hello World!!", "Vijay")
        filename = note.generate_filename()
        self.assertIn("hello-world", filename)
        self.assertTrue(filename.endswith(".md"))


class TestValidation(unittest.TestCase):

    def test_validate_title_accepts_normal_title(self):
        self.assertTrue(validate_title("A Normal Title"))

    def test_validate_title_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            validate_title("")

    def test_validate_title_rejects_long_title(self):
        with self.assertRaises(ValueError):
            validate_title("a" * 201)

    def test_is_valid_note_true_for_good_note(self):
        note = Note("Good Title", "Vijay")
        self.assertTrue(is_valid_note(note))


if __name__ == "__main__":
    unittest.main()