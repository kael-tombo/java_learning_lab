# Lab 04: AI Agent Frameworks — Code Deep Dive

## 1. Project Structure

```
lab04/
  src/com/aiengineering/lab04/
    tool/Tool.java, ToolRegistry.java, ArgValidator.java
    tool/ApprovalGate.java, CircuitBreaker.java
    parse/ActionParser.java, ParsedAction.java
    agent/Agent.java, AgentConfig.java, Budget.java
    agent/LoopDetector.java
    memory/Memory.java, ObservationPruner.java
    plan/Planner.java, PlanStep.java
    orchestrator/Supervisor.java, Pipeline.java, FanOutVote.java
    trace/TraceEmitter.java
    llm/LlmClient.java, ScriptedLlmClient.java
    eval/TrajectoryTest.java, AgentMetrics.java
    Main.java
```

## 2. Tool and Scoped Registry

```java
public record Tool(String name, String description, Map<String, Object> schema,
                   boolean reversible, boolean readOnly, Handler handler) {
    public interface Handler { String apply(Map<String, Object> args); }
}

public final class ToolRegistry {
    private final Map<String, Tool> tools = new LinkedHashMap<>();
    private final Set<String> revoked = new HashSet<>();

    public void register(Tool t) {
        if (tools.containsKey(t.name())) throw new IllegalStateException("duplicate: " + t.name());
        tools.put(t.name(), t);
    }

    public void revoke(String name) { revoked.add(name); }

    /** A scoped view is how specialists are prevented from reaching other tools. */
    public ToolRegistry scopedTo(Set<String> allowed) {
        ToolRegistry s = new ToolRegistry();
        tools.forEach((n, t) -> { if (allowed.contains(n)) s.tools.put(n, t); });
        s.revoked.addAll(revoked);
        return s;
    }

    public Optional<Tool> find(String name) {
        return revoked.contains(name) ? Optional.empty() : Optional.ofNullable(tools.get(name));
    }
}
```

`scopedTo` returns a new registry rather than filtering at dispatch, so a bug in the
dispatcher cannot accidentally bypass the role boundary. Revocation is checked inside
`find` so even a cached reference is neutered.

## 3. Argument Validation

```java
public final class ArgValidator {

    public record Result(boolean ok, String error, Map<String, Object> clean) {}

    @SuppressWarnings("unchecked")
    public static Result validate(Tool tool, Map<String, Object> args) {
        Map<String, Object> props = (Map<String, Object>) tool.schema().get("properties");
        List<String> required = (List<String>) tool.schema().getOrDefault("required", List.of());

        for (String r : required)
            if (!args.containsKey(r)) return fail("MISSING_ARGUMENT:" + r);

        for (String key : args.keySet())                       // additionalProperties:false
            if (!props.containsKey(key)) return fail("UNKNOWN_ARGUMENT:" + key);

        Map<String, Object> clean = new TreeMap<>();          // normalize order for hashing
        for (var e : args.entrySet()) {
            Object spec = props.get(e.getKey());
            String type = (String) ((Map<String, Object>) spec).getOrDefault("type", "string");
            Object v = coerce(type, e.getValue());
            if (v == null) return fail("INVALID_TYPE:" + e.getKey());
            String pattern = (String) ((Map<String, Object>) spec).get("pattern");
            if (pattern != null && !v.toString().matches(pattern))
                return fail("INVALID_ARGUMENT:" + e.getKey());
            clean.put(e.getKey(), v);
        }
        return new Result(true, null, clean);
    }
}
```

Two details carry the security value: the pattern check is what blocks
`A-1001'; DROP TABLE`, and the `TreeMap` normalization is what makes the approval key
and loop-detection key stable against argument ordering.

## 4. Parser: Five Strategies, Fail Closed

```java
public sealed interface ParsedAction permits ToolCall, FinalAnswer, BadAction {}
public record ToolCall(String tool, Map<String, Object> args) implements ParsedAction {}
public record FinalAnswer(String text) implements ParsedAction {}
public record BadAction(String reason, String raw) implements ParsedAction {}

public final class ActionParser {

    private static final Pattern FENCED = Pattern.compile("(?s)```(?:json)?\\s*(\\{.*?\\})\\s*```");
    private static final Pattern MINI   = Pattern.compile("(?s)^Action:\\s*([A-Za-z_]\\w*)\\s*\\((.*)\\)\\s*$");
    private static final Pattern AFTER  = Pattern.compile("(?s)Action:\\s*(\\{.*)$");
    private static final Pattern KV     = Pattern.compile("(\\w+)\\s*=\\s*(\"[^\"]*\"|[^,()]+)");

    public ParsedAction parse(String raw) {
        String t = raw == null ? "" : raw.strip();
        if (t.isEmpty()) return new BadAction("EMPTY", t);

        var native_ = Json.readToolCall(t);
        if (native_ != null) return native_;

        var fenced = FENCED.matcher(t);
        if (fenced.find()) return toCall(fenced.group(1));

        // MINI before AFTER: the mini-language is a stricter prefix
        var mini = MINI.matcher(t);
        if (mini.matches()) return new ToolCall(mini.group(1), parseKv(mini.group(2)));

        var after = AFTER.matcher(t);
        if (after.find()) return toCall(after.group(1));

        return new BadAction("UNPARSEABLE", t);                // fail closed
    }

    static Map<String, Object> parseKv(String blob) {
        Map<String, Object> args = new LinkedHashMap<>();
        Matcher m = KV.matcher(blob);
        while (m.find()) {
            String raw = m.group(2).strip();
            args.put(m.group(1), raw.startsWith("\"") ? raw.substring(1, raw.length() - 1)
                                                      : parseScalar(raw));
        }
        return args;
    }
}
```

