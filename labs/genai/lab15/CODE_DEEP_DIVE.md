# Lab 15: Building a GenAI Platform — Code Deep Dive

## 1. Project Structure

```
lab15/
  src/com/genai/lab15/
    registry/ModelRegistry.java        logical name -> deployment
    registry/PromptRegistry.java       versions, owners, risk tiers
    registry/ToolRegistry.java         schemas, side effects, approvals
    route/Router.java                  capability/quality/latency/region/health
    route/CircuitBreaker.java          closed/open/half-open
    route/FallbackChain.java           retry policy skipping 4xx
    fleet/CapacityPlanner.java         replicas, fallback sizing
    guardrail/GuardrailService.java    classify/scrub/validateOutput
    eval/EvalService.java              run/regression/compare
    tenancy/TenantContext.java         auth, quota, scope
    tenancy/QuotaEnforcer.java         limits + weighted fair queue
    tenancy/NamespaceCache.java        tenant-scoped cache keys
    tenancy/IndexIsolation.java        pre-filter enforcement
    sli/SliReport.java                 the platform SLI report
    incident/PlatformIncident.java     incident process + escalation
    integration/QuickstartSdk.java     chat/rag/agent in 20 lines
    Main.java
```

## 2. Model Registry With Logical Names

```java
public record ModelDeployment(String provider, String model, String version,
                              Set<Capability> capabilities, boolean supportsTools,
                              boolean supportsJsonMode, int maxContext,
                              Slos slos, double costPer1kTokens, Health health) {}

public enum Capability { TEXT, VISION, AUDIO, LONG_CONTEXT, FUNCTION_CALLING }

public final class ModelRegistry {

    private final Map<String, List<ModelDeployment>> byLogicalName = new LinkedHashMap<>();

    public void register(String logicalName, ModelDeployment d) {
        byLogicalName.computeIfAbsent(logicalName, k -> new ArrayList<>()).add(d);
    }

    /** Product code asks for "chat-quality"; the platform decides what that is today. */
    public Optional<ModelDeployment> resolve(String logicalName) {
        return byLogicalName.getOrDefault(logicalName, List.of()).stream()
                .filter(d -> d.health() == Health.HEALTHY)
                .findFirst();
    }

    /** Re-pointing a logical name is a platform change with zero product code change. */
    public void promote(String logicalName, ModelDeployment d) {
        byLogicalName.compute(logicalName, (k, v) -> {
            List<ModelDeployment> next = new ArrayList<>(v == null ? List.of() : v);
            next.removeIf(x -> x.version().equals(d.version()));
            next.add(0, d);
            return next;
        });
    }
}
```

`promote` putting the new deployment at index 0 and `resolve` filtering on health is
the whole abstraction: swapping models and failing over are both list operations.

## 3. Router

```java
public final class Router {

    public record Request(String logicalName, Set<Capability> needs, QualityTier tier,
                          LatencyTier latency, String region, String tenant, double costCeiling) {}

    public ModelDeployment route(Request r) {
        return registry.resolve(r.logicalName())
            .filter(d -> d.capabilities().containsAll(r.needs()))
            .filter(d -> d.supportsTools() || !r.needs().contains(Capability.FUNCTION_CALLING))
            .filter(d -> d.costPer1kTokens() <= r.costCeiling())
            .filter(d -> regionAllows(d, r.region()))
            .filter(d -> breakers.get(r.logicalName()).allowRequest())
            .or(() -> fallbackFor(r))                 // ordered fallback chain
            .orElseThrow(() -> new NoCapacityException(r.logicalName()));
    }
}
```

`containsAll(r.needs())` rather than `contains` is the bug that would let a text-only
request land on a vision-only model. Capabilities are a *superset* requirement.

## 4. Circuit Breaker

