import os
import shutil
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from src.notes_app.api.main import app


class TestApi(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path("/tmp/notes_app_api_test")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)

        self.original_notes_home = os.environ.get("NOTES_HOME")
        os.environ["NOTES_HOME"] = str(self.test_dir)

        self.client = TestClient(app)

    def tearDown(self):
        if self.original_notes_home is None:
            os.environ.pop("NOTES_HOME", None)
        else:
            os.environ["NOTES_HOME"] = self.original_notes_home
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def create_note(self, title="Test Note", content="Hello", author="Vijay", tags=None):
        response = self.client.post("/notes", json={
            "title": title,
            "content": content,
            "author": author,
            "tags": tags or [],
        })
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_create_and_read_round_trip(self):
        created = self.create_note(title="My Note", content="Body text", tags=["a", "b"])

        response = self.client.get(f"/notes/{created['filename']}")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["title"], "My Note")
        self.assertEqual(body["content"], "Body text")
        self.assertEqual(body["tags"], ["a", "b"])

    def test_create_with_empty_title_returns_400(self):
        response = self.client.post("/notes", json={"title": "   "})
        self.assertEqual(response.status_code, 400)

    def test_list_notes_empty(self):
        response = self.client.get("/notes")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_list_notes_filters_by_tag(self):
        self.create_note(title="Tagged", tags=["work"])
        self.create_note(title="Untagged")

        response = self.client.get("/notes", params={"tag": "work"})
        self.assertEqual(response.status_code, 200)
        titles = [n["title"] for n in response.json()]
        self.assertEqual(titles, ["Tagged"])

    def test_list_notes_search_by_keyword(self):
        self.create_note(title="Findme", content="nothing special")
        self.create_note(title="Other", content="irrelevant")

        response = self.client.get("/notes", params={"q": "findme"})
        self.assertEqual(response.status_code, 200)
        titles = [n["title"] for n in response.json()]
        self.assertEqual(titles, ["Findme"])

    def test_read_missing_note_returns_404(self):
        response = self.client.get("/notes/does-not-exist.md")
        self.assertEqual(response.status_code, 404)

    def test_update_changes_only_given_fields(self):
        created = self.create_note(title="Original", content="Original content", tags=["x"])

        response = self.client.patch(f"/notes/{created['filename']}", json={"title": "Updated"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["title"], "Updated")
        self.assertEqual(body["content"], "Original content")
        self.assertEqual(body["tags"], ["x"])

    def test_update_missing_note_returns_404(self):
        response = self.client.patch("/notes/does-not-exist.md", json={"title": "Updated"})
        self.assertEqual(response.status_code, 404)

    def test_delete_then_read_returns_404(self):
        created = self.create_note()

        response = self.client.delete(f"/notes/{created['filename']}")
        self.assertEqual(response.status_code, 204)

        response = self.client.get(f"/notes/{created['filename']}")
        self.assertEqual(response.status_code, 404)

    def test_delete_missing_note_returns_404(self):
        response = self.client.delete("/notes/does-not-exist.md")
        self.assertEqual(response.status_code, 404)

    def test_list_tags(self):
        self.create_note(title="One", tags=["red", "blue"])
        self.create_note(title="Two", tags=["blue"])

        response = self.client.get("/tags")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), ["blue", "red"])

    def test_invalid_filename_rejected(self):
        response = self.client.get("/notes/..%2F..%2Fetc%2Fpasswd")
        self.assertIn(response.status_code, (400, 404))


if __name__ == "__main__":
    unittest.main()
