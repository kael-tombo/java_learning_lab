# SIEM & Monitoring - MINI PROJECT

## Project: Watchtower — detection-as-code with tests, metrics, and a simulated attacker

Build a small detection pipeline: structured event schema, correlation rules as versioned
code, unit tests against fixtures, and a simulation that proves rules fire on attack and
stay quiet on normal traffic.

### Architecture

```
  Services ──> JSON logs (stable schema + correlation_id)
                    │
                    ▼
             Collector ──> Normaliser ──> Event store (queryable)
                                              │
  rules/ (YAML, versioned)                     │
      ├── 001-auth-burst.yaml                  │
      ├── 002-impossible-travel.yaml           │
      ├── 003-admin-role-granted.yaml          │
      └── 004-token-algorithm-anomaly.yaml     │
                    │                           ▼
                    └──> Rule test suite ──> deploy ──> Alerts ──> triage queue
                              (fixtures)
```

### Implementation

The event schema, designed for querying rather than for reading:

```java
/** One schema, enforced. A field name that varies is a field you cannot correlate on. */
public record SecurityEvent(
    @JsonProperty("ts")        Instant timestamp,
    @JsonProperty("event_id")  String eventId,          // ULID: sortable, unique
    @JsonProperty("schema")    String schemaVersion,   // "auth.login.v2"
    @JsonProperty("service")   String service,
    @JsonProperty("env")       Environment env,        // prod/staging - filters staging noise
    String action,               // login_success | login_failure | role_grant | ...
    Outcome outcome,             // SUCCESS | FAILURE | DENIED
    @JsonProperty("actor")     Actor actor,            // userId, ip, userAgent, asn
    @JsonProperty("target")    Map<String,Object> target,
    @JsonProperty("correlation_id") String correlationId,  // ties a whole request together
    Map<String,Object> detail) {}

public record Actor(String userId, String ip, String userAgent, String deviceId, Integer asn) {}
```

The service emits security-relevant events as a side effect of real authorisation decisions,
so detections are grounded in the truth rather than inferred from access logs:

```java
@Component
class SecurityEventPublisher {
    private final SecurityEventSink sink;

    public void recordLoginFailure(Authentication attempt, String reason) {
        sink.publish(new SecurityEvent(
                Instant.now(), ULID.random().toString(), "auth.login.v2",
                "orders-api", currentEnv(), "login_failure", Outcome.FAILURE,
                Actor.of(attempt.username(), attempt.remoteAddr(), attempt.userAgent(), null, geo.asnOf(attempt.remoteAddr())),
                Map.of("tenant", tenantOf(attempt), "reason", reason), MDC.get("correlationId"),
                Map.of("method", "password", "mfa", attempt.mfaPresent())));
    }

    /** Denials are logged from the policy engine, so we see authorization probing too. */
    public void recordAuthorizationDenial(Subject s, String action, Resource r, String reason) {
        sink.publish(new SecurityEvent(Instant.now(), ULID.random().toString(), "authz.denied.v1",
                "orders-api", currentEnv(), "authz_deny", Outcome.DENIED,
                Actor.of(s.userId(), s.ip(), s.userAgent(), null, null),
                Map.of("action", action, "resource_type", r.type(), "tenant", s.tenantId()),
                MDC.get("correlationId"), Map.of("reason", reason)));
    }
}
```

A correlation rule, with a test, as code:

```yaml
# rules/001-auth-burst.yaml
id: AUTH-BURST-001
title: Credential stuffing / password spraying against a single tenant
status: production
severity: high
schedule: "*/5 * * * *"
data:
  - index: security-events
    timeframe: 5m
    filter:
      schema: auth.login.v2
      env: prod                      # staging noise must not page anyone
      outcome: FAILURE
  threshold: field>account.actor.ip, count>20
  # Aggregation matters: 20 failures from one IP is an attack; 20 from 20 IPs is normal.
  group_by: [account.actor.ip, account.target.tenant]
  suppression:
    # One alert per (source, tenant) per 30 minutes. A sustained attack does not page 288 times/day.
    key: [account.actor.ip, account.target.tenant]
    window: 30m
filter:
  # Exclude known-benign automated clients, with an owner and a review date.
  - NOT account.actor.userAgent: (Approved) scanner-okta/1.0
composite:
  second_condition:                       # require a SUCCESS in the same window: real progress
    index: security-events
    timeframe: 5m
    filter: { schema: auth.login.v2, env: prod, outcome: SUCCESS, action: login_success }
    match: { field: account.actor.ip, operator: equals, value: "{{rule_1.group_values.0}}" }
action:
  severity: high
  route: [soc-tier1, pagerduty-security]
  playbook: playbook-credential-stuffing
  enrich: [threat_intel_ip, asset_owner]
```

