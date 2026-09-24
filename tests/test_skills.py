"""ac-3: each implemented skill has passing unit tests."""

import pytest

from synkage.config import load_config
from synkage.skills.registry import SkillError, SkillRegistry

CFG = load_config()
R = SkillRegistry(CFG)


def call(name, **data):
    agent = next(a for a, skills in CFG.permissions.agent_skills.items() if name in skills)
    return R.invoke(name, agent, data)


# --- plan_steps -------------------------------------------------------------------


def test_plan_steps_message():
    out = call(
        "plan_steps",
        verb="send",
        object="message",
        target="Raj",
        content="hi",
        tool_name="WhatsApp Web",
        requires_confirmation=True,
    )
    assert out.steps == [
        "Open WhatsApp Web",
        "Find Raj",
        "Draft message: hi",
        "Ask the user to confirm",
        "Send via WhatsApp Web",
        "Verify the result",
    ]


def test_plan_steps_blocked_has_no_action_steps():
    out = call("plan_steps", verb="send", object="message", tool_name="WhatsApp Web", blocked=["no target"])
    assert out.steps == [
        "Open WhatsApp Web",
        "Find (recipient missing)",
        "Draft message (content not given yet)",
    ]


def test_plan_steps_plan_verb_skips_confirmation():
    out = call("plan_steps", verb="plan", object="launch", requires_confirmation=True)
    assert out.steps == ["Plan launch"]


def test_plan_steps_unknown_verb_is_empty():
    assert call("plan_steps", verb=None).steps == []


# --- classify_intent --------------------------------------------------------------


@pytest.mark.parametrize(
    "text, task_type, verb, confidence",
    [
        ("send whatsapp message to Raj", "messaging", "send", 1.0),
        ("reply email last thread", "email", "reply", 1.0),
        ("save this as a note", "notes", "save", 1.0),
        ("open vscode and search auth bug", "code", "open", 1.0),
        ("summarize this thread", None, "summarize", 0.5),
        ("hello there", None, None, 0.0),
    ],
)
def test_classify_intent(text, task_type, verb, confidence):
    out = call("classify_intent", text=text)
    assert (out.task_type, out.verb, out.confidence) == (task_type, verb, confidence)


def test_classify_intent_tool_beats_object_noun():
    # "gmail" (tool) wins over "message" (object noun)
    assert call("classify_intent", text="send message use gmail").task_type == "email"


def test_classify_intent_ignores_content():
    assert call("classify_intent", text="send message to Raj: check the email").task_type == "messaging"


# --- format_note ------------------------------------------------------------------


def test_format_note_single_item():
    out = call("format_note", text="  meeting   at 4pm with the design team about launch  ")
    assert out.title == "Meeting at 4pm with the design…"
    assert out.items == ["Meeting at 4pm with the design team about launch"]
    assert (
        out.markdown
        == "# Meeting at 4pm with the design…\n\nMeeting at 4pm with the design team about launch\n"
    )


def test_format_note_multiple_items_become_bullets():
    out = call("format_note", text="buy milk; call  mom\nfix auth bug")
    assert out.items == ["Buy milk", "Call mom", "Fix auth bug"]
    assert out.title == "Note (3 items)"
    assert out.markdown == "# Note (3 items)\n\n- Buy milk\n- Call mom\n- Fix auth bug\n"


def test_format_note_explicit_title():
    assert call("format_note", text="a; b", title="groceries").title == "Groceries"


def test_format_note_rejects_blank():
    with pytest.raises(SkillError, match="invalid input"):
        call("format_note", text="   ")


# --- statelessness ----------------------------------------------------------------


def test_each_call_gets_a_fresh_instance(monkeypatch):
    from synkage.skills.text.format_note import FormatNoteSkill

    constructed = []
    original = FormatNoteSkill.__init__

    def counting_init(self, config):
        constructed.append(self)
        original(self, config)

    monkeypatch.setattr(FormatNoteSkill, "__init__", counting_init)
    call("format_note", text="a")
    call("format_note", text="b")
    assert len(constructed) == 2 and constructed[0] is not constructed[1]
