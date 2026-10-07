# REAL_WORLD_PROJECT — Java Version History

## The engagement

**Client:** enterprise insurer, ~500 engineers, 4 business units, 38 years of
accumulated Java estate.
**Scope:** 240 services and 90 batch jobs on **JDK 8 → JDK 25**, plus the build
estate, the container base images, the CI fleet, and the vendor contracts.
**Forcing function:** three, all dated. (1) the mainframe middleware vendor
announces JDK 8 end-of-support in 9 months; (2) the container base image for 8
leaves support in 12; (3) two regulators have asked for evidence of a supported
runtime and incident-response patch path.
**Team:** 9 engineers (3 platform, 6 application), 2 leads, **32 calendar weeks**.
**Method:** single-hop 8 → 25 with a 21 staging release for teams blocked by a
dependency; libraries first, JDK second, never in one deploy.

This is the capstone. It assumes you have run the `--release` matrix, reproduced
the JDK 18 encoding change, measured the GC logs, and can produce a blocker
inventory without being asked.

## 1. What the timeline actually buys this client

Before planning, price the destination — MATH_FOUNDATION.md §2 and §4 — because
"modernise because it is modern" is not a plan.

| Benefit | Mechanism | Version | Quantified for this estate |
|---|---|---|---|
| Memory density | Compact object headers, −4 to −8 B/object | 25 (opt-in flag) | 140M live objects → **0.56–1.12 TiB** saved, ~7–15% of fleet heap; vendor-measured Lilliput real-world range is 10–20% of live data |
| Concurrency ceiling removed | Virtual threads | 21 | Removes the `pool_size` ceiling on 40 IO-bound services; ~180k saved thread-equivalents of reserved stack |
| Density on huge heaps | Generational ZGC default | 25 | 6 services move from G1 pause tuning to sub-ms pauses at 32 GB+ |
| Boilerplate removal | Records | 16 | ~4,500 DTO classes → ~1,800 lines; ~30 person-days recovered |
| Exhaustiveness | Sealed + switch patterns | 17/21 | Removes `default:` branches that silently absorbed unknown subtypes in 22 domain hierarchies |
| Encoding correctness | UTF-8 default | 18 | Kills the platform-locale dependency that produced the 2019 garbled-claimant-name incident |
| Ergonomics | `import module java.base` | 25 | Cosmetic: less import noise. It works in classpath code too (JEP 511 does not require modularising), so it is safe but low value |

Per MATH_FOUNDATION.md §1, with `N = 2.5` on IO-bound services, `gain(0.5) =
1.286` — a **28.6%** fleet-wide improvement for a full migration, concentrated in
the first 25% migrated. That is the number the executive summary quotes, and the
number that justifies sequencing low-blast-radius services first rather than
revenue services.

## 2. Version-by-version timeline (32 weeks)

Target **25**, with 21 as a staging release for two dependency-blocked units.

| Weeks | Phase | Exit criteria | Owner |
|---|---|---|---|
| 1–2 | Inventory: `jdeps --jdk-internals` on all 330 artifacts, dependency trees, encoding audit, CLDR golden-file gap, scored risk ledger | Ledger complete, every row typed and owned; effort within 2× of plan | Lead |
| 3–6 | **Library wave** — Spring Boot 2→3, Hibernate 4→6, `javax`→`jakarta`, JUnit 4→5, Mockito 1→5, de-Charset every I/O site, per-locale golden files | All 330 artifacts build and pass tests **on JDK 8**. Zero source changes that depend on JDK version | 6 app engineers |
| 7 | Build estate on 25: CI agents, `--release 25` enforcement, Animal Sniffer + forbidden-apis gates, distroless 25 images pinned by digest | Gates in CI, each failing on a deliberate violation | Platform |
| 8 | **Compatibility gates** installed enterprise-wide (see §5). Encoded-text backfill scan of all shared databases | Backfill count reported to Legal; gates inherited, not opt-in | Platform + DBA |
| 9–11 | Wave 1 — 118 internal/low-risk services, batched by 8, 1%→5%→25%→50%→100% | SLOs green at required samples; shadow divergence under threshold | Unit leads |
| 12–13 | Wave 2 — 74 customer-facing read services | Divergence under 0.13% vs baseline; full weekday+weekend cycle each batch | Unit leads |
| 14–16 | **21 staging release** for the two dependency-blocked units only (legacy mainframes, old MQ client) | Those two units green on 21; no other service pinned below 25 | Lead |
| 17–21 | Wave 3 — 41 customer-facing write services, one at a time, 14-day soak | Zero write-path divergence; Finance signs off reconciliation | Finance + unit leads |
| 22–24 | Records/sealed/pattern-matching adoption on the 22 domain hierarchies (sequenced, not in the migration release) | Exhaustiveness checks green; `default:` branches removed | 6 app engineers |
| 25–27 | Virtual-thread migration of the 40 IO-bound services; `synchronized`-around-IO audit first | p99 improvement measured per service; no pinning detected in traces | 6 app engineers |
| 28 | Capacity re-tune: heap sizing from compact headers, GC re-baseline at 2 GB and 32 GB | Measured savings match MATH_FOUNDATION §2 within 15% | Platform |
| 29–30 | **Stabilisation** — soak, chaos, and a deliberate rollback drill per wave | Drill wall-clock measured; residual-risk register signed | On-call + lead |
| 31 | Decommission: delete JDK 8 images, remove `--add-opens`, remove `-source 8` fallbacks, terminate 8 agents | Flags at zero; `grep -rn 'add-opens\|source 8' .` returns nothing | Platform |
| 32 | Post-mortem, ADR filed, roadmap handed to BAU | Ledger closed with evidence per row | Lead |

