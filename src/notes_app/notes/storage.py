
from datetime import datetime
from src.notes_app.notes.models import Note
from src.notes_app.notes.validation import is_valid_note
from src.notes_app.config.paths import build_note_file_path, ensure_notes_directory_exists


def format_note_for_file(note):
    """Convert a Note into YAML front matter + Markdown text, built manually."""
    output = "---\n"
    output += f"title: {note.title}\n"
    output += f"created: {note.created.isoformat()}\n"
    output += f"modified: {note.modified.isoformat()}\n"

    if note.tags:
        output += f"tags: [{', '.join(note.tags)}]\n"

    if getattr(note, "author", None):
        output += f"author: {note.author}\n"
    if getattr(note, "status", None):
        output += f"status: {note.status}\n"
    if getattr(note, "priority", None):
        output += f"priority: {note.priority}\n"

    output += "---\n\n"
    output += note.content
    return output


def parse_yaml_header(file_content):
    """Split a note file's text into (metadata dict, content string)."""
    if not file_content.startswith("---"):
        raise ValueError("Invalid note format: missing YAML header")

    lines = file_content.split("\n")

    yaml_end_index = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            yaml_end_index = i
            break

    if yaml_end_index == -1:
        raise ValueError("Invalid note format: YAML header not closed")

    yaml_lines = lines[1:yaml_end_index]
    metadata = {}
    for line in yaml_lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key == "tags":
            value = value.strip("[]")
            metadata[key] = [t.strip() for t in value.split(",") if t.strip()]
        else:
            metadata[key] = value

    content_lines = lines[yaml_end_index + 1:]
    content = "\n".join(content_lines).strip()

    return metadata, content


def save_note(note):
    """Validate, format, and write a Note to disk. Returns the file path."""
    if not is_valid_note(note):
        raise ValueError("Invalid note")

    ensure_notes_directory_exists()
    filename = note.generate_filename()
    full_path = build_note_file_path(filename)
    full_path.write_text(format_note_for_file(note), encoding="utf-8")
    return full_path


def load_note(file_path):
    """Read a note file from disk and reconstruct a Note object."""
    if not file_path.exists():
        raise FileNotFoundError(f"Note file not found: {file_path}")

    file_content = file_path.read_text(encoding="utf-8")
    metadata, content = parse_yaml_header(file_content)

    note = Note(
        title=metadata["title"],
        author=metadata.get("author", "unknown"),
        content=content,
        tags=metadata.get("tags", []),
        created=datetime.fromisoformat(metadata["created"]),
        modified=datetime.fromisoformat(metadata["modified"]),
    )
    return note


def update_note(file_path, title=None, author=None, content=None, tags=None):
    """Load a note, change only the fields provided, save it back in place."""
    note = load_note(file_path)

    if title is not None:
        note.title = title
    if author is not None:
        note.author = author
    if content is not None:
        note.content = content
    if tags is not None:
        note.tags = tags

    note.modified = datetime.now()
    file_path.write_text(format_note_for_file(note), encoding="utf-8")
    return note


def delete_note(file_path):
    """Delete a note file from disk. Returns True if deleted, False if it didn't exist."""
    if not file_path.exists():
        return False
    file_path.unlink()
    return True


def list_all_notes(base_dir):
    """Return a list of (file_path, Note) tuples for every note in the notes folder."""
    notes_dir = base_dir / "notes"
    if not notes_dir.exists():
        return []

    results = []
    for path in sorted(notes_dir.glob("*.md")):
        note = load_note(path)
        results.append((path, note))
    return results

def search_notes_by_keyword(base_dir, keyword):
    """Search notes by keyword in title or content (case-insensitive)."""
    all_notes = list_all_notes(base_dir)
    matching_notes = []

    for file_path, note in all_notes:
        if keyword.lower() in note.title.lower():
            matching_notes.append((file_path, note))
        elif keyword.lower() in note.content.lower():
            matching_notes.append((file_path, note))

    return matching_notes


def filter_notes_by_tag(base_dir, tag):
    """Filter notes by tag (case-insensitive)."""
    all_notes = list_all_notes(base_dir)
    matching_notes = []

    for file_path, note in all_notes:
        note_tags_lower = [t.lower() for t in note.tags]
        if tag.lower() in note_tags_lower:
            matching_notes.append((file_path, note))

    return matching_notes


def get_all_tags(base_dir):
    """Return a sorted list of every unique tag across all notes."""
    all_notes = list_all_notes(base_dir)
    all_tags = set()

    for _, note in all_notes:
        for tag in note.tags:
            all_tags.add(tag)

    return sorted(all_tags)