"""Intent resolver: turns a command string into a structured Intent.

Grammar (docs/command_grammar.md): <action> <object> [target] [options]

    send whatsapp message to Raj: I'll call in 10 minutes
    ^verb ^tool    ^object    ^target ^content

Rule-based and deterministic. Options (tool directives, autonomy modifiers, agent
directives) are stripped first, wherever they appear. Anything the parser can't
pin down is recorded in `unclear` and forces preview mode — it never guesses.
"""

from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field
from rapidfuzz import process

from synkage.config import SynkageConfig

DETERMINERS = {"a", "an", "the", "this", "that", "these", "those", "my", "our"}


class Mode(str, Enum):
    execute = "execute"  # may run (autonomy guard still decides on confirmation)
    preview = "preview"  # show the plan only
    dry_run = "dry_run"  # simulate without side effects


class ToolSource(str, Enum):
    directive = "directive"  # "use gmail"
    mention = "mention"  # "send whatsapp message"
    preference = "preference"  # object type -> app_preferences.yaml


class Intent(BaseModel):
    raw: str
    verb: str | None = None
    object: str | None = None
    target: str | None = None
    details: str | None = None
    content: str | None = None
    tool: str | None = None
    tool_source: ToolSource | None = None
    modifier: str | None = None
    agent_directive: str | None = None
    mode: Mode = Mode.execute
    unclear: list[str] = Field(default_factory=list)


def _find_phrase(text: str, phrases: list[str]) -> tuple[str, re.Match[str]] | None:
    """First whole-word, case-insensitive match; longer phrases win."""
    for phrase in sorted(phrases, key=len, reverse=True):
        m = re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text, re.IGNORECASE)
        if m:
            return phrase, m
    return None


def _cut(text: str, m: re.Match[str]) -> str:
    return " ".join((text[: m.start()] + " " + text[m.end() :]).split())


def _strip_determiners(words: list[str]) -> list[str]:
    while words and words[0].lower() in DETERMINERS:
        words = words[1:]
    return words