```java
public final class CircuitBreaker {

    public enum State { CLOSED, OPEN, HALF_OPEN }

    private final int failureThreshold;      // e.g. 5
    private final int minCalls = 20;         // do not evaluate before this
    private final Duration openDuration;
    private final int halfOpenTrials = 3;
    private volatile State state = State.CLOSED;
    private final Deque<Boolean> recent = new ArrayDeque<>();
    private int halfOpenSuccesses;

    public boolean allowRequest() {
        return switch (state) {
            case CLOSED    -> true;
            case OPEN      -> false;
            case HALF_OPEN -> halfOpenSuccesses < halfOpenTrials;
        };
    }

    public synchronized void record(boolean success, Instant now) {
        if (state == State.HALF_OPEN) {
            if (success && ++halfOpenSuccesses >= halfOpenTrials) {
                state = State.CLOSED; recent.clear();
            } else if (!success) {
                state = State.OPEN;
            }
            return;
        }
        if (!success) recent.addLast(false); else recent.addLast(true);
        if (recent.size() > failureThreshold) recent.removeFirst();
        if (recent.size() >= minCalls) {                    // minCalls guard
            long failures = recent.stream().filter(b -> !b).count();
            if (failures / (double) recent.size() > 0.5 && state == State.CLOSED) {
                state = State.OPEN;
                reopenAt = now.plus(openDuration);
            }
        }
    }

    public synchronized void tick(Instant now) {
        if (state == State.OPEN && !now.isBefore(reopenAt)) {
            state = State.HALF_OPEN;
            halfOpenSuccesses = 0;
        }
    }
}
```

The `minCalls = 20` guard is what stops the spurious-trip problem from MATH section 7:
without it, three failures in a quiet period trip the breaker on a model that is fine.

## 5. Fallback Chain With Correct Retry Policy

```java
public final class FallbackChain {

    /**
     * Retry timeouts and 5xx. NEVER retry 4xx: the request is malformed and will
     * fail identically, so retrying just burns capacity and latency budget.
     */
    public static boolean retryable(int status, Throwable t) {
        if (t instanceof TimeoutException || t instanceof IOException) return true;
        if (status >= 500) return true;
        if (status == 429) return true;                       // rate limited: back off
        return false;                                          // 400/401/403/404/422
    }

    public Response call(List<ModelDeployment> chain, Request r, int maxAttempts) {
        Throwable last = null;
        for (ModelDeployment d : chain) {
            for (int a = 0; a < maxAttempts; a++) {
                try {
                    Response resp = invoke(d, r);
                    if (resp.status() < 300) return resp;
                    if (!retryable(resp.status(), null)) break;   // do not retry
                    last = new HttpStatus(resp.status());
                } catch (Exception e) {
                    if (!retryable(0, e)) break;
                    last = e;
                }
                backoff(a);
            }
        }
        throw new AllAttemptsFailed(last);
    }
}
```

The `break` out of the retry loop on non-retryable status matters as much as the retry
itself: a stream of 400s from a misconfigured tenant can otherwise consume the whole
request budget of every model in the chain.

## 6. Capacity Planner

```java
public final class CapacityPlanner {

    public record Plan(int primaryReplicas, int fallbackReplicas,
                       double targetUtilization, double peakRps, String note) {}

    public static Plan size(double peakRps, double serviceRatePerReplica,
                            double targetUtilization, double degradedShare) {
        int primary = (int) Math.ceil(peakRps / (serviceRatePerReplica * targetUtilization));
        int fallback = (int) Math.ceil(peakRps * degradedShare
                                      / (serviceRatePerReplica * targetUtilization));
        return new Plan(primary, fallback, targetUtilization, peakRps,
                "fallback serves %.0f%% of peak at degraded quality (measured)".formatted(degradedShare * 100));
    }

    /**
     * Erlang-C: fraction of arrivals that WAIT. At high rho this is what drives p95,
     * not the service time.
     */
    public static double erlangC(double offeredLoad, int servers) {
        if (offeredLoad >= servers) return 1.0;
        double aN = 0, term = 1;
        for (int n = 1; n <= servers; n++) {
            term *= offeredLoad / n;
            aN += term;
        }
        return term / (1 - term + aN);                 // simplified Erlang-C
    }
}
```

Returning `erlangC` alongside the replica count makes the report answer the question
people actually ask — "why is p95 higher than p50 by so much?" — with queueing rather
than guesswork.

## 7. Prompt Registry

```java
public record PromptVersion(String promptId, int version, String template,
                            Map<String, Type> variables, String owner, RiskTier riskTier,
                            String changelog, String templateHash, Instant created) {}

public final class PromptRegistry {

    private final Map<String, List<PromptVersion>> versions = new LinkedHashMap<>();

    public String render(String promptId, int version, Map<String, Object> vars) {
        PromptVersion v = get(promptId, version);
        String out = renderTemplate(v.template(), vars);
        assertNoUnfilled(out);                                  // Lab 03 invariant
        assertTypes(out, v.variables());                        // typed variables
        return out;
    }

    public void promote(String promptId, int version, GateResult gate) {
        if (!gate.passed()) throw new IllegalStateException(
                "prompt " + promptId + "@v" + version + " failed the gate");
        active.merge(promptId, version, (old, candidate) -> gate.canary() ? candidate : old);
    }

    private static void assertNoUnfilled(String rendered) {
        if (PLACEHOLDER.matcher(rendered).find())
            throw new IllegalStateException("unfilled placeholder reached the model");
    }
}
```

