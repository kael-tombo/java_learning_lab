# Autonomous Agent Platform — MINI PROJECT

## Project: Bounded Agent Runtime with Tool Contracts, Verification, and Replay

A Java 21 agent runtime: a plan/act/observe loop with hard budgets, a typed
tool registry with schema validation, a verify-before-commit stage, a
human-approval workflow, and a replayable trace.

### Scope

- **Loop**: reason -> plan -> act -> observe, with a termination condition and
  a loop detector.
- **Budgets**: steps, tokens, wall time, tool calls, and a per-tool cost, all
  hard limits that stop the run rather than warn.
- **Tools**: a typed contract (JSON-schema-like) with argument validation, a
  read/write classification, and a deny list.
- **Verification**: each proposed action passes a verifier before execution;
  a verifier can reject with a reason that feeds back into the loop.
- **Approval**: actions above a risk tier pause for human approval, with a
  timeout policy (default: deny).
- **Trace**: every step recorded with inputs, outputs, budget state, and
  decisions; replayable and diffable.
- **Idempotency**: every tool call carries a key, so a retry cannot double-apply.

### Architecture

```
 task -> [planner] -> [actor] -> [verifier] -> [permission gate] -> [executor]
            ^                                              |           |
            |                                              |           v
            +----------- observation / rejection <----------+------ [tool]
                                                                        |
                                                                      [trace]
```

### Implementation — the loop with hard budgets

```java
public final class AgentLoop {
    public Trace run(Task task) {
        Trace trace = new Trace(task.id(), Instant.now());
        Budget budget = policy.budgetFor(task);           // hard limits, not warnings
        Memory memory = new Memory(workingSetSize());
        int step = 0;

        while (step < budget.maxSteps()) {
            step++;
            budget.consumeStep();

            if (budget.exhausted()) {
                trace.stop(StopReason.BUDGET_EXHAUSTED,
                        describeBudget(budget));
                return trace;                             // stop, do not continue
            }
            if (deadlinePassed(budget)) {
                trace.stop(StopReason.TIME_EXHAUSTED, describeBudget(budget));
                return trace;
            }
            if (loopDetected(memory)) {
                // The failure mode that burns budget silently: the agent
                // repeats an action because the observation never changed.
                trace.stop(StopReason.LOOP_DETECTED, "state hash unchanged for "
                        + loopPatience() + " steps: " + memory.recentActions());
                return trace;
            }

            Decision decision = reason(task, memory, budget);
            budget.consumeTokens(decision.tokensUsed());
            trace.record(decision);

            if (decision.isFinal()) {
                trace.stop(StopReason.COMPLETED, decision.answer());
                return trace;
            }

            Action action = decision.action();
            budget.consumeToolCall(action.tool(), costOf(action));

            VerificationResult v = verifier.verify(action, task, memory);
            if (!v.approved()) {
                memory.record(action, "REJECTED: " + v.reasons());
                trace.recordRejection(action, v);
                continue;                                 // feedback, not a hard stop
            }

            if (permissionGate.requiresApproval(action)) {
                ApprovalDecision approval = approvals.request(trace.id(), action, task);
                if (!approval.approved()) {
                    trace.recordDenied(action, approval.reason());
                    memory.record(action, "DENIED by approver: " + approval.reason());
                    continue;
                }
            }

            ActionResult result = execute(action, budget);   // idempotent by key
            memory.record(action, result.summary());
        }

        trace.stop(StopReason.STEP_LIMIT, "no final answer within " + budget.maxSteps() + " steps");
        return trace;
    }

    /** Loop detection: hash the observable state, not the reasoning text.
     *  Same state + same action twice = stuck. */
    private boolean loopDetected(Memory memory) {
        String h = memory.stateHash();
        int repeats = memory.consecutiveUnchanged(h);
        return repeats >= loopPatience();
    }
}
```

### Implementation — typed tool contracts