`MINI` must be tried before `AFTER` or the looser pattern swallows the mini-language
form. `toCall` returning `BadAction` rather than throwing is the fail-closed behavior.

## 5. The Agent Loop

```java
public final class Agent {

    private final LlmClient llm;
    private final ToolRegistry tools;
    private final AgentConfig cfg;
    private final Budget budget;
    private final LoopDetector loopDetector;
    private final TraceEmitter trace;

    public AgentResult run(String goal) {
        Memory mem = Memory.start(cfg.systemPrompt(), goal);
        long deadline = System.nanoTime() + cfg.maxWallClockMs() * 1_000_000L;

        while (true) {
            if (budget.steps() >= cfg.maxSteps())        return budgetExhausted("STEPS", mem);
            if (budget.tokens() >= cfg.maxTokens())      return budgetExhausted("TOKENS", mem);
            if (budget.toolCalls() >= cfg.maxToolCalls())return budgetExhausted("TOOL_CALLS", mem);
            if (System.nanoTime() >= deadline)           return budgetExhausted("WALL_CLOCK", mem);

            if (loopDetector.tripped(mem.recentActions(cfg.loopWindow()))) {
                mem.observation("You already called this tool with identical arguments. "
                              + "Change approach or produce the Final Answer now.");
            }

            long t0 = System.nanoTime();
            String raw = llm.complete(mem.render(), cfg.sampling());
            mem.addAssistant(raw);
            budget.addTokens(cfg.tokenizer().count(mem.render()));

            ParsedAction action = parser.parse(raw);
            trace.span(mem.steps(), raw, action, System.nanoTime() - t0, budget.snapshot());

            switch (action) {
                case FinalAnswer f -> return AgentResult.done(f.text(), mem.stats());
                case BadAction b  -> mem.observation("ERROR:" + b.reason());
                case ToolCall c   -> { mem.observation(dispatch(c)); budget.toolCall(); }
            }
        }
    }
}
```

Budget checks happen at the top of every iteration and cover four independent
resources. The `loopDetector` runs before the model call so the intervention is visible
in that turn's output rather than one turn later.

## 6. Dispatch Order

```java
private String dispatch(ToolCall call) {
    Optional<Tool> found = tools.find(call.tool());
    if (found.isEmpty()) return "ERROR:UNKNOWN_TOOL:" + call.tool();
    Tool tool = found.get();

    var v = ArgValidator.validate(tool, call.args());
    if (!v.ok()) return "ERROR:" + v.error();                    // handler NEVER reached

    if (!tool.reversible() && !approvals.granted(approvalKey(tool.name(), v.clean())))
        return "ERROR:APPROVAL_REQUIRED:" + tool.name();

    if (!breakers.allow(tool.name())) return "ERROR:CIRCUIT_OPEN:" + tool.name();

    try {
        String result = tool.handler().apply(v.clean());
        breakers.recordSuccess(tool.name());
        return result;
    } catch (RuntimeException ex) {
        breakers.recordFailure(tool.name());
        return "ERROR:TOOL_FAILURE:" + ex.getClass().getSimpleName();   // recoverable
    }
}
```

The ordering is deliberate: allowlist, then arguments, then approval, then breaker, then
execute. Every rejection is an **observation string** so the policy can react, and every
path returns a string so the message list stays well-typed.

## 7. Approval Gate

```java
public final class ApprovalGate {

    private final Duration timeout;

    /** Absent approval -> deny. The model cannot grant itself authority. */
    public boolean granted(String key) {
        CompletableFuture<Boolean> f = pending.get(key);
        if (f == null) return false;                             // nothing pending -> deny
        try {
            return Boolean.TRUE.equals(f.get(timeout.toMillis(), TimeUnit.MILLISECONDS));
        } catch (TimeoutException e) {
            f.complete(false);                                   // timeout -> deny
            metrics.approvalTimeout(key);
            return false;
        } finally {
            pending.remove(key);                                 // one approval per call
        }
    }
}
```

`f.get(timeout)` with `complete(false)` on timeout is the whole design: absent, invalid,
or late approval is a denial. Removing the entry in `finally` prevents a stale approval
from being reused for a different call.

## 8. Loop Detector