War-room cadence: daily 15-minute standup from week 9, one tracker, one channel.
The war room is not the meeting — it is the shared record of which service is at
which traffic percentage right now.

## 3. Per-version risk register

Scored with MATH_FOUNDATION.md §1: `B` blast radius, `D` detectability, `E` effort,
each 1–5. The register is **per version**, because that is what a roadmap
review actually disputes.

| Version | Risk | B | D | E | Score | Mitigation |
|---|---|---|---|---|---|---|
| 8 → 25 | Shared DB text columns written on an ASCII-default container, read as UTF-8 | 5 | 5 | 4 | **100** | Backfill scan + rewrite before Wave 1; explicit charsets everywhere |
| 8 → 25 | `Optional`/DTO classes with hand-written `equals` replaced by records — synthesized equality differs | 3 | 4 | 3 | 72 | Incremental per class; `Objects.equals` vs `==` review |
| 8 → 17 | Hibernate 4 / Mockito 1 bytecode generation on `Unsafe.defineAnonymousClass` | 3 | 3 | 5 | 90 | Library wave weeks 3–6, **before** any JDK bump |
| 9 | CLDR formatting change: de-DE/fr-FR/tr-TR invoice and claim text | 5 | 5 | 2 | 76 | Golden files per locale in the library wave; business sign-off per diff |
| 17 | Strong encapsulation: `--add-opens` accumulation across 330 artifacts | 3 | 2 | 4 | 48 | Zero-tolerance at week 31; `LEGACY-####` tickets from week 7 |
| 18 | UTF-8 default — silent mojibake in archived claim documents | 5 | 5 | 3 | 90 | Explicit charset at every site; grep gate in CI |
| 21 | Virtual threads adopted while `synchronized` still wraps IO — no win, pinned carriers | 3 | 2 | 4 | 48 | `synchronized` audit (week 25) strictly before adoption (week 27) |
| 21 | Fixed thread pools left in place — compiles, silently wrong shape | 2 | 3 | 2 | 24 | Pool-removal ticket per service; trace-based pinning check |
| 23 | Generational ZGC changes tail latency profile | 4 | 2 | 2 | 32 | Re-baseline SLOs; do not carry pause thresholds across |
| 25 | Compact object headers: heap-dump tooling and memory accounting revalidation | 4 | 2 | 2 | 32 | Capacity work week 28; verify every heap-dump pipeline against 25 |
| 25 | `import module` collides with an existing on-demand import and changes name resolution | 2 | 3 | 2 | 12 | Lint rule; apply file by file, only where it removes real import noise |
| any | Enterprise vendors certify against 8/11, not 25 | 4 | 5 | 5 | **100** | Cert letters obtained before the commit; two vendors refuse — see §4 |

**The register's message.** The two `100`s are not code problems, and they are the
entire reason the plan is 32 weeks rather than 16. A roadmap that only counts
source fixes will be wrong by a factor of two.

## 4. Adopt / do not adopt

**Adopt, with a workstream each.**

