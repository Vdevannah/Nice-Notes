import os
from pathlib import Path

DEFAULT_NOTES_HOME = Path.home() / ".notes"


def get_notes_home_directory():
    """Return the directory where notes should be stored."""
    if "NOTES_HOME" in os.environ:
        return Path(os.environ["NOTES_HOME"])
    return DEFAULT_NOTES_HOME


def ensure_notes_directory_exists():
    """Make sure the notes directory exists on disk, creating it if needed."""
    notes_home = get_notes_home_directory()
    (notes_home / "notes").mkdir(parents=True, exist_ok=True)
    return notes_home

def get_absolute_path_to_notes_home():
    """Return the notes home directory as a fully resolved absolute path."""
    notes_home = get_notes_home_directory()
    return notes_home.resolve()


def build_note_file_path(note_filename):
    """Return the full path to a specific note file, given just its filename."""
    notes_home = get_absolute_path_to_notes_home()
    return notes_home / "notes" / note_filename