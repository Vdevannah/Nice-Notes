from datetime import datetime


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

        