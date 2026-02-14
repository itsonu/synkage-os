# Project Structure

```
synkage-os/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── docs/
│ ├── architecture.md
│ ├── autonomy_safety.md
│ ├── command_grammar.md
│ ├── mvp_vs_phase2.md
│ └── research_abstract.md
│
├── brain/ ← renamed from core (more accurate now)
│ ├── prime.py
│ ├── intent_resolver.py
│ ├── situation_detector.py
│ ├── priority_resolver.py
│ ├── autonomy_guard.py
│ └── verifier.py
│
├── agents/
│ ├── base_agent.py
│ ├── planner_agent.py
│ ├── researcher_agent.py
│ ├── builder_agent.py
│ ├── critic_agent.py
│ └── reporter_agent.py
│
├── skills/
│ ├── base_skill.py
│ ├── text/
│ ├── analysis/
│ └── decision/
│
├── adapters/ ← NEW — important
│ ├── openclaw_adapter.py
│ ├── local_exec_adapter.py
│ └── tool_adapter_base.py
│
├── tools/ ← keep but shrink responsibility
│ ├── tool_registry.json
│ ├── browser/
│ ├── desktop/
│ └── fallback/
│
├── context/
│ ├── signal_ingestion.py
│ ├── activity_monitor.py
│ ├── time_context.py
│ └── app_context.py
│
├── memory/
│ ├── project.md
│ ├── user_profile.json
│ ├── relationship_state.json
│ ├── logs.json
│ └── night_cycle.py
│
├── execution/
│ ├── action_planner.py
│ ├── autonomy_router.py ← NEW
│ ├── confirmation_loop.py
│ └── rollback.py
│
├── avatar/ ← NEW (future layer)
│ ├── state_mapper.py
│ ├── emotion_axes.py
│ └── unity_bridge.py
│
├── interfaces/
│ ├── cli.py
│ ├── hotkeys.py
│ └── voice_stub.py
│
├── config/
│ ├── permissions.yaml
│ ├── autonomy_levels.yaml
│ ├── command_aliases.yaml
│ └── app_preferences.yaml
│
├── tests/
│
└── scripts/
├── init_project.py
├── run_synkage.py ← rename
└── nightly_update.py
```