class IntentResolver:
    def __init__(self, config: SynkageConfig):
        self.cfg = config
        self.cmd = config.commands

    def resolve(self, text: str) -> Intent:
        intent = Intent(raw=text)
        head, _, content = text.partition(":")
        intent.content = content.strip() or None
        head = " ".join(head.split())

        head = self._take_options(head, intent)

        words = head.split()
        if not words:
            intent.unclear.append("no action given")
            return self._finish(intent)

        verb, rest = words[0].lower(), words[1:]
        if verb not in self.cmd.verbs:
            suggestion = process.extractOne(verb, list(self.cmd.verbs), score_cutoff=75)
            hint = f" (did you mean '{suggestion[0]}'?)" if suggestion else ""
            intent.unclear.append(f"unknown action '{words[0]}'{hint}")
            return self._finish(intent)
        intent.verb = verb

        rest = self._take_tool_mention(" ".join(rest), intent)
        self._split_object_target(rest, intent)
        self._resolve_tool_from_preference(intent)
        return self._finish(intent)

    # --- steps --------------------------------------------------------------

    def _take_options(self, head: str, intent: Intent) -> str:
        modifiers = []
        while found := _find_phrase(head, list(self.cmd.autonomy_modifiers)):
            modifiers.append(self.cmd.autonomy_modifiers[found[0]])
            head = _cut(head, found[1])
        if len(set(modifiers)) > 1:
            intent.unclear.append(f"conflicting autonomy modifiers: {', '.join(modifiers)}")
        if modifiers:
            intent.modifier = modifiers[0]

        if found := _find_phrase(head, self.cmd.agent_directives):
            intent.agent_directive = found[0]
            head = _cut(head, found[1])
        # "use <directive>" — also catches unknown directives so they can't be ignored.
        m = re.search(r"(?<!\w)use\s+(.+?)\s*$", head, re.IGNORECASE)
        if m:
            found = _find_phrase(m.group(1), list(self.cmd.tool_directives))
            if found and found[1].start() == 0:
                phrase, pm = found
                intent.tool = self.cmd.tool_directives[phrase]
                intent.tool_source = ToolSource.directive
                leftover = m.group(1)[pm.end() :]
                head = (head[: m.start()] + " " + leftover).strip()
            else:
                intent.unclear.append(f"unknown tool '{m.group(1)}'")
                head = head[: m.start()].strip()

        return head

    def _take_tool_mention(self, rest: str, intent: Intent) -> str:
        found = _find_phrase(rest, list(self.cmd.tool_directives))
        if not found:
            return rest
        phrase, m = found
        if intent.tool is None:
            intent.tool = self.cmd.tool_directives[phrase]
            intent.tool_source = ToolSource.mention
        if intent.verb == "open":  # "open vscode ..." — the tool is the object; keep it
            return rest
        before = rest[: m.start()].split()
        if before and before[-1].lower() in {"on", "via", "in", "with", "using"}:
            before = before[:-1]  # "to Raj on whatsapp" -> drop "on" too
        return " ".join(before + rest[m.end() :].split()) or rest

    def _split_object_target(self, rest: str, intent: Intent) -> None:
        rule = self.cmd.verbs[intent.verb]
        words = rest.split()
        if rule.needs_target:
            if words and words[0].lower() == "to":  # "reply to that email ..."
                words = words[1:]
            lowered = [w.lower() for w in words]
            if "to" in lowered:
                i = lowered.index("to")
                obj, tgt = words[:i], words[i + 1 :]
            else:  # "reply email last thread" -> object email, target "last thread"
                stripped = _strip_determiners(words)
                obj, tgt = stripped[:1], stripped[1:]
            obj = _strip_determiners(obj)
            intent.object = " ".join(obj) or None
            intent.target = " ".join(tgt) or None
            if intent.target is None:
                intent.unclear.append(f"'{intent.verb}' needs a target (e.g. '{intent.verb} message to Raj')")
        else:
            lowered = [w.lower() for w in words]
            if "as" in lowered:  # "save this as a note"
                i = lowered.index("as")
                intent.details = " ".join(words[:i]) or None
                words = words[i + 1 :]
            elif words and words[0].lower() in {"and", "then"}:
                words = words[1:]
            words = _strip_determiners(words)
            if intent.tool_source == ToolSource.mention and intent.verb == "open":
                # "open vscode and search auth bug" -> object vscode, details the rest
                intent.object = words[0] if words else None
                tail = words[1:]
                if tail and tail[0].lower() in {"and", "then"}:
                    tail = tail[1:]
                intent.details = " ".join(tail) or intent.details
            elif words and words[0].lower() in self.cmd.object_types:
                # "save note meeting at 4pm" -> object note, details the rest
                intent.object = words[0]
                intent.details = " ".join(words[1:]) or intent.details
            else:
                intent.object = " ".join(words) or None
        if intent.object is None and rule.needs_tool and intent.tool is None:
            intent.unclear.append(f"'{intent.verb}' needs an object")

    def _resolve_tool_from_preference(self, intent: Intent) -> None:
        if intent.tool or not intent.object:
            return
        if any(u.startswith("unknown tool") for u in intent.unclear):
            return  # the user named a tool we don't have; don't swap in another
        for word in intent.object.lower().split():
            task = self.cmd.object_types.get(word)
            tool = self.cfg.preferences.preferred_tools.get(task) if task else None
            if tool:
                intent.tool = tool
                intent.tool_source = ToolSource.preference
                return

    def _finish(self, intent: Intent) -> Intent:
        named_unknown = any(u.startswith("unknown tool") for u in intent.unclear)
        if (
            intent.verb
            and self.cmd.verbs[intent.verb].needs_tool
            and intent.tool is None
            and not named_unknown
        ):
            intent.unclear.append(f"no tool for '{intent.verb}' (add 'use <tool>')")
        if intent.unclear or intent.modifier == "preview":
            intent.mode = Mode.preview
        elif intent.modifier == "dry_run":
            intent.mode = Mode.dry_run
        return intent