| Feature | Why, for this estate | Sequencing |
|---|---|---|
| Explicit charsets everywhere | The single highest-severity silent break (18) | Library wave, week 3 |
| Per-locale golden files | Catches the CLDR class that no test asserted | Library wave, week 4 |
| Records for DTOs | ~4,500 classes; ~30 person-days recovered | Week 22+, one hierarchy per release |
| Sealed + exhaustive switch | 22 domain hierarchies lose silent `default:` branches | Week 22+, alongside records |
| Pattern matching `switch` | Removes 400+ `instanceof` chains; readability on incident paths | Week 22+ |
| Virtual threads on 40 IO services | Removes the concurrency ceiling; ~180k thread-equivalents | `synchronized` audit first, week 27 |
| Compact headers (capacity, not code) | ~2.1 TiB fleet-wide | Deploy with 25; re-tune heaps week 28 |
| Generational ZGC at 32 GB+ | Sub-ms pauses for six large services | Week 23+ with re-baselined SLOs |

**Do not adopt, and say so out loud.**

| Feature | Why not |
|---|---|
| String templates | **Withdrawn.** Previewed in 21 and 22, then JEP 465 was withdrawn; it never shipped. Adopting the preview would have been a full rewrite for nothing (MATH_FOUNDATION §6) |
| Structured concurrency | Still **preview** in 25 — 19→25 without finalisation. Experiments only, behind a flag, never in a claim-handling path |
| `import module java.base` | Not harmful, but a cosmetic change with a name-resolution subtlety (module imports are *shadowed* by on-demand and single-type imports). Do it opportunistically, never as a workstream |
| Generics-on-primitives (value classes) | Repeatedly deferred; no timeline you can plan against |
| Compact headers as a *performance* project | It is a capacity change, not a latency change. Teams who treat it as a speed project will not find the memory and will declare it a disappointment |
| `--enable-preview` in any production artifact | Preview bytecode will not load on the next JDK; it is a bet with a bad payoff distribution |

**The meta-rule for this section:** the "do not adopt" list is worth more to the
programme than the "adopt" list, because the adopt list is already in every
engineer's blog post and the do-not list is where the roadmap's money is saved.

## 5. Compatibility gates

Numeric, evaluated by a pipeline, identical for every artifact. No artifact gets
a bespoke threshold; thresholds derive from that artifact's own baseline.

```text
PROMOTE  ⟺  all of:
  min_samples          ≥ 3,000 AND elapsed ≥ 7 days (weekday + weekend)
  p99_canary           ≤ 1.10 × p99_baseline        (same window, 1% split)
  error_ratio_canary   ≤ 1.10
  shadow_divergence    < d_baseline + 3·√(d(1−d)/n)
  new_blocker_classes  == 0
  ledger_rows_closed   == rows_for_this_artifact
HOLD     ⟺  any gate inconclusive → hold 24 h, re-evaluate. Never promote "to keep moving".
ROLLBACK ⟺  any gate violated → image swap, post-mortem before retry.
```

Static gates, in `main`, inherited from the shared build template:

| Gate | Catches | Failure message you should see |
|---|---|---|
| `javac --release 25` with `ct.sym` | Your own code calling a post-8 API | `cannot find symbol` |
| Animal Sniffer (`java25` signatures) | **Compiled dependencies** calling a post-8 API | `Undefined reference: java.nio.file.Files readString(...)` |
| `forbidden-apis` | JDK internals, `Class.newInstance`, `SecurityManager` | `Usage of internal API` |
| Grep: bare charset | The JDK 18 class, in files the compiler cannot see | `new String(` without `Charset` |
| Grep: bare `String.format` | The JDK 9 CLDR class | `String.format(` without `Locale` |
| Runtime version assertion in health check | Build-JDK skew (compiled on 25, shipped on 8) | health endpoint non-200 |
| `jdeps --jdk-internals` | Internal-API reach, weekly, whole fleet | `sun.misc.Unsafe` → `com.acme...` |

Per MATH_FOUNDATION.md §4 and §5 in the sibling migration lab: the sample-size
floor is what makes the p99 comparison mean anything (a tail quantile needs ~10×
the samples of a mean), the 7-day floor covers traffic shapes no test covers, and
the divergence gate is the only one that catches the *behavioural* surface — it
compares responses rather than error counts. **For write-path services, shadow to
a discarding sink; never let a shadow write to the same database.**

**Rollback budget.** Per stage, and measured in a drill (not documented):

