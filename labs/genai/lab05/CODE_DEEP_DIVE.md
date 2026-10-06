# Lab 05: LLM Agent Frameworks — Code Deep Dive

## 1. Project Structure

```
lab05/
  src/com/genai/lab05/
    agent/Agent.java            the ReAct loop + budgets
    agent/AgentConfig.java      record of all budgets and flags
    agent/Budget.java           mutable counters, throws BudgetExhausted
    llm/LlmClient.java          interface
    llm/ScriptedLlmClient.java  deterministic test double
    tool/Tool.java              record(name, description, schema, handler, reversible)
    tool/ToolRegistry.java      register / find / schemas / guarded lookup
    tool/ArgValidator.java      hand-written schema checks
    tool/Tools.java             built-in demo tools
    parse/ActionParser.java     5 parse strategies, fail closed
    parse/ParsedAction.java     sealed: ToolCall | Final | Unknown
    memory/Memory.java          working memory + pruning
    observe/ObservationPruner.java
    trace/TraceEmitter.java     JSONL spans
    eval/TrajectoryTest.java    expected tool sequences
    Main.java
```

## 2. Tool and Registry

```java
public record Tool(
        String name,
        String description,
        Map<String, Object> inputSchema,
        boolean reversible,
        Handler handler) {

    public interface Handler {
        /** @return JSON-encoded result, never throws past the agent loop. */
        String apply(Map<String, Object> args);
    }
}

public final class ToolRegistry {
    private final Map<String, Tool> tools = new LinkedHashMap<>();
    private final Set<String> revoked = new HashSet<>();

    public ToolRegistry register(Tool t) {
        if (tools.containsKey(t.name())) throw new IllegalStateException("duplicate tool: " + t.name());
        tools.put(t.name(), t);
        return this;
    }

    /** Role-scoped view: an agent only ever sees what it was granted. */
    public ToolRegistry scopedTo(Set<String> allowed) {
        ToolRegistry scoped = new ToolRegistry();
        tools.forEach((n, t) -> { if (allowed.contains(n)) scoped.tools.put(n, t); });
        scoped.revoked.addAll(revoked);
        return scoped;
    }

    public Optional<Tool> find(String name) {
        if (revoked.contains(name)) return Optional.empty();   // revocation wins
        return Optional.ofNullable(tools.get(name));
    }
}
```

`scopedTo` is the mechanism behind "specialists never receive tools outside their
subset" in Exercise 9. Revocation must beat registration so a revoked tool cannot
be reached through a cached reference.

## 3. Argument Validation

```java
public final class ArgValidator {

    public record Result(boolean ok, String error, Map<String, Object> clean) {}

    public static Result validate(Tool tool, Map<String, Object> args) {
        @SuppressWarnings("unchecked")
        Map<String, Object> props =
                (Map<String, Object>) tool.inputSchema().get("properties");

        for (Object k : tool.inputSchema().getOrDefault("required", List.of())) {
            if (!args.containsKey(k)) return fail("MISSING_ARGUMENT:" + k);
        }
        for (var e : args.entrySet()) {                          // additionalProperties:false
            if (!props.containsKey(e.getKey())) return fail("UNKNOWN_ARGUMENT:" + e.getKey());
        }
        Map<String, Object> clean = new LinkedHashMap<>();
        for (var e : args.entrySet()) {
            Object v = coerce(props.get(e.getKey()), e.getValue());
            if (v instanceof String s && !PATTERN_OK.test(s) && hasPattern(props, e.getKey())) {
                return fail("INVALID_ARGUMENT:" + e.getKey());   // blocks injection payloads
            }
            clean.put(e.getKey(), v);
        }
        return new Result(true, null, clean);
    }
}
```

Validate **before** dispatch and count invocations separately from successes, so a
test can assert the handler was never reached on an invalid argument.

## 4. Parser: Five Strategies, Fail Closed