`promote` refusing a version whose gate failed is the mechanism that makes "every
prompt change is a release" real rather than aspirational.

## 8. Guardrail Service

```java
public final class GuardrailService {

    public record Policy(Set<Category> enabled, double blockThreshold, RiskTier tier) {}

    public Verdict classify(String text, TenantContext tenant) {
        Policy p = tenant.policy();                            // per-tenant overrides
        for (Category c : p.enabled()) {
            double score = classifiers.get(c).score(text);
            if (score >= p.blockThreshold()) return Verdict.block(c, score);
        }
        return Verdict.allow();
    }

    /** Products may tighten (raise thresholds, add categories); disabling requires approval. */
    public Policy tighten(Policy base, Policy requested, Approval approval) {
        Set<Category> enabled = new TreeSet<>(base.enabled());
        enabled.addAll(requested.enabled());                   // monotone: only add
        double threshold = Math.min(base.blockThreshold(), requested.blockThreshold());
        if (!requested.enabled().containsAll(base.enabled()) && !approval.granted())
            throw new ApprovalRequired("disabling a platform guardrail category");
        return new Policy(Set.copyOf(enabled), threshold, base.tier());
    }
}
```

`tighten` is monotone by construction: you can only add categories or lower
thresholds. Removing a guardrail is not a permission the API can grant.

## 9. Tool Registry Contract

```java
public record ToolSpec(String toolId, String version, String owner, JsonSchema input,
                       JsonSchema output, AuthModel auth, SideEffect sideEffect,
                       Duration timeout, RetryPolicy retry, ApprovalPolicy approval) {}

public enum SideEffect { READ, REVERSIBLE_WRITE, IRREVERSIBLE_WRITE }

public void register(ToolSpec spec) {
    if (spec.owner() == null || spec.owner().isBlank())
        throw new IllegalArgumentException("a tool must have an owner: " + spec.toolId());
    if (spec.sideEffect() == SideEffect.IRREVERSIBLE_WRITE && spec.approval() == null)
        throw new IllegalArgumentException("irreversible tool needs an approval policy");
    contractTests.verify(spec);                               // Exercise 22 / Stretch I
    tools.put(spec.toolId(), spec);
}
```

Requiring an owner and, for irreversible tools, an approval policy means a tool cannot
be registered in a state where nobody is accountable for it.

## 10. Eval Service

```java
public final class EvalService {

    public EvalReport run(ReleaseManifest manifest, String suiteId) {
        var items = suites.get(suiteId).items();
        var results = items.stream().map(i -> scorer.score(i, runtime.invoke(manifest, i)))
                                 .toList();
        return new EvalReport(manifest.hash(), suiteId, items.size(),
                              PerCategory.of(results), SafetyMetrics.of(results),
                              CostMetrics.of(results));
    }

    public Diff regression(String suiteId, String baselineManifestHash) {
        EvalReport now = run(currentManifest(), suiteId);
        EvalReport base = reports.get(baselineManifestHash + ":" + suiteId);
        return now.perCategory().diff(base.perCategory());     // per category, threshold flagged
    }
}
```

Attaching the manifest hash to the report means the report itself says which
configuration produced it — the Lab 14 discipline applied to evaluation output.

## 11. Tenant-Scoped Cache

```java
public final class NamespaceCache {

    public Optional<String> lookup(TenantContext t, String prefixHash) {
        return inner.get(key(t, prefixHash));
    }

    public void store(TenantContext t, String prefixHash, String response) {
        inner.put(key(t, prefixHash), response);
    }

    /** Tenant is part of the key, not a filter applied afterwards. */
    private String key(TenantContext t, String prefixHash) {
        return t.tenantId() + "|" + t.authzScope() + "|" + prefixHash;
    }

    /** Exercise 11: remove the tenant from key() and the leak test must fail. */
    static void assertNoCrossTenantLeak(NamespaceCache c, List<TenantContext> tenants) {
        for (TenantContext a : tenants)
            for (TenantContext b : tenants) {
                if (a.tenantId().equals(b.tenantId())) continue;
                c.store(a, "shared", "SECRET-A");
                if (c.lookup(b, "shared").isPresent())
                    throw new AssertionError("cross-tenant cache leak");
            }
    }
}
```

