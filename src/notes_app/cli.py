import sys
from datetime import datetime
from src.notes_app.notes.models import Note
from src.notes_app.notes.storage import (
    save_note, load_note, update_note as _update_note, delete_note as _delete_note,
    search_notes_by_keyword, filter_notes_by_tag, get_all_tags,
)
from src.notes_app.config.paths import get_absolute_path_to_notes_home, build_note_file_path


def format_readable_date(dt):
    """Turn a datetime into a friendly readable string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


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

Usage: cli.py [command]

Available commands:
  help                       - Display this help information
  create                     - Create a new note (prompts for title, content)
  list                       - List all notes
  read <name>                - Display a specific note (partial name/title match)
  update <name>               - Update a note's content (partial name/title match)
  delete <name>               - Delete a note (partial name/title match)
  search <keyword>           - Search notes by keyword in title/content
  tag <tagname>               - List notes with a specific tag
  tags                        - List all tags used across notes
    """.strip())


def main():
    if len(sys.argv) < 2:
        print("Error: No command provided.", file=sys.stderr)
        show_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "help":
        show_help()

    elif command == "create":
        title = input("Enter note title: ").strip()
        content = input("Enter note content: ").strip()
        tags_input = input("Enter tags (comma-separated, or leave blank): ").strip()
        tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else None
        create_note(title, content, tags=tags)

    elif command == "list":
        display_notes_list(list_all_notes())

    elif command == "read":
        if len(sys.argv) < 3:
            print("Error: Missing name. Usage: cli.py read <name>", file=sys.stderr)
            sys.exit(1)
        match = find_note_by_partial_name(sys.argv[2])
        if match is not None:
            read_note_by_filename(match.name)

    elif command == "update":
        if len(sys.argv) < 3:
            print("Error: Missing name. Usage: cli.py update <name>", file=sys.stderr)
            sys.exit(1)
        match = find_note_by_partial_name(sys.argv[2])
        if match is not None:
            new_content = input("Enter new content: ").strip()
            update_note(match.name, new_content=new_content)

    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: Missing name. Usage: cli.py delete <name>", file=sys.stderr)
            sys.exit(1)
        match = find_note_by_partial_name(sys.argv[2])
        if match is not None:
            delete_note(match.name)

    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Missing keyword. Usage: cli.py search <keyword>", file=sys.stderr)
            sys.exit(1)
        keyword = sys.argv[2]
        base_dir = get_absolute_path_to_notes_home()
        results = search_notes_by_keyword(base_dir, keyword)
        display_search_results(results, keyword)

    elif command == "tag":
        if len(sys.argv) < 3:
            print("Error: Missing tag. Usage: cli.py tag <tagname>", file=sys.stderr)
            sys.exit(1)
        tag = sys.argv[2]
        base_dir = get_absolute_path_to_notes_home()
        results = filter_notes_by_tag(base_dir, tag)
        if not results:
            print(f"No notes tagged '{tag}'")
        else:
            print(f"Notes tagged '{tag}':")
            for path, note in results:
                print(f"  {path.name}: {note.title}")

    elif command == "tags":
        base_dir = get_absolute_path_to_notes_home()
        all_tags = get_all_tags(base_dir)
        if not all_tags:
            print("No tags found.")
        else:
            print("All tags:")
            for tag in all_tags:
                print(f"  - {tag}")

    else:
        print(f"Error: Unknown command '{command}'", file=sys.stderr)
        show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()