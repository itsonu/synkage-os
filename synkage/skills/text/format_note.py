"""format_note: tidy free text into a titled Markdown note.

Rules: collapse whitespace; split items on newlines or ';' (2+ items -> bullets).
Title: explicit title; else for one item its first 6 words; else "Note (N items)"
(using the first item would just repeat it as a bullet).
"""

from __future__ import annotations

import re

from pydantic import BaseModel, field_validator

from synkage.skills.base_skill import BaseSkill

TITLE_WORDS = 6


class FormatNoteInput(BaseModel):
    text: str
    title: str | None = None

    @field_validator("text")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("note text is empty")
        return v


class FormatNoteOutput(BaseModel):
    title: str
    items: list[str]
    markdown: str


def _clean(s: str) -> str:
    s = " ".join(s.split())
    return s[:1].upper() + s[1:]


class FormatNoteSkill(BaseSkill):
    name = "format_note"
    description = "Tidy free text into a titled Markdown note (bullets for multiple items)."
    Input = FormatNoteInput
    Output = FormatNoteOutput

    def run(self, data: FormatNoteInput) -> FormatNoteOutput:
        items = [_clean(p) for p in re.split(r"[;\n]", data.text) if p.strip()]
        if data.title and data.title.strip():
            title = _clean(data.title)
        elif len(items) > 1:
            title = f"Note ({len(items)} items)"
        else:
            words = items[0].split()
            title = " ".join(words[:TITLE_WORDS]) + ("…" if len(words) > TITLE_WORDS else "")
        body = "\n".join(f"- {i}" for i in items) if len(items) > 1 else items[0]
        return FormatNoteOutput(title=title, items=items, markdown=f"# {title}\n\n{body}\n")
