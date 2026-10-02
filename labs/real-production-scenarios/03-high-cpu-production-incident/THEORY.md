# THEORY — High-CPU Pathology on the JVM

## 1. Four CPU pathologies and their profiler signatures

High CPU is a symptom with (at least) four distinct diseases. The
flame-graph/stack profile distinguishes them in seconds — if you know
what to look for:

| Pathology | Flame-graph signature | Thread state | GC activity | This lab's case? |
|---|---|---|---|---|
| **ReDoS / algorithmic blowup** | 85% in one library subtree (`Pattern$GroupHead/Branch/Curly`) | RUNNABLE, user-space, no syscalls | Minimal (compute-bound) | **Yes** — ROOT_CAUSE.md lines 12–21 |
| **GC storm** | Wide `GarbageCollector`/`G1ParTask` frames, mutator starved | RUNNABLE + long STW pauses | Allocation rate ≈ heap/s, pause % climbing | No (profiling excluded it) |
| **Lock contention** | `park`/`ObjectMonitor` frames, few hot methods | BLOCKED/WAITING, low *useful* CPU | Normal | No |
| **Runaway loop / busy spin** | One application frame dominating, no I/O | RUNNABLE | Normal | Differential to rule out |

The incident's fingerprint — RUNNABLE + 100% user CPU + near-zero GC +
`Pattern.match` dominance — uniquely identifies compute-bound library
pathology. Profiling *before* theorizing is the whole game (contrast the
Atlassian Graviton lesson: PMU data killed the "not enough horsepower"
folk theory the same way).

## 2. Why NFA backtracking explodes

`java.util.regex` is an NFA simulation with backtracking: on overall
failure it replays every untried alternative at every position. Nested
quantifiers + overlapping alternation multiply choices per position, so
paths grow as O(2^n) in input length (ROOT_CAUSE.md lines 51–57: 40 a's →
~1 trillion paths). Atomic groups `(?>…)` and possessive quantifiers
(`++`, `*+`) commit to the first match and never re-enter — O(2^n) → O(n)
by deleting the search tree, not by speeding it up.

## 3. The thread-pool amplifier

A 200-thread pool turns 5 concurrent 30 s requests into 300 thread-seconds
of demand per second — total saturation within seconds, with legitimate
traffic queueing behind (Little's law: L = λW with W blown 200×).
Fixed pools bound blast radius *only if* per-request work is bounded;
unbounded work (untimed regex) converts the pool from bulkhead to fuse.
Fixes compose in layers: bound the work (atomic groups), bound the wait
(100 ms `TimeoutPattern`), bound the blast (bulkheads/rate limits),
detect the class (CI ReDoS scan + `ReDoSScanner`).

## 4. Timeout honesty: interrupt ≠ cancel

Java regex is not interruptible mid-match in any clean sense — the lab's
`TimeoutPattern` interrupts the *thread* and treats the outcome as
non-match, while the pool variant abandons the worker (`future.cancel`)
and lets the orphaned evaluation die whenever the engine notices. Both
trade correctness theater (a late match arriving after timeout) for
bounded latency. The engine default (`policyPattern.matches → false` on
timeout) encodes the incident's key judgment: *an unevaluated rule must
fail closed, never hang open*.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Jan Goyvaerts, "Preventing Regular Expression Denial of Service
  (ReDoS)", regular-expressions.info (page updated 8 Aug 2025): the
  prevention rules behind this lab's fixes — alternatives must be
  mutually exclusive (else 2^N permutations, e.g. `( |\s)*` on spaces);
  quantified tokens in sequence must exclude each other (negated classes
  like `[^b]*`); groups with inner quantifiers must not carry outer
  quantifiers unless mutually exclusive; make groups atomic and
  quantifiers possessive wherever possible; hard-coded-regex servers can
  prevent ReDoS *entirely* by review, user-supplied-regex servers must
  use timeouts or RE2-style non-backtracking engines. The lab's
  `(?>…)`/`++` fixes and `TimeoutPattern` are textbook instances.
  <https://www.regular-expressions.info/redos.html>
- OWASP reference drift (correction to SOLUTION.md line 679): the
  `cheatsheetseries…/Regular_Expression_Denial_of_Service_Cheat_Sheet.html`
  URL now 404s; current canonical entry points are the OWASP Community
  ReDoS attack page and the Denial-of-Service cheat sheet:
  <https://community.owasp.org/attacks/Regular_expression_Denial_of_Service_-_ReDoS>
  <https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html>
- Microsoft Security Briefs (MSDN Magazine, May 2010, "ReDoS Attacks and
  Defenses"): <50-char payloads suffice — corroborates this incident's
  ~40-char trigger and the lab's "length caps never suffice" lesson.
