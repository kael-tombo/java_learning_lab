# REAL_WORLD_PROJECT — Java Migration

## The engagement

**Client:** mid-size fintech, ~400 engineers, 3 business units.
**Scope:** 61 services on JDK 8 → JDK 21. Plus the build estate, the container
base images, and the CI fleet.
**Forcing function:** container base-image EOL (the distroless 8 variant leaves
support in 180 days) *and* a vendor dropping JDK 8 support for the core ledger
library. Both dated, neither negotiable.
**Team:** 6 engineers, 2 platform engineers shared, 14 calendar weeks.
**Method:** single-hop 8 → 21, libraries first, canary-gated, staged per unit.

This is the capstone. It assumes you have already done EXERCISES.md and
MINI_PROJECT.md and can produce the inventory and the gates without being asked.

## 1. Blast-radius analysis

61 services is not one migration; it is four migrations with different risk
profiles. Rank by blast radius first, and note that the biggest service is
deliberately not first.

| Tier | Services | Examples | Blast radius | Why |
|---|---|---|---|---|
| **T1 — internal, low risk** | 18 | admin UI, report scheduler, batch notifiers | single team, no customer PII on the failure path | **Start here.** Cheap real traffic, exercises the shared build chain |
| **T2 — customer-facing read** | 27 | account summary, statement API, KYC status | read-only, no writes, replayable | Second wave. Divergence is detectable by shadow diff |
| **T3 — customer-facing write** | 13 | payments, transfers, ledger postings | money movement; rollback cannot always undo | Third wave, longest soak per service |
| **T4 — critical shared** | 3 | core ledger, settlement batch, auth gateway | every other service depends on it | **Last.** These three change the blast radius of everything else |

**Integration surfaces (the cross-service risk).** Before touching a JDK,
enumerate what the service shares: PostgreSQL schemas (JDBC driver version
coupling), Kafka topics (serialization/encoding coupling), Redis (client
coupling), gRPC/REST contracts (JSON charset coupling), and shared tables whose
columns hold text written by a JVM on a different JDK. That last one is where the
JDK 18 charset change lands: a legacy row written by a JDK 8 process on an
ASCII-default container is read by a JDK 21 process as UTF-8, and it either
round-trips or corrupts depending on whether the bytes were valid UTF-8.

Per MATH_FOUNDATION.md §3, with 8 shared integration surfaces at 4% independent
skew-incident probability: `1 − 0.96^8 = 27.9%` chance of at least one
cross-service incident while the fleet is mixed. That number — not a preference —
is why the fleet moves in three waves over 10 weeks rather than dripping over six
months.

## 2. War-room timeline (14 weeks)

| Weeks | Phase | Exit criteria | Owner |
|---|---|---|---|
| 1 | Inventory: `jdeps --jdk-internals` on all 61, dependency trees, encoding audit, full ledger scored | Ledger complete, all blockers typed, effort estimate within 2× of plan | Lead |
| 2–3 | Library upgrade wave — Spring Boot 2 → 3, Hibernate 4 → 6, Mockito 1 → 5, `javax` → `jakarta`, de-Charset everything | All services build and pass tests **on JDK 8**; zero source changes to JDK-version behaviour | 2 eng per unit |
| 4 | Wave 1 infrastructure: CI agents on 21, Maven `--release` enforcement, Animal Sniffer + forbidden-apis gates, Docker base images | Gates in CI and failing on a deliberate violation | Platform |
| 5 | T1 canary: 1 service, 1%, shadow-diff against baseline, SLO-gated | Rollback drill measured under 5 min | On-call + lead |
| 6 | T1 full (18 services), decommission of T1 old images | T1 at 100% on 21, no `--add-opens` | T1 owners |
| 7–8 | T2 canary wave (27 services), 1% → 5% → 25% → 50% → 100% in batches of 5 | Divergence < 0.13% vs baseline, SLOs green at required samples | Unit leads |
| 9–10 | T3 canary wave (13 services), one at a time, 14-day soak each | Zero write-path divergence; finance signs off on reconciliation | Finance + unit leads |
| 11–12 | T4 (core ledger, settlement, auth) — one at a time, longest soak, exec go/no-go per service | Reconciliation clean for a full settlement cycle | Staff+ / principal |
| 13 | Decommission: delete JDK 8 images, remove `--add-opens`, remove `-source 8` fallbacks, shut down 8 agents | Fleet 100% on 21, flags at zero | Platform |
| 14 | Post-mortem + close: ledger closed, tickets transferred or deleted | Every ledger row closed with evidence | Lead |

