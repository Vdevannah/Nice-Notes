def validate_title(title):
    """
    Check that a title is usable. Raises ValueError if not.
    Returns True if the title passes all checks.
    """
    if not title.strip():
        raise ValueError("Title cannot be empty")
    if len(title) > 200:
        raise ValueError("Title too long (max 200 characters)")
    return True


def is_valid_note(note):
    """
    Check whether a Note object looks valid, without raising.
    Returns True or False.
    """
    if not note.title.strip():
        return False
    if note.content is None:
        return False
    return True