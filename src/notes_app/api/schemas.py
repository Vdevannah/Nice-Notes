from datetime import datetime

from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: str = ""
    author: str = "unknown"
    tags: list[str] = []


class NoteUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    content: str | None = None
    tags: list[str] | None = None


class NoteResponse(BaseModel):
    filename: str
    title: str
    author: str
    content: str
    tags: list[str]
    created: datetime
    modified: datetime


class NoteSummary(BaseModel):
    filename: str
    title: str
    modified: datetime
    tags: list[str]