War-room cadence: daily 15-min standup for weeks 5–12, a single shared tracker,
and one Slack channel with no other topics. The war room is not the meeting —
it is the shared record of which service is on which traffic percentage right now.

## 3. Per-stage rollback plan

Rollback is per *stage*, and every stage's rollback is an image swap. The previous
image is tagged, pushed, and pullable before the new one gets any traffic.

| Stage | Rollback action | Time budget | Preconditions |
|---|---|---|---|
| Library-only wave (wk 2–3) | Revert deploy to previous tag; JDK unchanged | < 5 min | Library upgrade is its own release, never bundled with a JDK bump |
| Compile-enforcement (wk 4) | Revert `pom.xml` / CI config | < 10 min | Enforcement is a separate commit, revertible without code change |
| Single service canary | `kubectl set image` to previous digest | ≤ 5 min | Both digests pushed; no build step |
| Batch of 5 (T2/T3) | Revert the batch, then the stragglers individually | ≤ 15 min | Services are independently revertible — no shared deploy |
| T4 core service | Exec-authorised revert, plus reconciliation check | ≤ 30 min + finance verification | Pre-agreed: **reverting a ledger service after settlement closes may require a compensating entry** |

The T4 row is why those three go last and soak longest. Before starting T4, agree
in writing with Finance what "rollback" means for a partially-applied settlement:
is it a redeploy, a compensating journal entry, or a page? A rollback plan whose
meaning is ambiguous is not a plan.

**Drills.** Rehearsed in week 5 (T1) and again at the start of week 9 (T3), each
measured with `time kubectl rollout status`. Target ≤ 5 min for a single service,
≤ 15 min for a batch. MATH_FOUNDATION.md §5 gives the derivation: with a 99.9% SLO
on 100M req/month at 1000 req/s, a 128× canary burn rate cuts the deadline to a
few hours of remaining budget — and that budget shrinks as the month is consumed,
which is a concrete argument for doing canaries early in a budget period.

## 4. SLO gates

Gates are numeric, evaluated by a pipeline, and identical for every service. No
service gets a bespoke threshold; the thresholds are service-specific but derived
from that service's own baseline, not chosen.

```text
PROMOTE  ⟺  all of:
  n_samples            ≥ 3,000 AND elapsed ≥ 7 days (weekday + weekend covered)
  p99_latency_canary   ≤ 1.10 × p99_latency_baseline    (same window, 1% split)
  error_ratio_canary   ≤ 1.10
  shadow_divergence    < baseline_divergence + 3·√(d(1−d)/n)
  new_blocker_classes  == 0
  ledger_rows_closed   == rows_for_this_service
HOLD     ⟺  any gate inconclusive → hold 24h and re-evaluate, never promote "to keep moving"
ROLLBACK ⟺  any gate violated → image swap, then post-mortem before retry
```

Per-gate rationale, from MATH_FOUNDATION.md §4: the sample-size floor is what
makes the p99 comparison mean anything (a tail quantile needs roughly 10× the
samples of a mean); the 7-day floor covers traffic shapes no test covers; the
divergence gate is the only one that catches the behavioural surface, since it
compares actual responses rather than error counts.

**Shadow-run first for T3 and T4.** Mirror production traffic to both versions,
compare responses, alert on divergence. For write-path services, shadow to a
discarding sink — never let a shadow write to the same database.

## 5. What actually broke (realistic failure list)

Ordered by how often each shows up in a fleet this size:

1. **Encoding.** Text columns written by JDK 8 processes on ASCII-default
   containers, read by JDK 21 as UTF-8. Symptom: garbled names in statements.
   Fix: explicit charsets everywhere, plus a backfill scan for invalid UTF-8.
2. **CLDR formatting.** Invoice and statement text in de-DE / fr-FR changes
   (spacing, grouping, currency position). Symptom: unit tests comparing formatted
   strings fail. Fix: golden files per locale, business sign-off per diff.
3. **Library upgrades, not the JDK.** Spring Boot 2 → 3 forces `javax` →
   `jakarta` across every `@WebFilter`, `@Entity`, and hand-rolled `javax.servlet`
   import. Symptom: `ClassNotFoundException: javax.servlet.http.HttpServlet`.
   This is 70% of the engineering hours in weeks 2–3.
