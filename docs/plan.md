## After install (important or you’ll complain later)

```bash
pip install -r requirements.txt
playwright install
```

Yes, that second line matters.

---

# 🧠 plan.md — Synkage Build Plan (Reality-Based)

This goes in repo root as `plan.md`.
Not dreamware — execution roadmap.

---

# Synkage Core — Development Plan

## Objective

Build a situation-aware execution copilot that:

* interprets intent
* decides execution strategy
* routes to correct tools or runtimes
* enforces autonomy limits
* executes with confirmation and safety

Focus on **working MVP first**, not feature fantasies.

---

## Phase 0 — Foundation (Week 1)

### Goals

* Repo initialized
* Folder structure created
* Config system working
* CLI bootable

### Tasks

* Create repo structure
* Add requirements.txt
* Implement config loader
* Implement CLI entry (`run_synkage.py`)
* Add basic logging
* Add tool_registry.json schema

**Exit criteria:** CLI starts, loads config, prints system state.

---

## Phase 1 — Brain Layer (Week 2)

### Goals

Core decision engine exists.

### Tasks

* intent_resolver.py
* prime.py skeleton
* autonomy_guard.py
* command parser
* confirmation loop
* basic command grammar rules

**Exit criteria:** system parses commands into structured intents.

---

## Phase 2 — Agent Layer (Week 3)

### Goals

Agent delegation working.

### Tasks

* base_agent.py
* planner_agent
* builder_agent
* reporter_agent
* agent task contract
* file-based agent chaining

**Exit criteria:** Prime delegates → agent returns artifact.

---

## Phase 3 — Skills System (Week 4)

### Goals

Reusable skill framework.

### Tasks

* base_skill.py
* skill registry
* permission gating
* 3–5 MVP skills:

  * summarize
  * classify intent
  * plan steps
  * draft message
  * format note

**Exit criteria:** agents invoke skills through registry.

---

## Phase 4 — Execution Routing (Week 5)

### Goals

Tasks route to correct execution backend.

### Tasks

* adapters/tool_adapter_base.py
* local_exec_adapter
* openclaw_adapter stub
* autonomy_router.py
* execution planner

**Exit criteria:** intent → adapter → execution result.

---

## Phase 5 — Tool Control (Week 6)

### Goals

Real world action begins.

### Tasks

* browser controller
* WhatsApp Web draft flow
* Gmail draft flow
* Sticky Notes integration (OS-level)
* confirmation before send

**Exit criteria:** system drafts message in real app.

---

## Phase 6 — Situation Awareness (Week 7)

### Goals

Context-sensitive behavior.

### Tasks

* activity_monitor
* time_context
* focus vs idle detection
* urgency rule engine
* autonomy threshold adjustment

**Exit criteria:** autonomy level changes with context.

---

## Phase 7 — Memory & Night Cycle (Week 8)

### Goals

Continuity and learning.

### Tasks

* user_profile.json
* relationship_state.json
* logs.json
* night_cycle.py
* pattern compression
* behavior decay

**Exit criteria:** nightly update modifies trust/maturity.

---

## Phase 8 — OpenClaw Integration (Optional)

### Goals

External runtime execution.

### Tasks

* openclaw_adapter.py
* adapter contract
* routing rules
* safety boundary enforcement

**Exit criteria:** Synkage delegates execution safely.

---

## Phase 9 — Avatar Layer (Late Stage Only)

### Locked until:

* MVP stable
* execution reliable
* autonomy guard tested

### Tasks

* Unity avatar
* emotion_axes mapping
* state_mapper
* websocket bridge

**Exit criteria:** avatar reflects state, does not control logic.

---

## MVP Definition

MVP is complete when:

* CLI works
* Intent resolution works
* Agent delegation works
* Skills execute
* Tool routing works
* Message draft automation works
* Notes saving works
* Autonomy guard enforced

No avatar. No voice. No drama.

---

## Non-Goals (Do Not Creep In Early)

* AGI features
* emotional simulation
* constant voice chat
* 3D UI
* social personality
* autonomous financial actions

---

## Success Metric

A user can say one command and:

* system understands
* chooses tool
* executes safely
* confirms result
* logs outcome

No chat. No essays. Just done.

---

If you want, next we build:

* `tool_registry.json`
* `prime.py` skeleton
* intent parser
* adapter interface
* first runnable CLI loop

Now we build, not imagine.