| Stage | Action | Budget |
|---|---|---|
| Library-only wave | Revert deploy; JDK unchanged | < 5 min |
| Gate enforcement | Revert build config; no code change | < 10 min |
| Single service canary | `kubectl set image` to previous digest | ≤ 5 min |
| Batch of 8 (Waves 1–2) | Revert batch, then stragglers individually | ≤ 15 min |
| Wave 3 write service | Exec-authorised revert + reconciliation check | ≤ 30 min + Finance |

Before Wave 3 starts, agree **in writing** with Finance and Claims what "rollback"
means for a partially-applied claim batch: redeploy, compensating journal entry, or
page. A rollback plan whose meaning is ambiguous is not a plan.

## 6. Residual risk and how it is carried

| Risk | Severity | Mitigation | Carried by |
|---|---|---|---|
| Two enterprise vendors certify only against 8/11 | High | Cert letters in hand before Wave 1; vendor A agreed to 21, vendor B refused 25 → B stays on a 21 **staging release**, tracked as `RISK-001` with a review date | Procurement + lead |
| Archival claim documents with legacy encodings | High | Backfill scan (week 8) + Legal notified with an explicit count | DBA + Legal |
| A service nobody owns has hidden reflective JDK access | Medium | Reflection-reachability test in the shared build template — inherited, not opt-in | Platform |
| Mixed-encoding rows written during the migration window | High | Wave sequencing puts the backfill *before* Wave 1, not in parallel | DBA |
| Virtual-thread adoption without a `synchronized` audit | Medium | Audit's calendar dependency (week 25 before week 27) is a hard gate; trace-based pinning check in review | App leads |
| Team momentum loss in weeks 17–24 (the long middle) | Medium | Records/sealed workstream keeps the app engineers visibly productive; lead posts the divergence dashboard weekly | Lead |
| A future commit reintroduces a pre-25 API | Low | Animal Sniffer + `--release` gates; the migration is self-reversing | Platform |
| Schedule slips past the vendor deadline | High | Weeks 1–8 are the critical path and are fully in the platform team's control; Wave 1 alone delivers 118 services of value if the deadline forces a stop | Lead + exec |

## 7. What the exercise is actually teaching

The client does not ship 25 because 25 is better. They ship 25 because three
dated forcing functions plus ~2.1 TiB of memory and a removed concurrency ceiling
outweigh a 32-week programme — and because the timeline tells you *which* risks
are silent. THEORY.md's four cross-cutting patterns are the whole argument:

1. **Every feature answers existing pressure** — so every feature carries its
   own upgrade risk, discoverable in advance from the JEP index.
2. **Preview is the release valve** — so structured concurrency (incubator
   19–20, preview 21→25 and beyond, never final in 25)
   and string templates (withdrawn) are *not* roadmap items, and treating them
   as such is the most expensive mistake available.
3. **API-evolution mechanisms are features** — 17 closed the JDK over its own
   internals and produced the `--add-opens` era; 25 reopened ergonomics with
   `import module`. Expect the tax, budget for it.
4. **The runtime keeps being rebuilt** — GC, memory layout, and concurrency were
   all rebuilt in the target release. Every GC and heap number carried forward
   from JDK 8 is a guess until re-measured.

An advisor who presents this as a schedule plus a risk register with scores and
measured rollback times is doing a different job from one who presents a version
number. The first is staff-plus work.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- **OpenJDK JEP index** — the authoritative record of every feature by JDK
  version. The primary source for every attribution in this plan and for
  re-verifying the two score-100 rows before they are quoted to a steering
  committee.
  <https://openjdk.org/jeps/0>
- **Java SE support roadmap** — LTS cadence, release dates, and vendor support
  windows. The source for the forcing-function dates: the JDK 8 end-of-support
  claim in the engagement brief and the target-JDK decision in §2 both come from here.
  <https://www.oracle.com/java/technologies/java-se-support-roadmap.html>
- **Java Language Specification, JLS 13.5** — the binary-compatibility rules
  that define what this migration is and is not allowed to break, and the reason
  "it compiled on 25" never suffices as an acceptance criterion.
  <https://docs.oracle.com/javase/specs/jls/se21/html/jls-13.html>

Two further pages worth checking before this plan is presented, both referenced in
THEORY.md: JEP 400, UTF-8 by Default (the §18 silent-corruption risk) at
<https://openjdk.org/jeps/400> and JEP 519, Compact Object Headers (the §2 compact-header arithmetic) at
<https://openjdk.org/jeps/519>.