```java
public sealed interface ParsedAction permits ToolCall, FinalAnswer, BadAction {}

public record ToolCall(String tool, Map<String, Object> args) implements ParsedAction {}
public record FinalAnswer(String text) implements ParsedAction {}
public record BadAction(String reason, String raw) implements ParsedAction {}

public final class ActionParser {

    private static final Pattern FENCED = Pattern.compile("(?s)```(?:json)?\\s*(\\{.*?\\})\\s*```");
    private static final Pattern AFTER  = Pattern.compile("(?s)Action:\\s*(\\{.*)");
    private static final Pattern MINI   = Pattern.compile(
            "(?s)Action:\\s*([A-Za-z_][A-Za-z0-9_]*)\\s*\\((.*)\\)");

    public ParsedAction parse(String raw) {
        String t = raw == null ? "" : raw.strip();
        if (t.isEmpty()) return new BadAction("EMPTY", t);

        // strategy 1: provider-native structured call
        var nativeCall = Json.readIfToolCall(t);
        if (nativeCall != null) return toToolCall(nativeCall);

        // strategy 2: fenced JSON
        var fenced = FENCED.matcher(t);
        if (fenced.find()) return toToolCall(fenced.group(1));

        // strategy 4 first: mini-language is a stricter prefix than bare JSON
        var mini = MINI.matcher(t);
        if (mini.matches()) return miniCall(mini.group(1), mini.group(2));

        // strategy 3: bare JSON after Action:
        var after = AFTER.matcher(t);
        if (after.find()) return toToolCall(after.group(1));

        // strategy 5: fall closed
        if (looksLikeFinal(t)) return new FinalAnswer(stripPreamble(t));
        return new BadAction("UNPARSEABLE", t);
    }
}
```

Order matters: `MINI` must be tried before the looser `AFTER` pattern, otherwise the
bare-JSON branch swallows the mini-language form. `toToolCall` returns
`BadAction` on parse failure rather than throwing — that is the fail-closed
behavior.

## 5. Mini-Language Argument Parsing

```java
private ToolCall miniCall(String name, String argBlob) {
    Map<String, Object> args = new LinkedHashMap<>();
    Matcher m = KV.matcher(argBlob);                    // (\w+)=("([^"]*)"|[^,]+)
    while (m.find()) {
        String key = m.group(1);
        String raw = m.group(2);
        args.put(key, raw.startsWith("\"") ? raw.substring(1, raw.length() - 1)
                                            : parseScalar(raw.strip()));
    }
    return new ToolCall(name, args);
}
```

`parseScalar` maps `true/false`, integers, and bare strings. Any token containing
`(`/`)`/backticks is rejected as `UNPARSEABLE` — a cheap injection tripwire.

## 6. The Agent Loop

```java
public final class Agent {

    private final LlmClient llm;
    private final ToolRegistry tools;
    private final AgentConfig cfg;
    private final TraceEmitter trace;
    private final Memory memory;

    public AgentResult run(String goal) {
        memory.system(cfg.systemPrompt());
        memory.user("Goal: " + goal);
        long deadline = System.nanoTime() + cfg.maxWallClockMs() * 1_000_000L;

        while (true) {
            if (memory.steps() >= cfg.maxSteps()) return exhausted("STEPS");
            if (memory.tokensIn() >= cfg.maxTokens()) return exhausted("TOKENS");
            if (System.nanoTime() > deadline)            return exhausted("WALL_CLOCK");

            if (loopDetector().tripped(memory.recentActions(cfg.loopWindow()))) {
                memory.observation(
                    "You already called this tool with identical arguments. "
                  + "Change approach or produce the Final Answer now.");
            }

            long t0 = System.nanoTime();
            String raw = llm.complete(memory.render(), cfg.sampling());
            memory.addAssistant(raw);
            memory.countTokens(cfg.tokenizer().count(memory.render()));

            var action = parser.parse(raw);
            trace.span(memory.steps(), raw, action, System.nanoTime() - t0);

            switch (action) {
                case FinalAnswer f -> { trace.finish(); return AgentResult.done(f.text(), memory.stats()); }
                case BadAction b  -> memory.observation(b.reason() + ": " + b.raw());
                case ToolCall c   -> memory.observation(dispatch(c));
            }
        }
    }

    private String dispatch(ToolCall call) {
        Optional<Tool> found = tools.find(call.tool());
        if (found.isEmpty()) return "UNKNOWN_TOOL:" + call.tool();
        Tool tool = found.get();
        var v = ArgValidator.validate(tool, call.args());
        if (!v.ok()) return "ERROR:" + v.error();
        if (!tool.reversible() && !approvals.granted(tool.name(), call.args())) {
            return "ERROR:APPROVAL_REQUIRED:" + tool.name();
        }
        try {
            return tool.handler().apply(v.clean());        // handler must not throw
        } catch (RuntimeException ex) {
            metrics.toolError(tool.name());
            return "ERROR:TOOL_FAILURE:" + ex.getClass().getSimpleName();
        }
    }
}
```