The test suite, which is the difference between a rule and a guess:

```java
class AuthBurstRuleTest {
    // 1. FIRES: 25 failures then a success from one IP, one tenant, in 5 minutes.
    @Test
    void firesOnCredentialStuffing() {
        List<SecurityEvent> events = fixture("stuffing-attack-2026-10.jsonl");
        var result = engine.execute(rule("AUTH-BURST-001"), events);
        assertThat(result.alerts()).hasSize(1);
        assertThat(result.alerts().get(0).severity()).isEqualTo(HIGH);
        assertThat(result.alerts().get(0).groupValues()).contains("203.0.113.45");
    }

    // 2. SILENT: 25 failures spread across 25 different IPs (no single-source attack).
    @Test
    void silentOnDistributedNoise() {
        assertThat(engine.execute(rule("AUTH-BURST-001"), fixture("many-ips-many-failures.jsonl")).alerts()).isEmpty();
    }

    // 3. SILENT: staging traffic never pages.
    @Test
    void silentInStaging() {
        assertThat(engine.execute(rule("AUTH-BURST-001"), fixture("staging-burst.jsonl")).alerts()).isEmpty();
    }

    // 4. SUPPRESSED: 40 failures on one IP inside the window produce ONE alert, not 40.
    @Test
    void suppressesRepeatAlerts() {
        var alerts = engine.execute(rule("AUTH-BURST-001"), fixture("sustained-attack.jsonl")).alerts();
        assertThat(alerts).hasSize(1);
        assertThat(alerts.get(0).suppressedCount()).isEqualTo(39);
    }

    // 5. Metrics the programme is judged on.
    @Test
    void everyRuleDeclaresAnOwnerAndTest() {
        for (Rule r : rules.all()) {
            assertThat(r.owner()).isNotBlank();
            assertThat(r.playbook()).isNotBlank();       // a rule with no playbook is noise
            assertThat(coverage.has(r.id())).isTrue();
        }
    }
}
```

### Test It

```java
@Test void impossibleTravelFiresOnRealTravel() {
    // Two successful logins 40 minutes apart from London then Singapore.
    var alerts = engine.execute(rule("AUTH-TRAVEL-002"), fixture("travel-impossible.jsonl")).alerts();
    assertThat(alerts).hasSize(1);
    assertThat(alerts.get(0).detail()).contains("impossible_travel", "distance_km");
}

@Test void vpnEgressDoesNotFalsePositive() {
    // Corporate VPN egress IPs are declared, with an owner and a review date.
    assertThat(engine.execute(rule("AUTH-TRAVEL-002"), fixture("travel-vpn.jsonl")).alerts()).isEmpty();
}

@Test void detectionCoverageIsMeasured() {
    // Map rules to a technique list; uncovered techniques are a roadmap, not a secret.
    var coverage = coverageReport.against(mitreTechniques());
    assertThat(coverage.uncovered()).contains("T1078.004 cloud accounts");  // known gap, tracked
    assertThat(coverage.percentCovered()).isGreaterThan(60.0);
}
```

## Deliverables

- [ ] Versioned `SecurityEvent` schema with correlation IDs and documented fields
- [ ] Service instrumentation publishing login, authorization, and privilege-change events
- [ ] At least four correlation rules as YAML in version control
- [ ] Aggregation and suppression so a sustained attack yields one actionable alert
- [ ] Rule test suite with real event fixtures: fires on attack, silent on noise
- [ ] Rule metadata requiring an owner and a linked playbook
- [ ] Detection coverage report against a technique list, with known gaps tracked
- [ ] Metrics: alerts per day, true-positive rate, mean time to acknowledge