```java
public final class LoopDetector {

    private final int window;

    public boolean tripped(List<String> recentActions) {
        Map<String, Integer> counts = new HashMap<>();
        for (String a : recentActions) counts.merge(normalizedKey(a), 1, Integer::sum);
        return counts.values().stream().anyMatch(c -> c >= 2);
    }

    /** Normalize argument ORDER (and quoting) so equivalent calls collapse. */
    static String normalizedKey(String actionJson) {
        JsonNode n = Json.readTree(actionJson);
        TreeMap<String, String> norm = new TreeMap<>();
        n.path("args").fields().forEachRemaining(e -> norm.put(e.getKey(), e.getValue().asText().strip()));
        return n.path("tool").asText() + "|" + norm;
    }
}
```

Without normalization, `{"id":"A-1"}` and `{"id": "A-1"}` count as different actions and
the detector misses the loop it exists to catch.

## 9. Memory and Pruning

```java
public final class Memory {

    private final List<Message> history = new ArrayList<>();
    private int promptTokens;

    public String render(Pruner pruner, int keepVerbatim, int tokenCap) {
        String out = pruner.prune(history, keepVerbatim, tokenCap);
        promptTokens = tokenizer.count(out);
        return out;
    }

    public void observation(String toolResult) {
        history.add(new Message("user", "<observation>" + toolResult + "</observation>"));
    }

    public String evidenceLedger() {                              // claims must map to results
        return history.stream().filter(m -> m.content().startsWith("<observation>"))
                .map(m -> m.content()).collect(joining("\n"));
    }
}
```

Wrapping observations in explicit tags is what makes the evidence ledger extractable,
which is what lets a critic check that every claim in the final answer traces to a tool
result.

## 10. Planner

```java
public record PlanStep(int id, String goal, List<String> candidateTools, boolean optional) {}

public final class Planner {

    public List<PlanStep> plan(String goal, LlmClient llm) {
        String raw = llm.complete(
            "Break the goal into 2-5 steps. JSON array of {goal, tools}. No prose.",
            Sampling.deterministic());
        try {
            return parseSteps(raw);
        } catch (RuntimeException e) {
            metrics.planParseFailure();
            return List.of(new PlanStep(1, goal, List.of(), false));   // degrade to reactive
        }
    }

    /** A deviation must be recorded with a reason, or the plan is not being followed. */
    public void recordDeviation(PlanStep skipped, String reason) {
        deviations.add(new Deviation(skipped.id(), reason));
        metrics.deviation();
    }
}
```

Falling back to a single reactive step when the plan cannot be parsed is the right
failure mode: degrade to the simpler loop rather than aborting.

## 11. Supervisor

```java
public final class Supervisor {

    private final Map<String, Agent> specialists;

    public String delegate(String specialist, String task, AgentConfig cfg) {
        Agent a = specialists.get(specialist);                    // already scoped
        AgentResult r = a.run(task);
        totals.merge(specialist, r.costUsd(), Double::sum);       // per-specialist cost
        return r.text();
    }

    public String run(String goal, LlmClient llm) {
        StringBuilder evidence = new StringBuilder();
        for (String s : route(goal, llm))                          // routing call
            evidence.append(s).append(": ").append(delegate(s, goal, cfg)).append('\n');
        return synthesize(evidence.toString(), llm);              // synthesis call
    }
}
```

Per-specialist cost accumulation is the metric that tells you whether the supervisor
design is earning its overhead. `route` and `synthesize` are both model calls, so the
architecture is `1 + m + 1` calls, not `m`.

## 12. Trajectory Test

```java
public record TrajectoryCase(String name, String goal, List<String> expectedTools) {}

public static void assertTrajectory(TrajectoryCase c, List<String> actual) {
    List<String> trimmed = actual.stream().map(String::strip).toList();
    if (!trimmed.equals(c.expectedTools()))
        throw new AssertionError("%s: expected %s but got %s"
                .formatted(c.name(), c.expectedTools(), trimmed));
    // also assert no unexpected ERROR observations
}

public static void assertSuiteHasTeeth(List<TrajectoryCase> cases, Agent agent) {
    try {
        runAll(cases, agent);
        throw new AssertionError("suite passed on a deliberately broken agent");
    } catch (AssertionError expected) {
        // the suite MUST fail when a tool description is corrupted
    }
}
```

The second method is the one that proves the suite works. A trajectory suite that has
never failed is not evidence of anything.

## 13. Metrics

```java
public record AgentMetrics(int tasks, int successes, int stepsTotal, int stepsCorrect,
                           int tasksWithErrors, int tasksRecovered,
                           double costTotal, Map<String, Double> costByTool) {

    public double successRate()      { return successes / (double) tasks; }
    public double stepEfficiency()   { return stepsCorrect / (double) stepsTotal; }
    public double recoveryRate()     { return tasksWithErrors == 0 ? 1
                                            : tasksRecovered / (double) tasksWithErrors; }
    public double costPerTask()      { return costTotal / tasks; }
}
```

`recoveryRate` is the most informative single metric for agent frameworks: it separates
"cannot plan" from "no way to recover".

## Self-Check

1. Why does `scopedTo` return a new registry instead of filtering at dispatch?
2. Why is the validator's output a `TreeMap`?
3. What breaks if `MINI` is tried after `AFTER`?
4. Why does `ApprovalGate.granted` remove the pending entry in `finally`?
5. What does `assertSuiteHasTeeth` prove?