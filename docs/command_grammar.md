# Command Grammar

## Philosophy

Commands must be short, tool-oriented, and unambiguous.

Intent → Action → Target → Options

---

## Base Form

```

<action> <object> [target] [options]

```

Examples:

```

send message to Rahul
save note meeting at 4pm
reply email last thread
create banner maintenance 4 to 6

```

---

## Execution Verbs

- send
- reply
- create
- save
- open
- find
- summarize
- plan
- generate
- execute

---

## Tool Directives

Explicit tool hints:

```

use browser
use sticky notes
use gmail
use whatsapp
use vscode

```

Example:

```

create image maintenance banner use browser

```

---

## Autonomy Modifiers

```

preview only
ask before send
auto execute
dry run

```

---

## Agent Directives

```

research then write
plan then execute
chain agents

```

---

## Disambiguation Rule

If tool or target unclear → system switches to preview mode.
