# SIEM & Monitoring - REAL WORLD PROJECT

## Project: SentinelGrid — a detection programme for a 60-service production estate

Logs exist everywhere; nobody can say whether an attack would be caught. The programme
turns that into a measured capability: a detection catalogue with owners, tests, coverage
mapping against a technique list, and a tuning loop driven by measured false-positive rates.

### Architecture

```
  60 services / infra / cloud / network
        │  unified schema (OTel + ECS-aligned fields), correlation_id everywhere
        ▼
  Collectors ──> Normalise ──> Hot store (7d, fast)  ──┬──> Detections ──> Alert queue
        │                      Cold store (400d, cheap)│        │
        │                                              │        ├──> Tier1 analyst
        │                                              │        └──> PagerDuty (crit only)
        │                                              ▼
        │                                    SOAR: enrich, dedupe, auto-contain low-risk
        ▼
  Detection-as-code repo ──> CI: schema lint, rule lint, fixture tests ──> deploy
        │
        ▼
  Coverage report: technique x detection, gaps tracked as engineering backlog
```

### Implementation

Detection-as-code with linting and fixture tests in CI, because a rule deployed without a
test is a production liability:

```java
public class RulePipeline {
    /** CI gates, in order. A rule that fails any of these never reaches production. */
    public GateResult evaluate(Rule rule, List<Event> fixture) {
        List<String> problems = new ArrayList<>();

        // 1. Schema lint: every field the rule references must exist in the schema.
        problems.addAll(schemaLinter.check(rule.referencedFields()));

        // 2. Owner and playbook: a rule nobody owns is a rule nobody will maintain.
        if (rule.owner() == null || rule.owner().isBlank()) problems.add("missing owner");
        if (rule.playbook() == null) problems.add("missing playbook - unroutable alert");

        // 3. Fixture tests: must fire on the attack fixture and stay silent on the benign one.
        TestResult attack = execute(rule, fixtures.forScenario(rule.id(), ATTACK));
        if (attack.alerts().isEmpty()) problems.add("does not fire on its own attack fixture");
        TestResult benign = execute(rule, fixtures.forScenario(rule.id(), BENIGN));
        if (benign.alerts().size() > 0)
            problems.add("false positive on benign fixture: " + benign.alerts().size());

        // 4. Blast-radius check: simulate 7 days of production volume and measure the alert count.
        Simulation sim = simulate(rule, productionSample(7, DAYS));
        if (sim.alertsPerDay() > rule.maxAlertsPerDay())
            problems.add("projected " + sim.alertsPerDay() + " alerts/day, budget is " + rule.maxAlertsPerDay());
        if (sim.uniqueAlertsPerDay() < 1)
            problems.add("never fires against 7 days of production data - is it reachable?");

        return problems.isEmpty() ? GateResult.PASS : GateResult.BLOCK(problems);
    }
}
```

The tuning loop, driven by measured outcomes rather than opinions:

```java
@Service
class DetectionTuningService {
    // Every alert closes as: true_positive, false_positive, or benign_variant.
    // Rules whose FP rate exceeds budget are auto-suggested for tuning, not defended by owners.
    @Scheduled(cron = "0 0 6 * * *")
    void weeklyTuningReview() {
        for (Rule r : catalogue.productionRules()) {
            Stats s = outcomes.forRule(r.id(), Duration.ofDays(7));
            double fpRate = s.falsePositives() / (double) Math.max(1, s.total());
            if (fpRate > r.fpBudget()) {
                backlog.createTask("TUNE", r.id(),
                    "FP rate " + pct(fpRate) + " over budget " + pct(r.fpBudget())
                    + ". Top false-positive values: " + s.topFpValues(5));
            }
            if (s.total() == 0) {
                // A rule that has not fired in 30 days is either misconfigured or no longer relevant.
                backlog.createTask("REVIEW_SILENT_RULE", r.id(), "no alerts in 30 days");
            }
        }
    }
}
```

SOAR handles the automatable responses, with every automated action bounded and reversible:

```java
@Component
class ContainmentPlaybooks {
    /**
     * Automation is graded by reversibility and blast radius:
     *   AUTO  - read-only enrichment (threat intel lookup, asset owner lookup)
     *   AUTO  - reversible containment (disable a token, add an IP to a deny list with a TTL)
     *   HUMAN - anything destructive (revoke all sessions for a tenant, block a customer)
     */
    void onCredentialStuffing(Alert a) {
        var ip = a.groupValue(0);
        if (threatIntel.isKnownMalicious(ip)) {
            network.deny(ip, Duration.ofHours(6));          // reversible, TTL-bounded
            audit.recordAction("AUTO_DENY_IP", ip, "6h", a.id());
        }
        var account = assetOwner.forIp(ip);
        notify.socTier1(a, account);                        // a human still owns the response
    }

    void onImpossibleTravel(Alert a) {
        // Never auto-lock a legitimate user on travel evidence alone: revoke the session,
        // force re-auth with MFA, and let a human decide.
        sessions.revoke(a.userId());
        mfa.requireNextLogin(a.userId());
        notify.socTier2(a);
    }
}
```

### Non-functional requirements

- **Coverage**: map detections to a technique catalogue quarterly; every gap becomes a
  backlog item with an owner. Report coverage honestly, including known blind spots.
- **Signal quality**: alert volume target under 5,000/week across the estate, with a
  true-positive rate above 30% per critical/high rule. Both are leadership metrics.
- **Latency**: critical detections page within 5 minutes of the event.
- **Reliability**: detector failures must not drop events — buffered shipping with
  replay, and a visible "detection blind window" when a pipeline is down.
- **Data**: 7 days hot, 400 days cold, with an explicit retention decision per log class;
  access to security logs is itself audited and restricted.
- **Cost**: tiered storage and query-driven retention, since "keep everything searchable"
  is the line item that kills a SIEM budget.
- **People**: runbooks per rule, a shift handover process, and quarterly game days that
  exercise the rules rather than just the response process.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- MITRE ATT&CK provides the technique and tactic taxonomy used for the coverage mapping
  that turns "we have alerts" into a measurable detection capability.
  https://attack.mitre.org/
- OWASP Logging Cheat Sheet specifies which security events to record and the fields
  required, which shaped the unified event schema and its CI linting.
  https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html

## Deliverables

- [x] Unified event schema with CI schema linting and correlation IDs
- [x] Detection-as-code repo with rule lint, fixture tests, and simulated volume gates
- [x] Every rule requires an owner and a linked playbook before promotion
- [x] Coverage report against a technique catalogue with tracked gaps
- [x] Weekly auto-tuning loop creating backlog items for over-budget false-positive rates
- [x] Silent-rule review for rules that have not fired in 30 days
- [x] Graded SOAR automation: read-only, reversible, and human-gated actions separated
- [x] Reliability: buffered shipping, replay, and visible detection blind windows
- [ ] Quarterly game day exercising detections end to end, not just the response process
