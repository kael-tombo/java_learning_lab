# On-Call Runbook: Autonomous Agent Platform (Capstone 07)

> Scope: `AgentRuntime` (observe-think-act loop), `ToolRegistry`, `AgentMemory` (short/long-term + consolidation), `PlanningEngine` (ReAct), `MultiAgentOrchestrator`, `AgentMonitor`.
> Audience: on-call for a deployment running autonomous agents with real tool side effects.

## 1. Golden Signals (Agent-Specific)

| Signal | Source | Alert threshold (suggested) |
|---|---|---|
| Steps per task (mean/p99) | `AgentMonitor` per-agent metrics | p99 > 2× baseline over 15 min |
| Tool failure rate | `AgentMonitor` event log | > 5% over 10 min |
| Task success rate | `AgentMonitor` success/fail | drop > 10 pp vs 1 h ago |
| Memory size / recall latency | `AgentMemory` stats | recall p95 > 500 ms |
| Orchestrator queue depth | `MultiAgentOrchestrator` | sustained growth over 10 min |

## 2. Triage Decision Tree

```
Agent misbehaving?
├─ Looping / runaway steps / cost spike → §3
├─ Tool calls failing → §4
├─ Wrong answers, memory confusion → §5
└─ Multi-agent stall / contention → §6
```

First action in ALL cases: identify `agent-id` from `AgentMonitor.topPerformers/struggling` and capture the recent step trace (`getSteps()`) BEFORE restarting — it is the equivalent of a thread dump.

## 3. Runbook: Runaway Loop / Cost Spike

**Symptoms:** step count explodes, same tool called repeatedly, LLM/token cost alert, `runLoop(goal, maxSteps)` hitting its cap on every task.

**Mitigate (minutes):**
1. Hit the kill switch: `stop()` the offending `agent-id` via `AgentRuntime` control. Prefer stopping one agent over restarting the fleet.
2. If the goal is poisoned (ambiguous user request causing oscillation, e.g., "search and remember" with no termination condition), quarantine the goal — do not requeue it.
3. Check `PlanningEngine` plan: a plan with cyclic subgoals (A→B→A) indicates planner failure, not tool failure — cap `maxSteps` lower temporarily (e.g., 10 → 5) to bound blast radius while investigating.

**Diagnose (post-stop):** replay the captured step trace: look for `thought → action → observation` cycles with identical observations (tool returning the same error page). Fix is usually a missing `finish` tool trigger or a broken success predicate, not more steps.

## 4. Runbook: Tool Failures

**Symptoms:** `ToolRegistry` execution errors spike (`search`, `calculate`, custom tools), agents report "tool unavailable".

**Steps:**
1. Isolate: is it one tool or all? One tool → quarantine that tool ID in the registry so the planner routes around it; all tools → registry/config deployment issue, roll back last registry change.
2. Check parameter parsing: `PlanningEngine` thought vs actual tool args — schema drift (renamed param) is the #1 cause.
3. Verify external dependencies of default tools (search API quota, calculator sandbox) before touching agent code.
4. Re-enable the tool for a single canary agent and watch `AgentMonitor` tool-failure rate for 10 min before fleet-wide re-enable.

## 5. Runbook: Memory Confusion / Hallucinated Recall

**Symptoms:** agent cites stale facts, `recallByQuery` returns irrelevant episodes, post-consolidation quality drop.

**Steps:**
1. Check consolidation recency: did `AgentMemory` auto-consolidation just run? Compare recall quality before/after; roll back the consolidation checkpoint if degraded.
2. Separate short-term (observations) from long-term (experiences): overflow of short-term into long-term without indexing causes episodic-index pollution — trigger manual consolidation on a bounded window, not the full history.
3. Do NOT wipe long-term memory during the incident — snapshot it first; memory deletion is irreversible and destroys the post-mortem evidence.

## 6. Runbook: Multi-Agent Stall

**Symptoms:** `orchestrate(coordinator, workers, task)` never completes, worker agents idle, coordinator waiting.

**Steps:**
1. Check orchestrator message log: which worker never acknowledged? Restart that worker only.
2. Look for coordinator-pattern bottleneck: coordinator serializing all subtasks defeats parallel distribution — temporarily reduce fan-out.
3. Check for shared `AgentMemory` lock contention when multiple agents share one memory instance — give each worker its own short-term memory during the incident.

## 7. Post-Incident Checklist

- [ ] Offending agent-id + goal + step trace archived
- [ ] Tool quarantine on/off timestamps recorded
- [ ] Memory snapshot taken before any mutation
- [ ] `maxSteps` / cost guardrail change recorded and reverted or ratified
- [ ] Action items: success predicate fix, tool schema test, consolidation canary
