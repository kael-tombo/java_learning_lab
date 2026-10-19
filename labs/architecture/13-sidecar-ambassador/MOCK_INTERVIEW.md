# Mock Interview: What Belongs in a Sidecar

> Probe-list format. A platform with three languages — Java, Go, Python — and one notoriously flaky external partner API. No mesh installed yet; the question is what should leave application code.

---

## Probes

1. "Which concerns move out of the process first?"
   Transport mechanics: certificate rotation between services, endpoint lookup, and per-call timeout policy. No language should own those three times over; they belong to infrastructure once and forever.

2. "What must stay inside the process?"
   Whatever the domain has to answer for: idempotency keys, business-level retries that need to inspect an outcome, and transactional work against the store. A proxy can happily resend a payment nine times; only application logic knows which of those attempts actually charged the card.

3. "What does the extra hop cost?"
   Every call gains a loopback traversal — a fixed slice of latency plus per-pod memory and CPU. Budget it in advance: measure the ninety-ninth percentile with and without the proxy on one canary path. If a latency-critical route regresses, exempt it deliberately and write down why.

4. "The partner API keeps flapping. Does an ambassador help?"
   Enormously — one proxy dedicated to that host delivers pooling, capped retry counts with jitter, and an out-thread circuit state shared by all three languages. Every caller stops re-implementing the same resilience ritual in its own dialect.

5. "The sidecar crashes. What does the app experience?"
   Sudden unreachability that looks like a network partition rather than a process death. Readiness probes must cover the sidecar, so the pod gets replaced instead of lingering as a black hole accepting nothing.

6. "When is an ordinary library the better buy?"
   For an internal tool with two services, a shared client library plus one config file buys the same retries at a fraction of the per-pod cost. Sidecars pay off past a handful of languages, or whenever security policy is managed centrally rather than by app teams.

7. "What does the proxy absorb for observability?"
   Span creation at the wire's edge stitches traces across languages without every runtime learning an exporter. Business-relevant spans remain the application's; transport truths — where a call died, how often it was resent — fall to the proxy.

8. "And when the proxy itself fails?"
   Silence on everything — an app crash shows in logs, a proxy death shows as total quiet. Per-pod synthetic checks that traverse the proxy turn that silence into a signal within seconds, because an invisible dependency is the most expensive one.

9. "Anything you'd keep in app code even with a full mesh?"
   Domain judgement around payments and anything needing local state. Infrastructure answers transport questions; whether a payment may be retried after an ambiguous timeout is a business question with the cardholder's money attached.

10. "Fleet upgrades across all of them?"
   The platform stages it node by node with drains; application teams coordinate nothing, which is the whole benefit stated as an ops plan.

11. "Per-cause transport metrics for the app teams — who publishes them?"
   The proxy: outcome classes per destination, retry counts it added, and connection failures, so an engineer can tell cable trouble from code trouble without reading stack traces.

12. "How do you size capacity for all this extra machinery?"
   It rides the pod, so there is no separate fleet to plan — but readiness must treat proxy health as part of pod health, or every capacity dashboard quietly lies.

---

## Red Flag

Welcoming the proxy because its config offers a retry knob, then moving domain judgement in with it — "should a payment be retried" is not a transport policy, no matter how convenient the placement looks.
