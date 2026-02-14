# Synkage Core — System Architecture

## Overview

Synkage is a **situation-aware execution copilot architecture** designed to coordinate tasks across tools, applications, and agent runtimes. Unlike chat-first assistants, Synkage is built around **decision, delegation, and execution**, with strict autonomy and safety controls.

The system separates **decision intelligence** from **execution substrates**, allowing Synkage to operate as a meta-orchestrator over local tools, browser automation, and optional external agent runtimes.

Primary design goal:

> Interpret intent → choose strategy → execute safely → report briefly.

---

## Design Principles

- Execution over conversation
- Decision layer separated from execution layer
- Situation awareness before autonomy
- Tools preferred over reinvention
- Safety gates before automation
- Modular and replaceable components
- CPU-friendly and local-first
- Adapter-based external integration

---

## Layered Architecture

Synkage uses a layered architecture with strict responsibility boundaries.

```
User Interface Layer
↓
Signal & Context Layer
↓
Brain Layer (Decision & Autonomy)
↓
Agent Layer (Specialists)
↓
Skill Layer (Atomic Capabilities)
↓
Execution Routing Layer
↓
Execution Adapters
↓
Tool / Runtime Layer
```

---

## Layer Descriptions

### User Interface Layer

Responsible for input and output.

Examples:

- CLI interface
- Hotkeys
- Voice stub (future)
- Avatar interface (future)

Responsibilities:

- Capture commands
- Display results
- Trigger confirmation flows

No decision logic lives here.

---

### Signal & Context Layer

Collects environmental and activity signals.

Components:

- Activity monitor
- App context reader
- Time context
- Signal ingestion

Responsibilities:

- Detect user activity patterns
- Provide context signals to brain layer
- Support situation classification

Outputs structured context signals.

---

### Brain Layer

Core decision engine.

Components:

- Prime agent
- Intent resolver
- Situation detector
- Priority resolver
- Autonomy guard
- Verifier

Responsibilities:

- Interpret user intent
- Classify situation state
- Decide autonomy level
- Select execution strategy
- Delegate to agents
- Enforce safety rules

This layer never directly executes tools.

---

### Agent Layer

Specialized reasoning workers.

Examples:

- Planner agent
- Researcher agent
- Builder agent
- Critic agent
- Reporter agent

Responsibilities:

- Perform specialized reasoning tasks
- Generate structured artifacts
- Chain tasks through files
- Invoke skills

Agents do not control tools directly.

---

### Skill Layer

Atomic, stateless capabilities.

Examples:

- Summarize text
- Plan steps
- Classify intent
- Draft message
- Critique output

Characteristics:

- Stateless
- Reusable
- Permission-gated
- Agent-invoked only

Skills are building blocks, not decision makers.

---

### Execution Routing Layer

Routes tasks to appropriate execution backend.

Components:

- Action planner
- Autonomy router
- Confirmation loop
- Rollback handler

Responsibilities:

- Map task → execution adapter
- Apply autonomy thresholds
- Trigger confirmation flows
- Support undo operations

This layer enforces autonomy policy.

---

### Execution Adapter Layer

Provides integration with execution substrates.

Examples:

- Local execution adapter
- Browser tool adapter
- OpenClaw adapter
- Future runtime adapters

Responsibilities:

- Translate tasks into backend calls
- Normalize execution results
- Enforce safety boundaries

Adapters are replaceable.

---

### Tool / Runtime Layer

Actual execution targets.

Examples:

- Browser automation tools
- Native desktop apps
- Messaging platforms
- IDE controllers
- External agent runtimes (OpenClaw)

Responsibilities:

- Perform real-world actions
- Return execution results

No decision logic exists here.

---

## Situation Awareness Model

Synkage uses rule-based situation classification.

Situation states include:

- Idle
- Normal
- Focused
- Urgent
- Emergency

Situation affects:

- Autonomy thresholds
- Confirmation requirements
- Execution speed
- Interruption policy

Situation detection is signal-driven, not model-driven.

---

## Autonomy Model

Autonomy is explicit and bounded.

Levels:

| Level | Behavior                                  |
| ----- | ----------------------------------------- |
| 0     | Observe only                              |
| 1     | Prepare actions                           |
| 2     | Execute with confirmation                 |
| 3     | Execute without confirmation (restricted) |

Autonomy is determined by:

- Situation state
- Confidence score
- Task risk level
- User trust level
- Safety rules

Certain actions are never autonomous.

---

## Execution Strategy Selection

Execution strategy is chosen based on:

- Task type
- Required tool
- Available backend
- Subscription/tool access
- Risk classification

Possible strategies:

- Local tool execution
- Browser automation
- External runtime delegation
- Guided fallback mode

Strategy is selected by brain layer and enforced by router.

---

## Memory & Learning

Synkage uses structured local memory.

Stores:

- Project memory
- User profile
- Relationship state
- Interaction logs
- Night cycle updates

Night cycle tasks:

- Log compression
- Pattern promotion
- Trust adjustment
- Behavior decay

Memory influences autonomy and personalization.

---

## External Runtime Integration

Synkage supports optional integration with external agent runtimes such as OpenClaw.

Integration rules:

- External runtime handles execution pipelines
- Synkage retains intent, autonomy, and safety control
- External runtime cannot bypass autonomy guard
- All results pass through verification layer

External runtimes are execution substrates, not decision authorities.

---

## Avatar Layer (Future)

Avatar layer is strictly presentation.

Components:

- Emotion axes
- State mapper
- Unity bridge

Responsibilities:

- Reflect system state visually
- Convey status through expression
- Provide optional voice feedback

Avatar never performs decision or execution.

---

## Safety Boundaries

Synkage enforces hard safety limits:

Never autonomous:

- Financial operations
- Account changes
- Password handling
- Public posting
- Destructive actions

All autonomous actions must be explainable and logged.

---

## Summary

Synkage architecture separates:

- Decision from execution
- Context from action
- Intelligence from tools
- Presentation from logic

This separation enables:

- modularity
- safety
- extensibility
- runtime flexibility
- reliable execution behavior

Synkage acts as a **meta-orchestrator**, coordinating agents and tools to complete tasks safely and efficiently.
