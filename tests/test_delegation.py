"""ac-3 (file chaining) and ac-4 (Prime.delegate picks agents, returns artifact path)."""

import pytest

from synkage.agents import registry
from synkage.agents.base_agent import BaseAgent, TaskStatus, read_artifact
from synkage.brain.prime import FULL_CHAIN, PLAN_CHAIN, Prime, select_chain
from synkage.config import load_config


@pytest.fixture
def prime(runs_dir):
    return Prime(load_config(), runs_dir=runs_dir)


def test_full_chain_passes_artifacts_through_files(prime):
    d = prime.delegate(prime.handle("send message to Rahul: running late"))
    assert d.ok and d.chain == FULL_CHAIN
    plan, draft, report = (d.run_dir / f"{n:02d}-{a}.json" for n, a in enumerate(FULL_CHAIN, 1))
    assert all(p.is_file() for p in (plan, draft, report))
    assert read_artifact(plan).inputs == []
    assert read_artifact(draft).inputs == [str(plan)]
    assert read_artifact(report).inputs == [str(plan), str(draft)]
    # the builder's steps come from the planner's file
    assert read_artifact(draft).body["steps"] == read_artifact(plan).body["steps"]


def test_delegate_returns_last_artifact_path(prime):
    d = prime.delegate(prime.handle("send message to Rahul"))
    assert d.artifact == d.run_dir / "03-reporter.json"
    assert read_artifact(d.artifact).kind == "report"


@pytest.mark.parametrize(
    "command, chain",
    [
        ("send message to Rahul", FULL_CHAIN),
        ("save note meeting at 4pm", FULL_CHAIN),
        ("send message", PLAN_CHAIN),  # preview
        ("send message to Rahul dry run", FULL_CHAIN),
        ("send message to Rahul preview only", PLAN_CHAIN),
        ("plan launch checklist", PLAN_CHAIN),
        ("snd message to Raj", PLAN_CHAIN),  # unknown verb
    ],
)
def test_select_chain(prime, command, chain):
    r = prime.handle(command)
    assert select_chain(r.intent, r.decision)[0] == chain


def test_level_0_runs_no_agents(prime):
    r = prime.handle("send message to Rahul")
    r.decision.level = 0
    d = prime.delegate(r)
    assert (d.chain, d.results, d.run_dir, d.artifact) == ([], [], None, None)
    assert not prime.runs_dir.exists()


def test_research_directive_notes_missing_researcher(prime):
    d = prime.delegate(prime.handle("research then write summarize market"))
    assert d.chain == FULL_CHAIN
    assert any("researcher" in n for n in d.notes)


class FailingBuilder(BaseAgent):
    name = "builder"
    kind = "action_draft"

    def produce(self, task, inputs):
        raise ValueError("cannot build")


def test_chain_stops_at_first_failure(prime, monkeypatch):
    monkeypatch.setitem(registry.AGENTS, "builder", FailingBuilder)
    d = prime.delegate(prime.handle("send message to Rahul"))
    assert [r.agent for r in d.results] == ["planner", "builder"]
    assert d.results[-1].status == TaskStatus.failed
    assert not d.ok and d.artifact is None
    assert not (d.run_dir / "03-reporter.json").exists()


def test_each_command_gets_its_own_run_dir(prime):
    r = prime.handle("send message to Rahul")
    assert prime.delegate(r).run_dir != prime.delegate(r).run_dir
