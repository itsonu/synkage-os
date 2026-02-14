# Synkage Core

**Synkage** is a situation‑aware personal execution copilot designed to **act across tools and applications**, not just respond in chat.

It focuses on decision, autonomy, context awareness, and multi‑agent orchestration while delegating execution to the best available substrate (local tools, browser automation, or external agent runtimes such as OpenClaw).

> Goal: minimum talk, maximum task completion.

---

## What Synkage Is

Synkage is an **operator‑style copilot layer** that:

* Understands user intent
* Detects situational context
* Decides execution strategy
* Delegates to agents and skills
* Routes tasks to the correct execution backend
* Enforces autonomy and safety limits
* Reports results briefly and clearly

It is **not** a chatbot, prompt wrapper, or generic LLM frontend.

---

## Core Capabilities

### Action‑First Design

* Executes tasks instead of only generating responses
* Uses native apps and browser tools when appropriate
* Delegates instead of reinventing existing tools

### Situation Awareness

* Detects context states (idle, focus, urgency, emergency)
* Adjusts confirmation requirements
* Supports priority‑based behavior

### Multi‑Agent Architecture

* Prime agent for decision and delegation
* Specialist agents for planning, research, building, critique, reporting
* File‑based agent chaining

### Skill System

* Atomic, stateless capabilities
* Reusable across agents
* Permission‑gated

### Execution Routing

* Pluggable execution backends
* Local tool controllers
* Browser automation
* External agent runtimes (e.g., OpenClaw) via adapters

### Autonomy Guardrails

* Explicit autonomy levels
* Confirmation loops
* Safety‑first execution rules

### Lightweight & Modular

* CPU‑friendly
* File‑based memory
* Replaceable components
* No heavy model dependency required

---

## High‑Level Architecture

User → Signal Intake → Situation Detection → Intent Resolver → Prime Agent → Specialist Agents → Skills → Execution Adapter → Tools / Apps → Verification → Report

Key layers:

* Brain (decision & autonomy)
* Agents (specialists)
* Skills (atomic capabilities)
* Context (signal ingestion)
* Execution routing
* Tool adapters
* Memory & learning

---

## Repository Structure

```
synkage-core/
│
├── brain/         Decision, intent, situation, autonomy logic
├── agents/        Specialized task agents
├── skills/        Atomic reusable capabilities
├── adapters/      Execution backends (OpenClaw, local exec, etc.)
├── tools/         Browser & desktop controllers
├── context/       Signal and activity ingestion
├── memory/        Project and user state
├── execution/     Task planning and routing
├── avatar/        Avatar state & Unity bridge (future layer)
├── interfaces/    CLI and input interfaces
├── config/        Permissions and autonomy settings
├── docs/          Architecture and design docs
└── tests/         Unit tests
```

---

## MVP Scope

Initial milestone includes:

* Prime agent
* 2–3 specialist agents
* Intent resolution
* Skill execution framework
* Tool registry
* Browser automation for one tool
* Native note saving
* Messaging draft with confirmation
* CLI interface
* File‑based memory
* Autonomy guard

Out of MVP:

* Voice interface
* Vision input
* Continuous listening
* 3D avatar UI
* Emotional modeling
* Full situational streams

---

## Autonomy Model

Autonomy levels:

| Level | Behavior                                  |
| ----- | ----------------------------------------- |
| 0     | Observe only                              |
| 1     | Prepare actions                           |
| 2     | Execute with confirmation                 |
| 3     | Execute without confirmation (restricted) |

Never autonomous for:

* Financial actions
* Deletions
* Password operations
* Account changes
* Public posting

All autonomous actions must be explainable.

---

## Command Style

Synkage uses action‑oriented commands.

Examples:

```
send whatsapp message to Raj: I’ll call in 10 minutes
save this as a note
reply to that email about downtime
create maintenance banner 4 to 6
open vscode and search auth bug
```

Commands are resolved using context and recent activity.

---

## Installation

Requirements:

* Python 3.10+
* Windows / Linux / macOS
* Browser automation driver (Playwright or Selenium)

Setup:

```bash
git clone https://github.com/itsonu/synkage-os.git
cd synkage-core
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

Configure tools in:

```
config/tool_registry.json
config/app_preferences.yaml
```

---

## Basic Usage

Start Synkage CLI:

```bash
python scripts/run_synkage.py
```

Enter action commands. Synkage will plan, route, and execute via configured backends.

---

## OpenClaw Integration (Optional)

Synkage can use OpenClaw as an execution substrate through the adapter layer.

Synkage handles:

* intent
* situation
* autonomy
* safety

OpenClaw handles:

* agent runtime
* channel execution
* tool pipelines

Execution always remains under Synkage autonomy guard.

---

## Design Principles

* Execution > generation
* Tools > reinvention
* Context > prompts
* Transparency > magic
* Reliability > personality
* Modularity > monolith

---

## Roadmap

* Situation signal streams
* Proactive preparation mode
* Night learning cycle
* Trust & maturity model
* Parallel execution routing
* Unity avatar interface

---

## License

MIT License (recommended). Update as needed.

---

## Status

Architecture and MVP development phase.
Not production ready.
