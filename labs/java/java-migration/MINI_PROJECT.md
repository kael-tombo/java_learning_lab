# MINI_PROJECT — Java Migration

Two weeks. One legacy app, Java 8 → JDK 21, end to end in the lab. The deliverable
is evidence, not a merged PR: a green build, a scored ledger, parity tests that
would have caught the silent breaks, and a rehearsed rollback.

## The app

**"Ledger" — an order-invoicing service, Java 8, Spring-style layering.**

| Property | Value |
|---|---|
| Language / build | Java 8, Maven, ~40 modules |
| Line count | ~60k LOC (own code ~25k, generated/report code ~35k) |
| Persistence | Hibernate 4.x + JDBC, PostgreSQL |
| XML | JAXB-marshalled invoices, `javax.xml.bind`, XSD-generated |
| Imports | ISO-8859-1 CSV files from a legacy mainframe |
| i18n | `Locale`-formatted invoice text (de-DE, fr-FR, tr-TR) |
| Tests | JUnit 4 + Mockito 1.x, ~900 tests |
| Problems deliberately planted | `sun.misc.Unsafe` buffer pool, `Class.newInstance()` plugin loader, `AccessController.doPrivileged`, unguarded `new String(bytes)`, platform-locale `DateFormat` |

## Requirements

1. `jdeps --jdk-internals` inventory, fully classified, with owners.
2. Compiles clean at `--release 21`. Zero suppressed errors, zero `-Xlint` skips
   you cannot justify in writing.
3. **No** `sun.*`/`jdk.internal.*` imports and **no** `setAccessible(true)` on JDK
   classes, proven by grep and by `ReflectionReachabilityTest`.
4. JAXB via explicit `jakarta.xml.bind` dependency; XML output byte-identical to a
   fixture captured on JDK 8.
5. Parity tests for the four behavioural risk classes, all passing on 8 and 21:
   encoding round-trip, locale golden files, iteration order, hash/equality.
6. Animal Sniffer + forbidden-apis green in CI, each failing on a deliberate
   violation.
7. Scored risk ledger (MATH_FOUNDATION.md §1) with total effort ≤ 20 person-days
   or an explicit justification.
8. Canary plan with named SLO gates and a **measured** rollback time from a drill.
9. `--add-opens` count is zero, or every flag has a `LEGACY-####` ticket.
10. A one-page memo defending the target-JDK choice and the sequencing.

## Phased plan

### Days 1–2 — Inventory (do not skip this)

```bash
mvn -q clean package -DskipTests
jdeps --jdk-internals --multi-release 21 -R target/ledger.jar | sort -u > inventory.txt
mvn dependency:tree -Dverbose > deps.txt
grep -rn 'setAccessible(true)\|sun\.misc\|jdk\.internal' src/ > reflection-risk.txt
grep -rn 'new String(\|FileReader(\|FileWriter(' src/main/java | grep -v Charset
```

Expected: a hand-sized list. Every line becomes a ledger row with a type from
MATH_FOUNDATION.md §2. **Deliverable:** `ledger.csv` scored and sorted.

### Days 3–5 — Compile

```bash
mvn clean compile -Dmaven.compiler.release=21 2> err.txt
grep -c 'error:' err.txt
```

Work the failures in type order: removed modules → direct internal APIs →
reflection paths → bytecode generators. The removed-module fixes are the fastest
wins and they unblock the rest, because `javax.xml.bind` failures mask everything
behind them.

Then `mvn dependency:tree | grep -c javaee` must be `0` — no `javax.xml.bind`
shadow jar left in the closure.

**Deliverable:** green compile, blocker count to zero or a decision to stop.

### Days 6–8 — Test and parity

```bash
mvn -q clean test -Dmaven.compiler.release=21
```

Expect two classes of failure, and they are different problems:

| Failure class | What it means | Fix |
|---|---|---|
| `NoSuchMethodError` / `InaccessibleObjectException` | Mockito 1.x + Hibernate 4 bytecode generation | Upgrade the libraries |
| Golden-file mismatch | CLDR or charset change | Decide which output is *correct*, pin it, commit it |

The second class is where the two weeks' value comes from. When a de-DE currency
format changes, **you decide** whether the new CLDR output is acceptable — that is
a business decision, and a test failure is how it surfaces at 09:00 rather than in
an invoice dispute at 14:00.

