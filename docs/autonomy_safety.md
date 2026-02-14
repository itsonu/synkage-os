# Autonomy & Safety Model

## Goal

Allow Synkage to execute useful actions automatically while preventing risky or irreversible operations without user consent.

Autonomy is bounded, explainable, and reversible where possible.

---

## Autonomy Levels

| Level | Behavior                  |
| ----- | ------------------------- |
| 0     | Observe only              |
| 1     | Plan only                 |
| 2     | Execute with confirmation |
| 3     | Limited auto-execute      |

Default = Level 2.

---

## Autonomy Inputs

Autonomy level is derived from:

- intent confidence
- situation state
- task risk class
- tool sensitivity
- user trust score

---

## Risk Classes

| Class    | Examples                      |
| -------- | ----------------------------- |
| Low      | notes, formatting, summaries  |
| Medium   | sending messages, replies     |
| High     | account actions, purchases    |
| Critical | financial, security, deletion |

High and Critical always require confirmation.

---

## Hard Safety Rules

Never autonomous:

- payments
- account changes
- password handling
- public posting
- destructive file ops
- system config changes

---

## Confirmation Loop

For gated actions:

1. show plan
2. show tool target
3. require explicit confirm
4. execute
5. log result

---

## Rollback Support

Where supported:

- message draft undo
- file restore
- staged execution
- dry-run preview

---

## Audit

All executions are logged with:

- intent
- tool
- autonomy level
- confirmation state
- result