The test helper is shipped with the class on purpose: this bug is invisible in review
and only shows up as a security incident.

## 12. Quota Enforcer With Fair Queueing

```java
public final class QuotaEnforcer {

    public record Decision(boolean allow, String reason) {}

    public Decision check(TenantContext t, Request r) {
        Usage u = usage.get(t.tenantId());
        if (u.requestsToday() >= t.quota().requestsPerDay())
            return new Decision(false, "DAILY_REQUEST_QUOTA");
        if (u.tokensThisMinute() + estimateTokens(r) > t.quota().tokensPerMinute())
            return new Decision(false, "TOKEN_RATE_LIMIT");
        if (u.concurrent() >= t.quota().maxConcurrent())
            return new Decision(false, "CONCURRENCY_LIMIT");
        double projected = u.spendToday() + projectCost(r);
        if (projected > t.quota().costBudget())
            return new Decision(false, "COST_BUDGET");       // projected, not actual
        return new Decision(true, "OK");
    }
}
```

Checking the cost budget on the **projected** cost rather than the settled cost is what
stops a single large request from blowing the monthly budget in one call.

## 13. Dependency Direction Check

```java
public final class LayerDependencyCheck {

    /** Lower layers must never import higher ones. Verifies by walking imports. */
    public static List<String> violations(Map<String, Set<String>> importsByModule) {
        var violations = new ArrayList<String>();
        importsByModule.forEach((module, deps) -> {
            int from = layer(module);
            deps.forEach(dep -> {
                if (layer(dep) > from)
                    violations.add("%s (L%d) imports %s (L%d)"
                            .formatted(module, from, dep, layer(dep)));
            });
        });
        return violations;
    }
}
```

A build-time check of this kind is cheap and catches the coupling that turns a
platform into a monolith. It also fails loudly on the deliberately violating import
from Exercise 17, which is how you know the check works.

## 14. SLI Report

```java
public record SliReport(Interval window, Map<String, Double> availability,
                        Map<String, Percentiles> latency, Map<String, Double> throughput,
                        Map<String, Double> qualityPassRate, Map<String, Double> costPerRequest,
                        Duration indexFreshness, double rollbackRate,
                        AdoptionFunnel adoption) {}

/** The SLI most teams forget: can a new team ship? */
public record AdoptionFunnel(int requested, int quickstarted, int passedFirstEval,
                             int shippedProduction, int stillShippingAt90d,
                             Duration medianTimeToFirstSuccess) {

    public Map<String, Double> conversion() {
        return Map.of(
                "quickstart", rate(quickstarted, requested),
                "first_eval", rate(passedFirstEval, quickstarted),
                "production", rate(shippedProduction, passedFirstEval),
                "retained_90d", rate(stillShippingAt90d, shippedProduction));
    }

    /** The stage with the largest drop is where to invest. */
    public String biggestDrop() {
        var c = conversion();
        return c.entrySet().stream().min(Map.Entry.comparingByValue()).map(Map.Entry::getKey)
                .orElse("none");
    }
}
```

`biggestDrop` turns adoption into an actionable metric rather than a vanity count.

## 15. Quickstart SDK

```java
public final class AiPlatform {

    public static AiPlatform connect() { return connectFromEnv(); }

    public String chat(String prompt) {
        return retrying(() -> router.route(Request.basic(prompt)));   // telemetry automatic
    }

    public String rag(String question) {
        var hits = retrieval.search(question, topK(5));
        var ctx = ContextPacker.pack(question, hits, budget());
        var resp = chat("Answer from sources:\n" + ctx.rendered());
        if (!CitationChecker.valid(resp, ctx)) throw new GroundingFailure(resp);
        return resp;
    }

    public String agent(String goal) {                                   // Lab 05 runtime
        return new Agent(router, toolRegistry(), budgets()).run(goal).text();
    }
}
```

Every call carries telemetry and retries because they are inside the SDK, not in
consumer code. That is the adoption argument: the platform's correctness properties
come for free with the call.

## Self-Check

1. Why does `promote` insert at index 0 instead of appending?
2. What does the `minCalls` guard prevent in the breaker?
3. Why break the retry loop on a 4xx instead of continuing to the next model?
4. Why is the tenant in the cache key rather than filtered afterwards?
5. Why check `projectedCost` rather than settled cost for quota enforcement?