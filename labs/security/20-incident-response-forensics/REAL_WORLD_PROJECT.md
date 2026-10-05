# Incident Response & Forensics - REAL WORLD PROJECT

## Project: BreachRoom — a rehearsed incident response capability for a payment platform

This platform processes card-not-present payments. A breach is a regulatory event with
notification deadlines, so response speed and evidence quality are business concerns, not
just security ones. The capability must work at 3 a.m. on a holiday, involving people who
have never worked together.

### Architecture

```
  Detection (SIEM, EDR, fraud, IdP, cloud)  ──▶  Incident queue with severity triage
                                                       │
                                          ┌────────────┴────────────┐
                                          │  Sev1 / Sev2 routing     │
                                          │  on-call + incident cmd  │
                                          └────────────┬────────────┘
                                                       ▼
                              ┌────────────────────────────────────┐
                              │  War room (single comms channel)    │
                              │  Roles: IC, Comms, Scribe, Ops,    │
                              │         Legal, Eng leads           │
                              └────────────────────────────────────┘
                                                       │
                       ┌───────────────┬───────────────────┼──────────────┐
                       ▼               ▼                   ▼              ▼
                  Contain          Scope/Impact       Evidence          Comms
              (revoke, isolate)  (which merchants,   (custody,        (internal,
                            card data,  which window)  preservation)   regulators)
                                                       │
                                                       ▼
                                          Eradicate ──▶ Rebuild ──▶ Verify
                                                       │
                                                       ▼
                                       Post-mortem (blameless) ──▶ Hardening backlog
```

### Implementation

The first hour is mostly decisions, so they are encoded as a time-boxed runbook rather than
improvised:

```java
@Component
class IncidentOrchestrator {
    // T+0 to T+15: triage and declare. No one should be debating scope before declaring.
    // Declaring early is cheap; declaring late costs the containment window.
    void onHighSeverityDetection(Alert a) {
        if (a.severity() == Severity.CRITICAL && !caseExistsFor(a)) {
            IncidentCase c = cases.declare(a, DeclaredBy(onCallEngineer()), Instant.now());
            comms.openWarRoom(c);                    // one channel; all roles check in
            comms.pageRoles(c, Roles.all());        // IC, comms, scribe, legal, eng leads
            runbook.start(c, Step.TRIAGE);          // every step time-boxed and logged
        }
    }

    /** Triage produces the two facts that determine everything else: scope and window. */
    ScopeAssessment triage(IncidentCase c) {
        var affectedIdentities = identityGraph.identitiesInvolved(c);
        var dataAccessed      = dataAccessMapper.whatWasRead(c);      // which records, which tenants
        var earliest          = timeline.earliestConfirmedEvent(c);
        var latest            = timeline.latestConfirmedEvent(c);
        return new ScopeAssessment(affectedIdentities, dataAccessed, earliest, latest,
                cardDataInvolved: dataAccessed.any(CardData::present));
    }
}
```

Card data triggers a parallel regulatory track with hard deadlines, so the runbook branches:

```java
@Service
class ComplianceTrack {
    /**
     * Payment card data involvement changes the response shape: the legal track starts
     * immediately and in parallel with containment, because the clock and the required
     * notifications are independent of when engineering finishes eradicating.
     */
    void evaluate(IncidentCase c, ScopeAssessment scope) {
        if (scope.cardDataInvolved()) {
            legal.startPciTrack(c, scope);
            legal.startBreachNotificationTrack(c, scope);   // jurisdiction-dependent deadlines
            // Do NOT wait for eradication to begin. Containment and notification run in parallel.
        }
        if (scope.customerRecordsExported()) {
            legal.startPrivacyTrack(c, scope);             // GDPR / state breach notification
        }
    }
}
```

Forensic timeline that survives scrutiny, since it becomes the regulatory evidence:

