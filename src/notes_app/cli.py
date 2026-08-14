import sys
import os
import subprocess
import tempfile
from datetime import datetime
from src.notes_app.notes.models import Note
from src.notes_app.notes.storage import (
    save_note, load_note, update_note as _update_note, delete_note as _delete_note,
    search_notes_by_keyword, filter_notes_by_tag, get_all_tags,
)
from src.notes_app.config.paths import (
    get_absolute_path_to_notes_home, build_note_file_path, ensure_notes_directory_exists,
)


def format_readable_date(dt):
    """Turn a datetime into a friendly readable string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def extract_flag_value(args, flag_name):
    """
    Look through args for a flag like --tags or --tag, and return the
    value right after it. Returns None if the flag isn't present.
    """
    if flag_name in args:
        index = args.index(flag_name)
        if index + 1 < len(args):
            return args[index + 1]
    return None


def read_multiline_content():
    """Read multiple lines of content until the user presses Ctrl+D (EOF)."""
    print("Enter note content (press Ctrl+D when done):")
    content = sys.stdin.read()
    return content.strip()


def read_content_via_editor(initial_content=None):
    """
    Open the user's editor on a temp file, then read back what they wrote.
    If initial_content is given, the temp file is pre-populated with it so
    the user can edit in place rather than starting from a blank file.
    """
    editor = os.environ.get("EDITOR", "nano")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tf:
        if initial_content:
            tf.write(initial_content)
        temp_path = tf.name

    try:
        subprocess.call([editor, temp_path])
        with open(temp_path, "r", encoding="utf-8") as f:
            content = f.read()
    finally:
        os.unlink(temp_path)

    return content.strip()


def create_note(title, content, author="unknown", tags=None):
    """Create a new Note, save it, and report the result."""
    note = Note(title, author, content=content)
    if tags is not None:
        note.tags = tags

    file_path = save_note(note)
    print(f"Note created successfully: {file_path.name}")
    return file_path.name


def list_all_notes():
    """Return all .md filenames in the notes directory, newest-modified first."""
    notes_dir = get_absolute_path_to_notes_home() / "notes"
    if not notes_dir.exists():
        return []

    note_files = list(notes_dir.glob("*.md"))
    note_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return note_files


def find_note_by_partial_name(partial):
    """
    Find a note whose filename or title contains the given partial text
    (case-insensitive). Returns the matching Path, or None if there's no
    match or more than one match (printing a message either way).
    """
    partial_lower = partial.lower()
    matches = []

    for path in list_all_notes():
        note = load_note(path)
        if partial_lower in path.name.lower() or partial_lower in note.title.lower():
            matches.append(path)

    if len(matches) == 0:
        print(f"No note found matching '{partial}'", file=sys.stderr)
        return None

    if len(matches) > 1:
        print(f"Multiple notes match '{partial}', please be more specific:", file=sys.stderr)
        for path in matches:
            print(f"  {path.name}", file=sys.stderr)
        return None

    return matches[0]


def display_notes_list(note_files):
    """Print a summary of each note file."""
    if not note_files:
        print("No notes found.")
        return

    print("Your Notes:")
    print("============")

    for path in note_files:
        note = load_note(path)
        print(f"{path.name}:")
        print(f"  Title: {note.title}")
        print(f"  Modified: {format_readable_date(note.modified)}")
        if note.tags:
            print(f"  Tags: {', '.join(note.tags)}")
        print()


def display_note(note):
    """Print full details of a single note."""
    print("=" * 50)
    print(note.title)
    print("=" * 50)
    print()
    print(f"Created: {format_readable_date(note.created)}")
    print(f"Modified: {format_readable_date(note.modified)}")

    if note.tags:
        print(f"Tags: {', '.join(note.tags)}")

    if note.author is not None:
        print(f"Author: {note.author}")

    print()
    print("-" * 50)
    print(note.content)
    print("-" * 50)


def read_note_by_filename(filename):
    """Load and display a note by its filename."""
    notes_dir = get_absolute_path_to_notes_home() / "notes"
    full_path = notes_dir / filename
    note = load_note(full_path)
    display_note(note)


def update_note(filename, new_content=None, new_tags=None):
    """Update a note's content/tags and report the result."""
    notes_dir = get_absolute_path_to_notes_home() / "notes"
    full_path = notes_dir / filename
    _update_note(full_path, content=new_content, tags=new_tags)
    print(f"Note updated successfully: {filename}")


def delete_note(filename):
    """Delete a note, asking for confirmation first."""
    notes_dir = get_absolute_path_to_notes_home() / "notes"
    full_path = notes_dir / filename

    if not full_path.exists():
        print(f"Note not found: {filename}", file=sys.stderr)
        return

    confirmation = input(f"Are you sure you want to delete '{filename}'? (yes/no): ").strip().lower()

    if confirmation == "yes":
        _delete_note(full_path)
        print(f"Note deleted successfully: {filename}")
    else:
        print("Deletion cancelled.")


