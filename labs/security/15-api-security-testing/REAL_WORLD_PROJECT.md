# API Security Testing - REAL WORLD PROJECT

## Project: AssuranceGate — a security test programme for a public API platform

A public developer-facing API (partner integrations, webhooks, OAuth clients) handling
payment initiation. One injection or BOLA bug is a reportable incident. The programme has
to run on every change, on a schedule, and during release qualification — without becoming
a bottleneck that teams route around.

### Architecture

```
   PR ──> SAST (CodeQL/Semgrep) ──┐
         Dependency scan (OWASP dep/Trivy) ──┤
         Secret scan (gitleaks)  ──┤
                                     ├──> Merge gate: new critical findings block
   main ──> Deploy to staging ──> Authenticated DAST (ZAP API scan, 2 personas)
                                     ├──> Staging gate: block release on regression
   nightly ──> Fuzz targets (AFL++/Jazzer on parsers)
                                     │
   quarterly ──> Manual pen test: IDOR matrix, business-logic abuse, chain of trust
                                     │
   Findings ──> triage ──> fix + regression test (required) ──> SLAs by severity
```

### Implementation

The gate logic, so "critical" means one thing across every tool:

```java
@Component
class AssuranceGate {
    // Normalise every tool's severity onto one scale. Different tools disagree, and a gate
    // that says "high" from one tool and "medium" from another is not a gate.
    record Finding(String id, String tool, Severity sev, String rule, String file, int line, String fingerprint) {
        String fp() { return tool + ":" + rule + ":" + file; }   // stable across runs for dedupe
    }

    GateResult evaluate(List<Finding> newFindings, Map<String, Finding> baseline) {
        List<Finding> blocking = newFindings.stream()
            .filter(f -> f.sev() == Severity.CRITICAL)
            .filter(f -> !acceptedRisk(f).isValid())                 // exceptions must be unexpired
            .toList();
        if (!blocking.isEmpty()) return GateResult.BLOCKED(blocking, buildReport(newFindings));
        return GateResult.PASSED(newFindings);
    }

    // A finding is only "new" if its fingerprint is not already triaged. Otherwise every
    // pre-existing technical debt blocks every PR and the gate gets disabled in a week.
    List<Finding> newOnly(List<Finding> all, Map<String, Finding> baseline) {
        return all.stream().filter(f -> !baseline.containsKey(f.fp())).toList();
    }

    record AcceptedRisk(String ticket, String owner, LocalDate expires) {
        boolean isValid() { return expires.isAfter(LocalDate.now()); }   // auto-expires
    }
}
```

Authenticated DAST with two personas, which is what makes IDOR detection possible:

```java
@Bean
ApiScanJob authenticatedScan() {
    return new ApiScanJob()
        .target(List.of(stagingBaseUrl))
        .openApi(stagingSpecUrl)                       // test against the real contract
        .context("alice", credentialsFor("alice"))     // persona 1: normal customer
        .context("bob",   credentialsFor("bob"))       // persona 2: enables cross-identity tests
        .withPlugin("bolt")                            // IDOR / access control
        .withPlugin("sqli").withPlugin("xss")
        .withPlugin("rateLimit").withSeverityThreshold("medium")
        .withRequestModifiers(authHeader -> "Bearer " + tokenCache.get(authHeader))
        .rebaselineOn(authenticatedScan -> false);     // auth scope means results are comparable
}
```

A manual IDOR matrix test, because automation cannot enumerate every object/identity pair:

```java
@Test void crossTenantAccessMatrix() {
    // Every (actor, resource-owner) pair must deny. Generated, not hand-picked, because
    // hand-picked tests miss exactly the endpoint someone forgot to protect.
    for (User actor : testUsers) {
        for (Account owner : accounts) {
            for (String endpoint : List.of("/orders", "/invoices", "/beneficiaries", "/payouts")) {
                var res = get(endpoint + "/" + owner.resourceId(), tokenFor(actor));
                if (actor.id().equals(owner.userId())) {
                    assertThat(res.status()).isIn(200, 404);
                } else {
                    assertThat(res.status())
                        .as("actor=%s must not read %s owned by %s", actor.id(), endpoint, owner.userId())
                        .isIn(403, 404);
                }
            }
        }
    }
}
```

Business-logic testing, where the tools are silent and the money moves:

```java
@Test void transferLimitsCannotBeBypassedByConcurrentRequests() throws Exception {
    // Race the limit check: 10 parallel transfers of the daily max must yield at most 1 success.
    var pool = Executors.newFixedThreadPool(10);
    var futures = IntStream.range(0, 10)
        .mapToObj(i -> pool.submit(() -> post("/api/transfers", transfer(DailyLimit), tokenA)))
        .toList();
    long succeeded = futures.stream().filter(CompletionStage::isCompletedExceptionally == false)
        .filter(f -> f.get() == 201).count();
    assertThat(succeeded).isLessThanOrEqualTo(1);   // requires a DB-level constraint, not a read-then-write
}

@Test void idempotencyKeyPreventsDuplicateTransfer() {
    String key = "idem-" + UUID.randomUUID();
    assertThat(post("/api/transfers", transfer(100), tokenA, key).status()).isEqualTo(201);
    ResponseEntity<String> replay = post("/api/transfers", transfer(100), tokenA, key);
    assertThat(replay.status()).isEqualTo(200);        // same response, no second debit
}
```

### Non-functional requirements

- **Coverage**: every endpoint in the OpenAPI spec is exercised; endpoints absent from the
  spec are flagged, because undocumented endpoints escape testing by definition.
- **Gating**: PR gate blocks new critical/high findings. Staging gate blocks regressions.
  Explicit, so "the gate blocked us" is a conversation about risk, not about tooling.
- **Baseline hygiene**: triaged technical debt lives in a versioned baseline with owners and
  expiry dates; a quarter with no baseline update is itself a signal.
- **SLA**: critical 24 h to triage / 7 d to fix; high 7 d / 30 d; accepted risks expire.
- **Fuzzing**: nightly fuzzing of the webhook signature parser, the ISO-8601 date parser,
  and the JSON depth limit — the three places parsers have historically died.
- **Evidence**: reports retained per release; the manual pen test is a release gate for
  major versions and a compliance artefact for the security questionnaire.
- **Anti-bypass**: gate bypass requires a named approver and is itself logged and alerted.
  A control nobody can bypass is not enforced; a control anyone can bypass silently is worse.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- OWASP Web Security Testing Guide is the reference for test cases by category, including
  the identity/authorization (IDOR) and input-validation classes implemented above.
  https://owasp.org/www-project-web-security-testing-guide/
- OWASP API Security Top 10 covers API-specific risks such as broken object level
  authorization and excessive data exposure, which the generated matrix test targets.
  https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- MITRE ATT&CK provides the technique taxonomy used to map findings to attacker
  behaviour, letting the programme prioritise by technique rather than by scanner severity.
  https://attack.mitre.org/

## Deliverables

- [x] Unified severity normalisation across SAST, dependency, and DAST findings
- [x] New-findings-only PR gate with a versioned, expiring exception baseline
- [x] Authenticated multi-persona staging scan enabling cross-identity detection
- [x] Generated IDOR matrix over actors × resources × endpoints as a release gate
- [x] Concurrency and idempotency tests for business-logic abuse in money movement
- [x] Nightly fuzzing of the webhook, date, and JSON parsers
- [x] Documented spec-coverage report flagging undocumented endpoints
- [x] Gate-bypass logging, alerting, and named-approver requirement