Then add the four parity tests (THEORY.md §6): encoding round-trip against an
ISO-8859-1 fixture, per-locale golden files, explicit iteration-order assertions
anywhere code depends on order, and `ReflectionReachabilityTest` from
CODE_DEEP_DIVE.md §7.

**Deliverable:** full suite green on 8 and 21, with the parity tests provably
failing when you break the invariant.

### Days 9–10 — Harden

Add the two gates (CODE_DEEP_DIVE.md §6 shows the `pom.xml`), verify each fails on
a deliberate violation, and reduce `--add-opens` to zero. For the remaining
flags, write the `LEGACY-####` ticket references into the Dockerfile.

Grep gate that must return empty:

```bash
grep -rn '^import sun\.\|^import jdk\.internal\.' src/main/java
```

**Deliverable:** CI green with the gates in it; flags ticketed.

### Days 11–12 — Canary and rollback drill

Tag both images and push both:

```bash
mvn clean package -Dmaven.compiler.release=21
docker build -t ledger:jdk8 . && docker push ledger:jdk8
docker build -t ledger:jdk21 . && docker push ledger:jdk21
```

Deploy 1% to the canary, hold for a full business cycle (in the lab: replay a
weekday and a weekend traffic file from your load generator). Gate on sample size
*and* SLO, per MATH_FOUNDATION.md §4 — not on elapsed time.

Then the drill: inject a regression, roll back, **measure** the wall-clock.

```bash
kubectl -n lab set image deploy/ledger ledger=ledger:jdk8
time kubectl -n lab rollout status deploy/ledger --timeout=300s
```

**Deliverable:** measured rollback time, SLO gates written down with numbers, and
a shadow-divergence report on the four risk classes.

### Days 13–14 — Memo and decommission

Write the memo (one page): target JDK and why, blocker summary, what you chose not
to fix, rollback numbers, and the decommission list. Then execute the first items
on that list, even in the lab — `--add-opens` flags removed, old image tagged for
deletion, no `-source 8` fallback left in CI.

## Rubric (100 points)

| # | Criterion | Pts | Full marks |
|---|---|---|---|
| 1 | `jdeps` inventory complete and correctly classified | 10 | Every line typed as replace / upgrade-lib / add-opens, each with an owner |
| 2 | Ledger scored with the MATH_FOUNDATION formula | 8 | Scores computed correctly; ordering defended in one paragraph |
| 3 | Compiles clean at `--release 21` | 12 | No suppressed errors; `-Xlint:all` clean or each warning justified in a comment |
| 4 | No internal-API usage remains | 10 | Greps empty; `ReflectionReachabilityTest` green; zero un-ticketed `--add-opens` |
| 5 | JAXB migration correct | 8 | `jakarta.xml.bind` explicit; XML byte-identical to the JDK 8 fixture |
| 6 | Encoding parity test | 8 | ISO-8859-1 round-trip passes on 8 and 21; fails when the charset is removed |
| 7 | Locale/CLDR golden files | 8 | Per-locale files committed; tr-TR casing asserted; each diff justified as a decision |
| 8 | Iteration-order and hash/equality tests | 4 | Each proves it catches the break it targets |
| 9 | Static gates in CI | 8 | Animal Sniffer + forbidden-apis both run; each fails on a deliberate violation |
| 10 | Build config correct | 6 | `maven.compiler.release`, Surefire UTF-8, enforcer on build JDK |
| 11 | Canary plan with numeric SLO gates | 8 | `min_samples` and thresholds stated; holds through weekday + weekend |
| 12 | Rollback drill measured | 6 | Under 5 min, no rebuild, wall-clock recorded from an actual run |
| 13 | Sequencing discipline | 4 | Library upgrades and the JDK bump are separable commits / releases |
| 14 | Decommission list executed | 4 | Flags removed, old image tagged for deletion, no `-source` fallback left |
| 15 | Memo quality | 6 | Target-JDK decision defended; "what we chose not to fix" stated explicitly |

**Deductions.** −3 for an untracked `--add-opens` or `--add-exports`. −5 for a
canary gated on elapsed time with no sample-size requirement. −5 for "it compiles,
so it works" reasoning anywhere in the write-up. −10 if a rollback requires a
rebuild.

**Done when.** Points 1, 3, 4, 5, 6, 9, and 12 are all-or-nothing gates — if any
one is missing the migration is not complete regardless of total score, because
each corresponds to a failure mode that reaches production.