# VISION — Autonomous Agent Platform Capstone

> Build an agent platform where autonomy is bounded by budgets, permissions,
  and an audit trail — and where the failure mode is "stopped", not "unbounded".

## Why this capstone

Agent platforms fail in a specific way: not from bad reasoning, but from
compounding small errors across many steps, unbounded tool access, and no way
to reconstruct what happened. The engineering is in limits, verification at
each step, and a trail you can read afterwards.

## The Arc

1. **Loop** — plan, act, observe, and where the loop must be stopped.
2. **Tools** — typed contracts, permission scoping, argument validation.
3. **Verification** — checking each action before it becomes a side effect.
4. **Limits** — budgets for tokens, steps, time, money, and blast radius.
5. **Trace** — a replayable record, and the human escalation path.

## Milestones (checkable)
- [ ] M1: build an agent loop with hard budgets and prove the budget stops it.
- [ ] M2: define a typed tool contract with schema validation and a deny list.
- [ ] M3: implement a verify-before-commit step and demonstrate it catching a bad action.
- [ ] M4: implement human-in-the-loop approval for a risk tier, with a timeout policy.
- [ ] M5: produce a replayable trace and reconstruct a specific failure from it.

## Anti-Goals
- An agent with write access to production and no approval gate.
- Retries without idempotency, so a retried side effect happens twice.
- A "loop until done" with no step budget.

## Interview Lens
- "Your agent deleted the wrong records. What in the design allowed that?"
- "How do you know the agent is making progress rather than looping?"
- "What is the blast radius of one agent run?"

## 30-Day Plan
- Wk1 loop + budgets + tool contracts. Wk2 verification + permissions.
- Wk3 approval workflow + trace replay. Wk4 a failure reconstruction exercise.

## Done = You Can
- Ship an agent that can act, and answer precisely what it can do and what
  happens when it goes wrong.
