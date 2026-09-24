"""ac-1: base_agent defines a typed task contract (input, output artifact path, status)."""

from pathlib import Path

import pytest
from agent_helpers import CFG, make_task
from pydantic import ValidationError

from synkage.agents.base_agent import (
    AgentTask,
    Artifact,
    BaseAgent,
    TaskStatus,
    read_artifact,
)


class EchoAgent(BaseAgent):
    name = "echo"
    kind = "echo"

    def produce(self, task, inputs):
        return f"echo of {len(inputs)} input(s)", {"seen": [a.summary for a in inputs]}


class BrokenAgent(BaseAgent):
    name = "broken"
    kind = "none"

    def produce(self, task, inputs):
        raise RuntimeError("boom")


def test_task_requires_output_path():
    base = make_task("echo", "send message to Rahul", out=Path("x"))
    data = base.model_dump()
    del data["output"]
    with pytest.raises(ValidationError, match="output"):
        AgentTask.model_validate(data)


def test_agent_writes_artifact_to_task_output(tmp_path):
    out = tmp_path / "run" / "01-echo.json"
    result = EchoAgent(CFG).run(make_task("echo", "send message to Rahul", out))
    assert result.status == TaskStatus.done
    assert result.output == out and result.error is None
    art = read_artifact(out)
    assert (art.agent, art.kind, art.task_id, art.inputs) == ("echo", "echo", "t/echo", [])
    assert not list(out.parent.glob("*.tmp"))


def test_agent_reads_inputs_from_files(tmp_path):
    first = tmp_path / "01.json"
    EchoAgent(CFG).run(make_task("echo", "send message to Rahul", first))
    second = tmp_path / "02.json"
    EchoAgent(CFG).run(make_task("echo", "send message to Rahul", second, inputs=[first]))
    art = read_artifact(second)
    assert art.inputs == [str(first)]
    assert art.body["seen"] == ["echo of 0 input(s)"]


def test_wrong_agent_fails(tmp_path):
    result = EchoAgent(CFG).run(make_task("planner", "send message to Rahul", tmp_path / "o.json"))
    assert result.status == TaskStatus.failed
    assert "not 'echo'" in result.error


def test_missing_input_fails_without_output(tmp_path):
    out = tmp_path / "o.json"
    task = make_task("echo", "send message to Rahul", out, inputs=[tmp_path / "nope.json"])
    result = EchoAgent(CFG).run(task)
    assert result.status == TaskStatus.failed
    assert "missing input artifact" in result.error
    assert not out.exists()


def test_invalid_input_fails(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"agent": "x"}')
    result = EchoAgent(CFG).run(make_task("echo", "send message to Rahul", tmp_path / "o.json", inputs=[bad]))
    assert result.status == TaskStatus.failed
    assert "invalid input artifact" in result.error


def test_agent_exception_becomes_failed_result(tmp_path):
    out = tmp_path / "o.json"
    result = BrokenAgent(CFG).run(make_task("broken", "send message to Rahul", out))
    assert result.status == TaskStatus.failed
    assert result.error == "RuntimeError: boom"
    assert not out.exists()


def test_artifact_round_trips():
    fields = Artifact.model_fields
    assert {"agent", "kind", "task_id", "created", "inputs", "summary", "body"} <= set(fields)
