"""classify_intent: which task type a piece of text is about (messaging, email,
notes, code, web), from the command vocabulary. Rule-based, no model.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from synkage.skills.base_skill import BaseSkill


class ClassifyIntentInput(BaseModel):
    text: str


class ClassifyIntentOutput(BaseModel):
    task_type: str | None
    verb: str | None
    signals: list[str] = Field(default_factory=list)  # words that decided it
    confidence: float  # share of the two signals (verb, task type) that were found


class ClassifyIntentSkill(BaseSkill):
    name = "classify_intent"
    description = "Task type (messaging, email, notes, code, web) and verb of a text."
    Input = ClassifyIntentInput
    Output = ClassifyIntentOutput

    def run(self, data: ClassifyIntentInput) -> ClassifyIntentOutput:
        cmd = self.config.commands
        text = data.text.split(":", 1)[0].lower()  # ignore message content
        words = re.findall(r"[a-z0-9']+", text)
        verb = words[0] if words and words[0] in cmd.verbs else None

        task_type, signals = None, []
        tool_task = {tool: task for task, tool in self.config.preferences.preferred_tools.items()}
        for phrase, tool_id in sorted(cmd.tool_directives.items(), key=lambda kv: -len(kv[0])):
            if re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text) and tool_id in tool_task:
                task_type, signals = tool_task[tool_id], [phrase]
                break
        if task_type is None:
            for w in words:
                if w in cmd.object_types:
                    task_type, signals = cmd.object_types[w], [w]
                    break
        if verb:
            signals.insert(0, verb)
        found = (verb is not None) + (task_type is not None)
        return ClassifyIntentOutput(task_type=task_type, verb=verb, signals=signals, confidence=found / 2)
