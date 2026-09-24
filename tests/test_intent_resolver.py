import pytest

from synkage.brain.intent_resolver import IntentResolver, Mode, ToolSource
from synkage.config import load_config


@pytest.fixture(scope="module")
def resolve():
    return IntentResolver(load_config()).resolve


# --- ac-1: <action> <object> [target] -----------------------------------------


def test_send_message_to_rahul(resolve):
    i = resolve("send message to Rahul")
    assert (i.verb, i.object, i.target) == ("send", "message", "Rahul")
    assert i.mode == Mode.execute
    assert i.unclear == []


def test_content_after_colon_and_inline_tool(resolve):
    i = resolve("send whatsapp message to Raj: I'll call in 10 minutes")
    assert (i.verb, i.object, i.target) == ("send", "message", "Raj")
    assert i.content == "I'll call in 10 minutes"
    assert (i.tool, i.tool_source) == ("whatsapp_web", ToolSource.mention)


def test_verb_is_case_insensitive(resolve):
    i = resolve("SEND message TO Rahul")
    assert (i.verb, i.target) == ("send", "Rahul")


@pytest.mark.parametrize(
    "command, verb, obj, target, details, tool",
    [
        ("reply email last thread", "reply", "email", "last thread", None, "gmail"),
        ("reply to that email about downtime", "reply", "email", "about downtime", None, "gmail"),
        ("save this as a note", "save", "note", None, "this", "apple_notes"),
        ("save note meeting at 4pm", "save", "note", None, "meeting at 4pm", "apple_notes"),
        ("open vscode and search auth bug", "open", "vscode", None, "search auth bug", "vscode"),
        (
            "create image maintenance banner use browser",
            "create",
            "image maintenance banner",
            None,
            None,
            "browser",
        ),
        ("summarize this thread", "summarize", "thread", None, None, None),
    ],
)
def test_documented_examples(resolve, command, verb, obj, target, details, tool):
    i = resolve(command)
    assert (i.verb, i.object, i.target, i.details, i.tool) == (verb, obj, target, details, tool)
    assert i.mode == Mode.execute, i.unclear


def test_preferred_tool_used_when_none_named(resolve):
    i = resolve("send message to Rahul")
    assert (i.tool, i.tool_source) == ("whatsapp_web", ToolSource.preference)


# --- ac-2: tool directives and autonomy modifiers ------------------------------


def test_use_gmail_directive(resolve):
    i = resolve("send message to Rahul use gmail")
    assert (i.tool, i.tool_source) == ("gmail", ToolSource.directive)
    assert i.target == "Rahul"


def test_directive_beats_inline_mention(resolve):
    assert resolve("send whatsapp message to Raj use gmail").tool == "gmail"


@pytest.mark.parametrize(
    "phrase, modifier, mode",
    [
        ("dry run", "dry_run", Mode.dry_run),
        ("preview only", "preview", Mode.preview),
        ("ask before send", "confirm", Mode.execute),
        ("auto execute", "auto", Mode.execute),
    ],
)
def test_autonomy_modifiers(resolve, phrase, modifier, mode):
    i = resolve(f"send message to Rahul {phrase}")
    assert (i.modifier, i.mode, i.target) == (modifier, mode, "Rahul")


def test_modifier_and_directive_together(resolve):
    i = resolve("send message to Rahul use gmail dry run")
    assert (i.tool, i.modifier, i.target) == ("gmail", "dry_run", "Rahul")


def test_agent_directive(resolve):
    i = resolve("plan then execute summarize doc")
    assert (i.agent_directive, i.verb, i.object) == ("plan then execute", "summarize", "doc")


# --- ac-3: unclear -> preview ---------------------------------------------------


@pytest.mark.parametrize(
    "command, reason",
    [
        ("send message", "needs a target"),
        ("create maintenance banner 4 to 6", "no tool for 'create'"),
        ("send message to Raj use telegram", "unknown tool 'telegram'"),
        ("snd message to Raj", "did you mean 'send'"),
        ("", "no action given"),
        ("send message to Raj dry run auto execute", "conflicting autonomy modifiers"),
    ],
)
def test_unclear_commands_go_to_preview(resolve, command, reason):
    i = resolve(command)
    assert i.mode == Mode.preview
    assert any(reason in u for u in i.unclear), i.unclear


def test_unknown_tool_is_not_replaced_by_preference(resolve):
    assert resolve("send message to Raj use telegram").tool is None


def test_modifier_after_unknown_tool_does_not_hide_it(resolve):
    i = resolve("send message to Raj use telegram dry run")
    assert i.mode == Mode.preview
    assert i.target == "Raj"
    assert any("unknown tool 'telegram'" in u for u in i.unclear)


def test_preposition_before_inline_tool_is_dropped(resolve):
    i = resolve("send message to Raj on whatsapp")
    assert (i.target, i.tool) == ("Raj", "whatsapp_web")


def test_options_inside_content_are_ignored(resolve):
    i = resolve("send message to Raj: please use gmail and auto execute")
    assert i.modifier is None
    assert i.tool_source == ToolSource.preference
    assert i.content == "please use gmail and auto execute"


@pytest.mark.parametrize("phrase", ["dry run", "preview only", "ask before send"])
def test_safer_modifier_at_end_of_content_forces_preview(resolve, phrase):
    i = resolve(f"send message to Raj: hi {phrase}")
    assert i.mode == Mode.preview
    assert any("put options before ':'" in u for u in i.unclear)


def test_modifier_in_middle_of_content_is_just_text(resolve):
    i = resolve("send message to Raj: can we do a dry run tomorrow")
    assert i.mode == Mode.execute and i.unclear == []


def test_auto_execute_in_content_is_ignored_not_previewed(resolve):
    i = resolve("send message to Raj: hi auto execute")
    assert (i.mode, i.modifier, i.unclear) == (Mode.execute, None, [])
