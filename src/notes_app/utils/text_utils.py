
import re


def sanitize_title_for_filename(title):
    """Strip special characters, replace spaces with dashes, lowercase."""
    safe_title = re.sub(r"[^a-zA-Z0-9\s]", "", title)
    safe_title = safe_title.replace(" ", "-")
    safe_title = safe_title.lower()
    return safe_title