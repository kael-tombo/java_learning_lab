# Incident Response & Forensics - MINI PROJECT

## Project: MockBreach — run a complete incident, from page to post-mortem

Stage a compromised application: an attacker creates an account, escalates privileges, and
exfiltrates data. Run the full response lifecycle against it, handling evidence properly
and producing the documentation a real incident requires.

### Architecture

```
  INJECTED COMPROMISE (staging only, scripted)
    T+0    attacker registers a normal user account
    T+2h   brute-forces an admin account
    T+3h   exploits an IDOR to read other tenants' records
    T+5h   bulk-exports data via a new endpoint they created
    T+6h   installs a cron job for persistence

  RESPONSE
    Alert (SIM: 200 exports in 10 min) ──▶ Tier1 triage ──▶ declare Sev1
      │  T+15m  scope: which tenants, which records, since when
      ▼
    Containment: revoke tokens, disable accounts, block egress, isolate pods
      │  (evidence preserved FIRST - memory/disk images, log export)
      ▼
    Eradication: remove the created endpoint, the cron job, the access key
      ▼
    Recovery: rebuild from known-good, rotate ALL credentials in scope
      ▼
    Post-mortem: timeline, contributing conditions, hardening backlog
```

### Implementation

Evidence acquisition with chain of custody, the part people skip and regret skipping:

```java
@Component
class EvidenceCollector {
    /**
     * Order matters: capture volatile state FIRST (memory, network, process list), then disk.
     * Everything is hashed at acquisition and the original is never analysed - analysts work
     * on a verified copy so the original remains admissible.
     */
    public EvidenceItem acquire(Target target, EvidenceType type) throws IOException {
        Path out = caseStore.newArtifactPath(target.id(), type);
        switch (type) {
            case MEMORY_IMAGE -> out = forensicImager.capture(target.host(), out);   // ram must go first
            case DISK_IMAGE   -> out = forensicImager.capture(target.volume(), out);
            case CONTAINER    -> out = capturePodState(target);  // manifest, logs, env, fs snapshot
            case LOG_BUNDLE   -> out = logCollector.export(target, range(from, to));
            case AUTH_LOG     -> out = authLogExporter.export(target, range(from, to));
        }
        String sha256 = sha256(out);
        custodyLog.record(caseId(), type, out, sha256, collector(), Instant.now());
        return new EvidenceItem(out, sha256, type);
    }

    /** Any analyst opening evidence works on a copy, and the copy's hash is re-verified. */
    public Path workingCopy(EvidenceItem item, String analyst) throws IOException {
        Path copy = caseStore.copyFor(item, analyst);
        if (!sha256(copy).equals(item.sha256())) throw new EvidenceIntegrityException("copy hash mismatch");
        return copy;
    }
}
```

Timeline reconstruction across systems, which is where the real insight appears:

```java
@Service
class TimelineBuilder {
    /** Merge heterogeneous sources onto one clock, then look for the contradictions. */
    public Timeline build(IncidentCase c) {
        List<Event> events = new ArrayList<>();
        events.addAll(authLogs.authEvents(c));        // logins, MFA, token issues
        events.addAll(appLogs.dataAccessEvents(c));   // reads, exports, API calls
        events.addAll(k8sEvents.podLifecycle(c));     // image pull, exec, scale
        events.addAll(edgeLogs.networkEvents(c));     // egress, IPs, TLS metadata

        // Clock skew between systems is real. Detect it rather than silently producing a
        // wrong sequence: a 40s "impossible" reorder is a clock problem, not an attack.
        ClockSkew skew = estimateSkew(events);
        events.forEach(e -> e.setNormalizedTime(e.rawTime().minus(skew.offsetFor(e.source()))));
        events.sort(Comparator.comparing(Event::normalizedTime));

        List<Finding> gaps = detectEvidenceGaps(events, c);   // e.g. no audit logs before T-24h
        return new Timeline(c.id(), events, skew, gaps);
    }

    record Finding(String type, String detail) {}
    // gap types: MISSING_LOG_WINDOW, CLOCK_SKEW, NO_AUDIT_TRAIL, IDENTITY_UNRESOLVED
}
```

Containment that is *also* correct for the attacker problem, not just loud:

```java
@Service
class ContainmentService {
    /**
     * Containment removes the ATTACKER'S ACCESS while preserving EVIDENCE.
     * Every action is reversible, scoped, logged, and time-bounded where possible.
     * Order: cut their access first, then preserve, then rebuild. Never the reverse -
     * if you let the attacker keep access while you investigate, you are investigating live.
     */
    ContainmentReport contain(IncidentCase c) {
        var actions = new ArrayList<ContainmentAction>();

        // 1. Revoke all active tokens for the compromised identities (fast, reversible).
        actions.add(revokeAllSessions(c.compromisedIdentities(), "credential compromise"));

        // 2. Disable the accounts. NOT delete - deletion destroys evidence and audit trail.
        actions.add(disableAccounts(c.compromisedIdentities()));

        // 3. Network: block the source, and importantly the DESTINATION of the exfiltration.
        actions.add(blockEgress(c.exfilDestination()));
        actions.add(blockSource(c.attackerSourceIps()));

        // 4. Quarantine, do not delete. The image and filesystem state are evidence.
        actions.add(quarantinePods(c.affectedWorkloads()));

        // 5. Kill persistence: the attacker's cron/created endpoint.
        actions.add(removeUnauthorizedResources(c.unauthorizedResources()));

        // 6. Only NOW preserve evidence from the quarantined systems.
        evidence.acquire(c.targets(), MEMORY_IMAGE, DISK_IMAGE, LOG_BUNDLE, AUTH_LOG);

        return new ContainmentReport(actions, allReversible: true);
    }

    /** Actions carry an expiry so an emergency block does not become permanent by accident. */
    record ContainmentAction(String type, String target, String reason, Instant expiresAt) {}
}
```