Invariants worth stating as tests: the loop always terminates (budgets are checked
at the top), handlers never throw into the loop, and every branch returns a string
observation so the message list stays well-typed.

## 7. Budget Tracking

```java
public final class Budget {
    private final int maxSteps, maxTokens;
    private final long maxWallClockNanos;
    private int steps, tokens;
    private long start = System.nanoTime();

    public void step() { steps++; }
    public boolean exhausted() {
        return steps >= maxSteps || tokens >= maxTokens
            || System.nanoTime() - start > maxWallClockNanos;
    }
    public BudgetSnapshot snapshot() { /* steps, tokens, elapsedMs */ }
}
```

Wall clock matters because a single slow tool can blow the deadline even with
step budget to spare — check all three, in that order (cheapest first is wrong
here; clock is O(1) and catches the case steps/tokens miss).

## 8. Observation Pruning

```java
public String prune(List<Message> history, int keepVerbatim, int tokenCap) {
    int start = Math.max(0, history.size() - keepVerbatim - 1);
    List<String> out = new ArrayList<>();
    out.add(system);
    for (int i = 1; i < start; i++) {
        Message m = history.get(i);
        out.add(m.role() == OBSERVATION ? summarize(m) : m.content());
    }
    out.addAll(history.subList(start, history.size()).stream().map(Message::content).toList());
    while (tokenizer().count(join(out)) > tokenCap && out.size() > 2) {
        out.remove(2);                                      // drop the oldest summary first
    }
    return join(out);
}

private String summarize(Message obs) {                    // "tool=X status=ok keys=a,b,c"
    JsonNode j = Json.parse(obs.content());
    if (j.has("error")) return "tool=" + j.get("tool") + " status=error code=" + j.get("error");
    return "tool=" + j.path("tool").asText("?")
         + " status=ok keys=" + String.join(",", fieldNames(j));
}
```

Dropping the **oldest summary first** (not the oldest message) keeps the system
prompt and recent evidence intact. Test that every tool result name still appears
somewhere after pruning.

## 9. Loop Detection

```java
public boolean tripped(List<String> recentActions) {
    Map<String, Integer> seen = new HashMap<>();
    for (String a : recent) seen.merge(actionKey(a), 1, Integer::sum);
    return seen.values().stream().anyMatch(c -> c >= 2);
}

private String actionKey(String a) {                        // tool + normalized args
    JsonNode j = Json.parse(a);
    TreeMap<String, Object> norm = new TreeMap<>(Json.toMap(j.get("args")));
    return j.get("tool").asText() + "|" + norm;
}
```

Normalizing args before counting is essential: `{"id":"A-1"}` and
`{"id": "A-1"}` are the same action.

## 10. Scripted Test Double

```java
public final class ScriptedLlmClient implements LlmClient {
    private final Deque<String> script;
    private final AtomicInteger call = new AtomicInteger();

    public String complete(String prompt, Sampling s) {
        int i = call.getAndIncrement();
        if (i >= script.size()) throw new IllegalStateException(
            "script exhausted at call " + i + " -- agent looped longer than the script");
        return script.get(i);
    }
}
```

Exhausting the script is itself a signal: if the agent needed more turns than the
script, the loop is not converging. This makes "the agent took 7 steps where 3 were
planned" a test failure rather than a surprise.

## 11. Trajectory Assertion

```java
List<String> expected = List.of("lookupCustomer", "listInvoices", "getOrderStatus");
assertEquals(expected, trace.toolNames());                   // wording ignored
assertTrue(trace.observations().stream().noneMatch(o -> o.startsWith("ERROR:")));
```

The second assertion is the valuable one — a trajectory that succeeds with errors
along the way is brittle.

## 12. Common Java Pitfalls

- `switch` over a sealed type without exhaustive cases (enable preview or use a
  `default` that throws).
- Handler exceptions escaping into the loop — wrap everything.
- `HashMap` ordering making traces nondeterministic; use `LinkedHashMap`/`TreeMap`.
- Blocking indefinitely on the approval future; always set a timeout.
- Leaking the approval future across runs — one per call, never a field.

## Self-Check

1. Why must `MINI` be matched before `AFTER`?
2. Trace one iteration where the tool is revoked: what observation reaches the model?
3. Why is checking wall clock not redundant with `maxSteps`?
4. Which assertion in Exercise 12 catches a "lucky" pass, and why?