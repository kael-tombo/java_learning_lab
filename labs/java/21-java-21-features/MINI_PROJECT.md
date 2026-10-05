# MINI PROJECT — Java 21 Features: Modernize a Legacy Module

## Goal (2 weeks, ~8–10h)
Rewrite an `Order` processing module (POJOs + visitor + thread pool) into records + sealed + patterns + virtual threads, proving less code and equal behavior.

## Requirements
### Functional
1. `record Order/LineItem/Customer` with compact-ctor validation; `SequencedCollection` for history (reversed view test).
2. `sealed interface Payment permits Card, Cash, Voucher`; exhaustive `switch` pricing without default; record patterns in `case Card(var n, var e)`.
3. Pattern refactor: eliminate 5+ instanceof-cast sites; `switch` expression returns values (arrow cases, `yield` where needed).
4. Virtual-thread gateway: `newVirtualThreadPerTaskExecutor()` order-fetch fan-out with structured scope or CF+deadline.
5. Text-block SQL/JSON fixtures; pattern-guarded validation (`case String s when s.isBlank()`).
### Non-functional
- LOC −30% vs legacy (counted); zero raw casts; sealed switch has no default yet compiles.
- 16+ tests: record validation, exhaustive switch (new permit breaks compile — documented), pattern branches, virtual fan-out merge.
- README: before/after diff gallery + feature-to-line-saved table.
- JFR note: virtual-thread run shows no pinning warnings.

## Phases
### Week 1 — Data + Types (4–5h)
- Records, sealed, exhaustive switches, pattern cleanup.
- Deliverable: legacy test suite green on modern code.
### Week 2 — Concurrency + Proof (4–5h)
- Virtual-thread fan-out, LOC count, JFR check.
- Deliverable: modernization report with numbers.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Records | Validated compact ctors | Used | Mutable kept |
| Sealed+switch | Exhaustive, no default | Sealed used | Default hides gaps |
| Patterns | Record/guard idioms | Basic instanceof | Casts remain |
| Virtual | Correct scope+deadline | Used | Pool kept |
| Tests + LOC | 16+ tests, −30% proven | 10+ tests | No proof |

Pass ≥ 70. Stretch: string-templates preview (with `--enable-preview` note) or scoped-value propagation demo.