Eradication, which must actually remove the foothold rather than hiding its symptoms:

```java
@Service
class EradicationService {
    /**
     * Eradication = remove attacker artefacts AND the vulnerability that allowed entry.
     * Rotating a credential without fixing the entry vector guarantees a repeat visit.
     */
    EradicationReport eradicate(IncidentCase c) {
        // 1. Remove every artefact found during forensics, with a verification check.
        for (Artifact a : forensics.findings(c).artifacts()) remove(a);
        verifyAbsent(forensics.findings(c).artifacts());     // prove it is gone, don't assume

        // 2. Close the entry vector, not just the symptom.
        for (Vulnerability v : forensics.findings(c).vulnerabilities())
            remediationQueue.enqueue(v.withSeverity(v.severity().escalate(EXPLOITED_IN_PROD)));

        // 3. Rotate the FULL scope, not just the keys the attacker used. Assume they
        //    captured anything they could read, including the key next to the one used.
        for (Credential c2 : blastRadius(c)) secrets.rotate(c2);

        // 4. Rebuild from a known-good image, not from the compromised filesystem.
        for (Workload w : c.affectedWorkloads()) infrastructure.redeployFrom(w.knownGoodImage());
        return new EradicationReport(...);
    }

    /** "Recovered" is a claim requiring evidence, not a decision requiring a deploy. */
    RecoveryReport verifyRecovery(IncidentCase c) {
        verifyNoAttackerInfrastructure(c);
        verifyNoUnauthorizedIdentities(c);
        verifyEntryVectorClosed(c);       // the IDOR is fixed and the exploit no longer works
        verifyMonitoringDetectsRecurrence(c);   // re-run the attack; the alert must fire
        return RecoveryReport.clean();""" } );
    }
}
```

### Test It

```java
@Test void injectedCompromiseIsDetectedWithinSla() {
    injectBreach(stagingScript());
    await().atMost(Duration.ofMinutes(10), () -> assertThat(alertQueue.hasMatchingAlerts()).isTrue());
    assertThat(alertQueue.matching().severity()).isEqualTo(SEV1);
}

@Test void evidenceChainIsVerifiable() {
    EvidenceItem mem = evidence.acquire(host, MEMORY_IMAGE);
    Path copy = evidence.workingCopy(mem, "analyst-1");
    assertThat(sha256(copy)).isEqualTo(mem.sha256());
    assertThat(custodyLog.entriesFor(mem.path())).hasSizeGreaterThanOrEqualTo(1);
}

@Test void containmentRemovesAccessButPreservesEvidence() {
    var report = containment.contain(caseForInjectedBreach());
    assertThat(report.action("disable-accounts")).isNotNull();          // not delete
    assertThat(report.action("revoke-sessions")).isNotNull();
    assertThat(evidenceStore.itemsFor(caseId())).isNotEmpty();           // evidence preserved
    assertThat(report.allReversible()).isTrue();
}

@Test void eradicationRemovesArtifactAndProvesIt() {
    eradication.eradicate(caseForInjectedBreach());
    assertThat(forensics.findArtifacts(persistenceArtifactPath)).isEmpty();  // verified absent
    assertThat(secretRotations.rotated()).hasSizeGreaterThan(2);            // full blast radius
}

@Test void recoveryIsVerifiedByReplayingTheAttack() {
    recovery.verifyRecovery(caseForInjectedBreach());
    injectBreach(stagingScript());   // the same technique, now blocked
    assertThat(alertQueue.newAlerts()).anyMatch(a -> a.ruleId().equals("EXFIL-VOLUME-001"));
}
```

## Deliverables

- [ ] Scripted breach scenario with a defined timeline (T+0 to T+6h) on staging only
- [ ] Evidence collector: memory before disk, SHA-256 at acquisition, working-copy discipline
- [ ] Chain of custody log with timestamps, hashes, and named custodians
- [ ] Timeline builder across auth, app, Kubernetes, and edge logs with skew detection
- [ ] Containment service: revoke, disable (not delete), block egress, quarantine, preserve
- [ ] Time-bounded, reversible containment actions with expiry
- [ ] Eradication that closes the entry vector and rotates the full credential blast radius
- [ ] Recovery verification that replays the attack technique to prove detection and closure
- [ ] Post-mortem with timeline, contributing system conditions, and a hardening backlog
