# JMM Foundations — README

Welcome to the bedrock lab of the memory track. The Java Memory Model
(JLS 17.4, rewritten by JSR-133 for Java 5) answers one question:
**which writes can a read observe?** This lab builds the five
happens-before edges and the two guarantees (DRF implies sequential
consistency; causality bans out-of-thin-air values) that every later
lab assumes.

## What you will learn

- The six happens-before sources: program order, monitor rule,
  volatile rule, thread start/join rules, final-field freeze, and the
  documented `java.util.concurrent` library edges.
- Why a data race (conflicting accesses unordered by happens-before)
  forfeits every intuition, and why race-freedom buys back sequential
  consistency (JLS 17.4.3-17.4.5).
- What causality guarantees even for racy code: only staleness and
  reordering, never invented values (JLS 17.4.8).
- What "observable behavior" means and why it licenses optimization.

## The five runnable demos (all guaranteed, never races)

| # | Class | Edge shown | Exact expected output |
|---|-------|-----------|----------------------|
| 1 | `StartEdge` | `start()` hb thread body | `expected checksum = 1499500`, thread observes `1499500` |
| 2 | `JoinEdge` | worker body hb `join()` return | `sum = 41541750 (expected 41541750)` |
| 3 | `LockEdge` | `unlock` hb next `lock` | `count = 2000000 (expected 2000000)` over 8 x 250000 |
| 4 | `LatchEdge` | `countDown()` hb `await()` return | `latch-published graph fully visible: true` |
| 5 | `CausalityFloor` | none (racy on purpose) | `out-of-thin-air values: 0`, every value in `[0, 100000]` |

Demos 1-4 assert `true` on every run on any JDK 9+ (verified on JDK 23).
Demo 5 is racy by design; its verdict (no invented values) is what is
asserted, not any particular interleaving.

## How to work this lab

1. Read `THEORY.md` first (the DRF guarantee, the hb rules, causality,
   observable behavior, one paragraph of JSR-133 history).
2. Read `CODE_DEEP_DIVE.md` alongside the sources in `src/`; each
   snippet names the JLS rule it exercises.
3. Do `EXERCISES.md` in order: break an edge, restore it, swap one edge
   for another, then explain why the verdict changed in hb terms.
4. Use `QUIZ.md` and `FLASHCARDS.md` for recall; `DEBUGGING.md` when a
   demo surprises you (it should not — that is the point).
5. Finish with `REFLECTION.md` and the interview set in `INTERVIEW.md`.

## Where this fits

- Previous: nothing in this track — this is the foundation.
- Next: `02-reordering` shows what happens with *no* edges (the Dekker
  anomaly, forbidden under sequential consistency, routine on hardware).
- Later: `03-memory-barriers` compiles these edges to fences;
  `04-final-semantics` deepens the freeze edge; `05-dcl-pattern`
  applies volatile publication end to end.

## Requirements

- JDK 9 or later (demos verified on JDK 23); no dependencies.
- Outputs must be pure ASCII on the console; prose files are UTF-8.
- Run each demo repeatedly: guaranteed demos print the same verdict
  every time. That repeatability *is* the lesson.
