from datetime import datetime
from src.notes_app.utils.text_utils import sanitize_title_for_filename


class Note:
    """Represents a single note with metadata and content."""

    def __init__(self, title, author, content="", tags=None, created=None, modified=None):
        if not title.strip():
            raise ValueError("Note title cannot be empty")

        self.title = title
        self.author = author
        self.content = content
        self.tags = tags if tags is not None else []
        self.created = created if created is not None else datetime.now()
        self.modified = modified if modified is not None else self.created

    # add this method inside the Note class, below __init__:
    def generate_filename(self):
        """Return a unique, filesystem-safe filename for this note."""
        safe_title = sanitize_title_for_filename(self.title)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{safe_title}-{timestamp}.md"

