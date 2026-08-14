from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from src.notes_app.api.schemas import NoteCreate, NoteResponse, NoteSummary, NoteUpdate
from src.notes_app.config.paths import (
    build_note_file_path,
    ensure_notes_directory_exists,
    get_absolute_path_to_notes_home,
)
from src.notes_app.notes.models import Note
from src.notes_app.notes.storage import (
    delete_note,
    filter_notes_by_tag,
    get_all_tags,
    list_all_notes,
    load_note,
    save_note,
    search_notes_by_keyword,
)
from src.notes_app.notes.storage import update_note as _update_note


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_notes_directory_exists()
    yield


app = FastAPI(title="Nice Notes API", lifespan=lifespan)


def _safe_filename(filename: str) -> str:
    """Reject filenames that could escape the notes directory."""
    if "/" in filename or filename in (".", ".."):
        raise HTTPException(status_code=400, detail="Invalid filename")
    return filename


def _note_to_response(path, note) -> NoteResponse:
    return NoteResponse(
        filename=path.name,
        title=note.title,
        author=note.author,
        content=note.content,
        tags=note.tags,
        created=note.created,
        modified=note.modified,
    )


def _note_to_summary(path, note) -> NoteSummary:
    return NoteSummary(
        filename=path.name,
        title=note.title,
        modified=note.modified,
        tags=note.tags,
    )


@app.post("/notes", response_model=NoteResponse, status_code=201)
def create_note_route(payload: NoteCreate):
    try:
        note = Note(payload.title, payload.author, content=payload.content, tags=payload.tags)
        path = save_note(note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _note_to_response(path, note)


@app.get("/notes", response_model=list[NoteSummary])
def list_notes_route(tag: str | None = None, q: str | None = None):
    base_dir = get_absolute_path_to_notes_home()
    if q is not None:
        results = search_notes_by_keyword(base_dir, q)
    elif tag is not None:
        results = filter_notes_by_tag(base_dir, tag)
    else:
        results = list_all_notes(base_dir)
    return [_note_to_summary(path, note) for path, note in results]


@app.get("/notes/{filename}", response_model=NoteResponse)
def read_note_route(filename: str):
    filename = _safe_filename(filename)
    path = build_note_file_path(filename)
    try:
        note = load_note(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _note_to_response(path, note)


@app.patch("/notes/{filename}", response_model=NoteResponse)
def update_note_route(filename: str, payload: NoteUpdate):
    filename = _safe_filename(filename)
    path = build_note_file_path(filename)
    try:
        note = _update_note(
            path,
            title=payload.title,
            author=payload.author,
            content=payload.content,
            tags=payload.tags,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _note_to_response(path, note)


@app.delete("/notes/{filename}", status_code=204)
def delete_note_route(filename: str):
    filename = _safe_filename(filename)
    path = build_note_file_path(filename)
    if not delete_note(path):
        raise HTTPException(status_code=404, detail=f"Note file not found: {path}")


@app.get("/tags", response_model=list[str])
def list_tags_route():
    base_dir = get_absolute_path_to_notes_home()
    return get_all_tags(base_dir)