```java
public record ToolSpec(String name, String description, ParameterSchema parameters,
                       RiskTier riskTier, String idempotencyKeyFrom,
                       Duration timeout, long costUnits, boolean reversible) {
    public enum RiskTier { READ_ONLY, WRITE_REVERSIBLE, WRITE_IRREVERSIBLE, EXTERNAL }
}

/** Every argument is validated against the schema before the tool runs. An
 *  agent producing a plausible-but-wrong argument is normal, not exceptional,
 *  so this must be structural rather than a prompt instruction. */
public final class ToolRegistry {
    private final Map<String, ToolSpec> specs = new LinkedHashMap<>();
    private final Set<String> denyList = Set.of("fs.delete_any", "sql.drop_table",
                                                "http.post_internal_admin");

    public void register(ToolSpec spec, ToolHandler handler) {
        if (denyList.contains(spec.name())) {
            throw new ToolDenied(spec.name(), "on the global deny list");
        }
        specs.put(spec.name(), spec);
        handlers.put(spec.name(), handler);
    }

    public PreparedAction prepare(String toolName, String rawArgsJson) {
        ToolSpec spec = specs.get(toolName);
        if (spec == null) throw new UnknownTool(toolName);
        if (denyList.contains(toolName)) throw new ToolDenied(toolName, "deny list");

        JsonNode args = parse(rawArgsJson);
        List<String> problems = spec.parameters().validate(args);
        if (!problems.isEmpty()) {
            // Return the problems as feedback so the agent can correct itself,
            // rather than throwing and losing the turn.
            return PreparedAction.rejected(toolName, problems);
        }
        String idemKey = idempotencyKey(spec, args, args);
        return PreparedAction.ready(toolName, args, idemKey, spec);
    }
}
```

### Implementation — verify before commit

```java
public sealed interface Verifier {
    record Approved() implements Verifier {}
    record Rejected(List<String> reasons) implements Verifier {}
    record NeedsHuman(String reason, String approverHint) implements Verifier {}
}

/**
 * Verification runs BEFORE the side effect. This is the difference between an
 * agent that occasionally errs and one that causes damage: the error is
 * caught while it is still a proposal.
 */
public final class VerificationChain {
    private final List<NamedVerifier> verifiers;

    public Verifier.Result verify(Action a, Task task, Memory memory) {
        List<String> reasons = new ArrayList<>();
        for (NamedVerifier v : verifiers) {
            Verifier.Result r = v.check(a, task, memory);
            if (r instanceof Rejected rejected) reasons.addAll(rejected.reasons());
            if (r instanceof NeedsHuman nh) return nh;      // escalate immediately
        }
        return reasons.isEmpty() ? new Approved() : new Rejected(reasons);
    }
}

public final class BlastRadiusVerifier implements NamedVerifier {
    /**
     * Estimate what the action touches, before it touches it. This is the
     * control that answers "what is the blast radius of one agent run" with a
     * number rather than a hope.
     */
    public Verifier.Result check(Action a, Task task, Memory memory) {
        if (!a.tool().startsWith("fs.") && !a.tool().startsWith("sql.")) return new Approved();
        long rows = dryRun(a);                             // SELECT COUNT(*) / dry run
        long limit = policy.rowLimitFor(task);
        if (rows > limit) {
            return new Rejected(List.of("action would affect " + rows
                    + " rows, above the limit of " + limit
                    + ". Narrow the scope, or request approval for a larger batch."));
        }
        if (a.tool().equals("sql.drop_table")) {
            return new NeedsHuman("destructive schema change", "data-platform oncall");
        }
        return new Approved();
    }
}
```

### Implementation — approval with a timeout policy

```java
public final class ApprovalGate {
    public enum Policy { REQUIRE_APPROVAL, AUTO_APPROVE_BELOW, DENY_ALWAYS }

    /**
     * Timeout policy matters more than it looks: the default is DENY, not
     * approve. An approval that times out into an approval is not an approval
     * gate, it is a delay.
     */
    public boolean requiresApproval(Action a, Task task) {
        return switch (a.tool().riskTier()) {
            case READ_ONLY -> false;
            case WRITE_REVERSIBLE -> rowsTouched(a) > policy.reversibleRowLimit();
            case WRITE_IRREVERSIBLE, EXTERNAL -> true;
        };
    }

    public ApprovalDecision request(String traceId, Action a, Task task) {
        PendingApproval p = approvals.create(traceId, a, task, policy.approvalTimeout());
        scheduler.schedule(p.expiresAt(), () -> {
            if (p.isPending()) p.resolve(ApprovalDecision.denied("approval timed out; "
                    + "deny is the default on timeout"));
        });
        return p.await(policy.approvalTimeout());
    }
}
```

### Implementation — idempotent execution and the trace