def display_search_results(results, keyword):
    """Print search results for a keyword search."""
    if not results:
        print(f"No notes found containing '{keyword}'")
        return

    print(f"Found {len(results)} note(s) containing '{keyword}':")
    print()

    for file_path, note in results:
        print(f"{file_path.name}: {note.title}")


def show_help():
    print("""
Nice Notes Manager

Usage:
  notes create [--tags tag1,tag2]     Create a new note
  notes list [--tag tagname]          List all notes or filter by tag
  notes read <name>                   Display a specific note (partial match)
  notes update <name>                 Update a note (partial match)
  notes delete <name>                 Delete a note (partial match)
  notes search <keyword>              Search notes by keyword
  notes tags                          List all tags
  notes --help                        Show this help message

Environment Variables:
  NOTES_HOME    Directory where notes are stored (default: ~/.notes)
    """.strip())


def parse_command_line_arguments(args):
    """Look at args and dispatch to the right command handler."""
    if not args or args[0] == "--help":
        show_help()
        return

    command = args[0].lower()
    rest = args[1:]

    if command == "create":
        handle_create_command(rest)
    elif command == "list":
        handle_list_command(rest)
    elif command == "read":
        handle_read_command(rest)
    elif command == "update":
        handle_update_command(rest)
    elif command == "delete":
        handle_delete_command(rest)
    elif command == "search":
        handle_search_command(rest)
    elif command == "tags":
        handle_tags_command(rest)
    else:
        print(f"Unknown command: {command}")
        print("Use --help for usage information")


def handle_create_command(args):
    tags_value = extract_flag_value(args, "--tags")
    tags = [t.strip() for t in tags_value.split(",") if t.strip()] if tags_value else None

    author = extract_flag_value(args, "--author") or "unknown"

    title = input("Enter note title: ").strip()
    if not title:
        print("Error: Title cannot be empty")
        return

    if "--editor" in args:
        content = read_content_via_editor()
    else:
        content = read_multiline_content()

    create_note(title, content, author=author, tags=tags)


def handle_list_command(args):
    tag_filter = extract_flag_value(args, "--tag")

    if tag_filter is not None:
        base_dir = get_absolute_path_to_notes_home()
        results = filter_notes_by_tag(base_dir, tag_filter)
        if not results:
            print(f"No notes tagged '{tag_filter}'")
        else:
            print(f"Notes tagged with '{tag_filter}':")
            for path, note in results:
                print(f"  {path.name}: {note.title}")
    else:
        display_notes_list(list_all_notes())


def handle_read_command(args):
    if len(args) < 1:
        print("Error: Please specify a filename")
        print("Usage: notes read <name>")
        return

    match = find_note_by_partial_name(args[0])
    if match is not None:
        read_note_by_filename(match.name)


def handle_update_command(args):
    if len(args) < 1:
        print("Error: Please specify a filename")
        print("Usage: notes update <name> [--tags tag1,tag2]")
        return

    match = find_note_by_partial_name(args[0])
    if match is None:
        return

    existing_note = load_note(match)

    tags_value = extract_flag_value(args, "--tags")
    new_tags = [t.strip() for t in tags_value.split(",") if t.strip()] if tags_value else None

    if "--editor" in args:
        # Pre-populate the editor with the existing content so the user
        # edits in place instead of retyping everything from scratch.
        new_content = read_content_via_editor(initial_content=existing_note.content)
    else:
        print("Current content:")
        print("-" * 50)
        print(existing_note.content)
        print("-" * 50)
        print()
        new_content = read_multiline_content()

    update_note(match.name, new_content=new_content, new_tags=new_tags)


def handle_delete_command(args):
    if len(args) < 1:
        print("Error: Please specify a filename")
        print("Usage: notes delete <name>")
        return

    match = find_note_by_partial_name(args[0])
    if match is not None:
        delete_note(match.name)


def handle_search_command(args):
    if len(args) < 1:
        print("Error: Please specify a search keyword")
        print("Usage: notes search <keyword>")
        return

    keyword = args[0]
    base_dir = get_absolute_path_to_notes_home()
    results = search_notes_by_keyword(base_dir, keyword)
    display_search_results(results, keyword)


def handle_tags_command(args):
    base_dir = get_absolute_path_to_notes_home()
    all_tags = get_all_tags(base_dir)

    if not all_tags:
        print("No tags found.")
    else:
        print("All tags:")
        for tag in all_tags:
            print(f"  - {tag}")


def main():
    ensure_notes_directory_exists()

    args = sys.argv[1:]

    try:
        parse_command_line_arguments(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Use --help for usage information", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()