4. **Mockito 1 → 5 and Hibernate proxy generation.** Old bytecode generation dies
   on `sun.misc.Unsafe` memory-access methods (permanently disabled in 24, JEP
   498). Symptom: `NoSuchMethodError`
   in test setup. Fix: upgrade, no flag exists.
5. **`--add-opens` accumulation.** Every service ends up with 2–4 flags. Symptom:
   none, which is the problem. Fix: ticketed, counted, and zero at decommission.
6. **GC pause profiles.** CMS (removed in 14) → G1 changes tail latency. Symptom:
   p99 improves or worsens depending on heap sizing; old `-XX` flags fail startup
   outright. Fix: re-baseline, do not carry flags across.
7. **Build-JDK skew.** One team compiles on 21 and ships an 8 runtime for a week.
   Symptom: `NoSuchMethodError` in one service only. Fix: enforcer on build JDK
   plus a runtime-version assertion in the app's own health check.

## 6. Decommission checklist

The step that gets skipped, which is why the flags become permanent.

- [ ] JDK 8 container images deleted from every registry, not just untagged
- [ ] JDK 8 CI agents terminated; `JAVA_HOME` defaults updated on the build fleet
- [ ] Every `--add-opens` / `--add-exports` removed from Dockerfiles, CI configs,
      and `JAVA_TOOL_OPTIONS`; verify: `grep -rn 'add-opens' .` returns nothing
- [ ] `LEGACY-####` tickets either closed or re-filed against a real owner with a date
- [ ] `SecurityManager` set-up code deleted (`doPrivileged` wrappers, policy files)
- [ ] `-source`/`-target` fallback profiles removed from `pom.xml`; `maven.compiler.release` is the only path
- [ ] Legacy encoding fallback flags (`-Dfile.encoding=ISO-8859-1`, `COMPAT`) removed
- [ ] Dead GC flags purged: `grep -rn 'UseConcMarkSweepGC\|PrintGCDetails\|PrintGCDateStamps' .`
- [ ] Mixed-fleet integration surfaces re-verified at 100%: schema encodings, Kafka
      topic payloads, shared-text columns
- [ ] Nightly builds that still run an 8 matrix leg removed; the matrix is 21-only
- [ ] Migration ledger closed with evidence links per row (PR, dashboard, drill log)
- [ ] Architecture decision record filed: why 21, why single-hop, why this sequence
- [ ] Team runbook updated: "we are on 21; here is what that means for your library"

## 7. Residual risk and how it is carried

| Risk | Severity | Mitigation | Carried by |
|---|---|---|---|
| Old text columns with mixed encodings in the ledger DB | High | Backfill scan + rewrite before T4; report count to Finance | Data team + Finance |
| A service nobody owns has hidden reflective JDK access | Medium | `ReflectionReachabilityTest` in the shared build template; gate is inherited, not opt-in | Platform |
| Two teams' changes interact after wave boundaries | Medium | Weekly cross-unit sync; dependency-surface matrix reviewed at each wave boundary | Lead |
| Rollback of a T4 service after settlement close | High | Pre-agreed semantics with Finance, written down before wave T4 starts | Finance + staff+ |
| A future commit reintroduces a post-21 API | Low | Animal Sniffer signature gate + enforcer; the migration is self-reversing | Platform |

## Sourced field notes (fetched Oct 2026 — verify before citing)

- **JEP 403: Strongly Encapsulate JDK Internals** (JDK 17, Sept 2021) — the
  reference for every `--add-opens` line in this plan; `--illegal-access` ignored
  by default.
  <https://openjdk.org/jeps/403>
- **JEP 400: UTF-8 by Default** (JDK 18) — the source of failure class #1, the
  highest-severity item in this migration.
  <https://openjdk.org/jeps/400>
- **JEP 486: Permanently Disable the Security Manager** (JDK 24) — the reason
  `doPrivileged` cleanup is safe to schedule now rather than after a future JDK.
  <https://openjdk.org/jeps/486>
- **`jdeps` tool documentation** — `--jdk-internals`, the week-1 inventory command.
  <https://docs.oracle.com/en/java/javase/21/docs/specs/man/jdeps.html>
- **Animal Sniffer** — signature-based API conformance checking for the CI gate.
  <https://www.mojohaus.org/animal-sniffer/>