import yaml
from datetime import datetime
from src.notes_app.notes.models import Note
from src.notes_app.config.paths import build_note_file_path, ensure_notes_directory_exists


def serialize_note(note):
    """Convert a Note object into YAML front matter + Markdown text."""
    metadata = {
        "title": note.title,
        "author": note.author,
        "created": note.created.isoformat(),
        "modified": note.modified.isoformat(),
        "tags": note.tags,
    }
    yaml_block = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
    return f"---\n{yaml_block}---\n\n{note.content}"


def parse_note_file(file_path):
    """Read a note file from disk and turn it back into a Note object."""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    parts = text.split("---", 2)
    yaml_block = parts[1]
    body = parts[2].strip()

    metadata = yaml.safe_load(yaml_block)

    return Note(
        title=metadata["title"],
        author=metadata["author"],
        content=body,
        tags=metadata.get("tags", []),
        created=datetime.fromisoformat(metadata["created"]),
        modified=datetime.fromisoformat(metadata["modified"]),
    )


def save_note(note):
    """Write a Note to disk using its generated filename. Returns the file path."""
    ensure_notes_directory_exists()
    filename = note.generate_filename()
    file_path = build_note_file_path(filename)
    file_path.write_text(serialize_note(note), encoding="utf-8")
    return file_path


def load_note(file_path):
    """Load a Note from a given file path."""
    return parse_note_file(file_path)