```java
@Service
class ForensicTimeline {
    /**
     * Every asserted fact is traceable to a source, a host, and a preserved artifact.
     * "The attacker exfiltrated at 14:32" is only usable if the exact log line and its
     * host are both recorded, and the host's state was preserved at that moment.
     */
    record Assertion(String statement, String sourceSystem, String hostId, String logOffset,
                     String evidenceSha256, double confidence, String corroboratingSources[]) {}

    void assertFact(IncidentCase c, String statement, List<EventRef> sources) {
        if (sources.size() < 2) {
            // A single-source fact is a hypothesis. Record it as such rather than
            // letting an unverified inference harden into accepted history.
            unresolved.add(c, new Hypothesis(statement, sources));
            return;
        }
        assertions.add(c, new Assertion(statement, sources.get(0).system(), sources.get(0).host(),
                sources.get(0).offset(), evidenceStore.shaFor(sources.get(0).host()),
                confidence(sources), sources.stream().map(EventRef::id).toArray(String[]::new)));
    }

    /** Every gap in the record is stated explicitly. A timeline that hides its holes is propaganda. */
    List<EvidenceGap> documentedGaps(IncidentCase c) {
        return List.of(
            gap(c, "no audit logging on the legacy reporting service before " + c.legacyCutover),
            gap(c, "log retention is 30 days; activity older than that is unrecoverable"),
            gap(c, "clock offset of +34s on " + c.legacyHost + ", skew not independently verified"));
    }
}
```

Rehearsal is the only thing that makes this real. The tabletop runs against a live
technical environment with injected faults, not a conference room:

```java
@Scheduled(cron = "0 0 3 1 4 *")   // 03:00 on 1 April: nobody is expecting it
class QuarterlyGameDay {
    void run() {
        // A surprise drill is the only honest test of whether the runbooks are usable.
        inject.seedScenario(Scenario.CREDENTIAL_STUFFING_THEN_DATA_EXPORT);
        inject.seedScenario(Scenario.CLOUD_KEY_COMPROMISE);
        inject.seedScenario(Scenario.RANSOMWARE_PARTIAL_ENCRYPTION);
        // Then MEASURE the humans and the process, not just the tooling:
        results.record(this, timeToDeclare, timeToContain, playbooksUsed, gapsFollowed, commsFidelity);
        // Findings become hardening backlog items with owners and dates, like any other work.
    }
}
```

### Non-functional requirements

- **Time to declare** (Sev1): under 15 minutes from detection. Measured in every game day.
- **Time to contain**: under 45 minutes for credential compromise; under 2 hours for
  an unknown-scope intrusion. Longer containment is a scoping failure, not a tooling one.
- **Evidence integrity**: every artifact hashed at acquisition, chain of custody complete,
  and no analysis performed on originals. The timeline's assertions must survive external
  review, since it is a regulatory artefact.
- **Regulatory clocks**: notification deadlines tracked as explicit case milestones with
  owners, because missing a deadline is a separate failure from the breach itself.
- **Availability**: containment options are pre-authorised for common scenarios so nobody
  waits for approval at 3 a.m. Authorised actions are pre-listed, bounded, and logged.
- **Comms**: templates pre-drafted for internal, customer, regulator, and press, with a
  named approver chain, and a single source of truth for the factual timeline.
- **People**: roles defined and filled; every engineer has incident role training. The
  incident commander is a practice, not a title.
- **Improvement**: every incident and every game day produces a blameless post-mortem and
  a hardening backlog item with an owner and a date. Systemic conditions are named:
  ambiguous ownership, missing detection, unreviewed access, no default-deny.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- NIST SP 800-61 (Computer Security Incident Handling Guide) provides the incident
  response lifecycle — preparation, detection and analysis, containment, eradication,
  recovery, and post-incident activity — that the orchestration and runbook steps follow.
  https://csrc.nist.gov/pubs/sp/800/61/r2/final
- NIST SP 800-86 covers integrating forensic techniques into an incident response process,
  including evidence acquisition, chain of custody, and analysis on verified copies.
  https://csrc.nist.gov/pubs/sp/800/86/r1/final
- The First responders' and CSIRT teams' (FIRST) CSIRT Services Framework provides the
  incident-handling service taxonomy used to describe capability gaps in the tabletop
  findings and the escalation path to external partners.
  https://www.first.org/cmm/

## Deliverables

- [x] Time-boxed incident runbook with an explicit, low-cost "declare early" threshold
- [x] Defined incident roles: IC, comms, scribe, ops, legal, engineering leads
- [x] Parallel legal/compliance track for card data and personal data, with tracked deadlines
- [x] Forensic timeline where every assertion cites source, host, log offset, and hash
- [x] Explicit documented evidence gaps rather than a suspiciously complete story
- [x] Pre-authorised, bounded containment actions for common scenarios
- [x] Quarterly surprise game days against live infrastructure, with measured results
- [x] Blameless post-mortems producing hardening backlog items with owners and dates
