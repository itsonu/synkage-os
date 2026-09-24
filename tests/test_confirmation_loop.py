import pytest

from synkage.execution.confirmation_loop import confirm


def run(answer):
    shown = []

    def ask(prompt):
        shown.append(prompt)
        if isinstance(answer, BaseException):
            raise answer
        return answer

    return confirm("send message to Rahul", "WhatsApp Web (whatsapp_web)", ask, shown.append), shown


@pytest.mark.parametrize("answer", ["yes", "YES", "  yes  "])
def test_explicit_yes_confirms(answer):
    result, _ = run(answer)
    assert result.confirmed


@pytest.mark.parametrize("answer", ["no", "", "y", "yeah", "yes please", "ok"])
def test_anything_else_cancels(answer):
    result, _ = run(answer)
    assert not result.confirmed
    assert result.answer == answer


@pytest.mark.parametrize("exc", [EOFError(), KeyboardInterrupt()])
def test_eof_and_ctrl_c_cancel(exc):
    result, _ = run(exc)
    assert (result.confirmed, result.answer) == (False, None)


def test_plan_and_tool_shown_before_asking():
    _, shown = run("no")
    assert shown[0] == "Plan: send message to Rahul"
    assert shown[1] == "Tool: WhatsApp Web (whatsapp_web)"
    assert "yes" in shown[2]