```java
public final class Executor {
    /**
     * Idempotency is not optional for an agent. Retries are expected (timeouts,
     * verifier rejections that re-propose the same action, reconnection), and a
     * retried irreversible tool call is a duplicated side effect.
     */
    public ActionResult execute(Action a, Budget budget) {
        String key = a.idempotencyKey();
        Optional<ActionResult> prior = executed.get(key);
        if (prior.isPresent()) {
            trace.markReplayed(key);
            return prior.get();                            // same result, no new effect
        }
        try (var timeout = budget.deadlineFor(a.tool().timeout())) {
            ActionResult r = handlers.get(a.tool()).apply(a.args());
            executed.put(key, r);
            audit.append(key, a.tool(), a.args(), Instant.now());   // append-only
            return r;
        }
    }
}

public final class Trace {
    public record Step(int index, String thought, Action action, String rawArgs,
                       String verification, String approval, String observation,
                       long tokensUsed, long costUnits, Instant at) {}

    public void record(Decision d) { steps.add(new Step(steps.size(), d.reasoning(), ...)); }

    /** Replay: re-run the recorded decisions against a stubbed executor, to
     *  see whether a fix changes the outcome. Deterministic by construction:
     *  the trace holds the arguments, not a pointer to live state. */
    public ReplayReport replay(Map<String, String> patchedArgs) {
        ReplayExecutor stub = new ReplayExecutor(handlers, patchedArgs);
        AgentLoop replayLoop = new AgentLoop(planner, verifier, permissionGate, stub);
        Trace t2 = replayLoop.runFromRecordedDecisionPoints(steps());
        return new ReplayReport(traceId, t2.stopReason(), divergedAtStep(t2));
    }
}
```

### Test It

```java
@Test void budgetStopsTheRun() {
    planner.forceNonTerminating();
    Trace t = new AgentLoop(planner, verifier, gate, executor).run(task());
    assertEquals(StopReason.BUDGET_EXHAUSTED, t.stopReason());
    assertTrue(t.steps().size() <= policy.maxSteps());
}

@Test void verifierBlocksABroadDestructiveAction() {
    Action a = action("sql.delete", Map.of("table", "orders", "where", "1=1"));
    Verifier.Result r = chain.verify(a, task(), memory);
    assertInstanceOf(Verifier.NeedsHuman.class, r);
    assertTrue(verifier.dryRunCount(a) > 1_000_000);
}

@Test void retryDoesNotDoubleApply() {
    Action a = action("fs.write", Map.of("path", "/tmp/x", "content", "hello"));
    executor.execute(a, budget());
    executor.execute(a, budget());                       // same idempotency key
    assertEquals(1, fs.writeCount("/tmp/x"));
    assertEquals(1, trace.replayedCount());
}

@Test void approvalTimeoutDenies() {
    clock.advance(policy.approvalTimeout().plusSeconds(1));
    ApprovalDecision d = gate.request("t1", writeAction(), task());
    assertFalse(d.approved());
    assertTrue(d.reason().contains("timed out"));
}

@Test void loopIsDetectedBeforeTheBudgetBurns() {
    planner.forceRepeatingAction();
    Trace t = loop.run(task());
    assertEquals(StopReason.LOOP_DETECTED, t.stopReason());
}
```

### Stretch

- Add a policy engine (e.g. Cedar/Rego style) so permissions are declarative.
- Add tool chaining with a dependency graph and a maximum chain depth.
- Add a cost model per run and a per-tenant budget, with a hard spend cap.
- Add adversarial test cases: prompt injection inside tool output, a tool
  returning a payload that tries to instruct the agent.

## Deliverables

- [ ] Loop with hard budgets on steps, tokens, time, tool calls, and cost
- [ ] Loop detection on observable state, not on reasoning text
- [ ] Typed tool contracts with schema validation and a global deny list
- [ ] Verification chain running before side effects, with feedback on rejection
- [ ] Blast-radius verifier with a dry-run row count and a row limit
- [ ] Approval gate with a deny-on-timeout policy and an append-only audit log
- [ ] Idempotent execution keyed per action, with a retry test
- [ ] Replayable trace with argument patching and divergence detection
- [ ] Tests: budget stop, verifier block, no double-apply, timeout deny, loop detect
- [ ] Adversarial test: prompt injection via tool output
