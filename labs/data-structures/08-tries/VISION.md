# VISION — Tries (Prefix Trees) (`08-tries`)
> Mastery path: from API user → implementer → selector → designer.

## Where you are
You can use `Trie` for autocomplete, spell-check, IP routing, dictionaries. Mastery means knowing
when NOT to use tries and what breaks at scale (resize pauses, skew, FPR, fan-out).

## Level 1 — Fluent user (this week)
- Pick the right stdlib type without hesitation (list vs deque vs map vs tree vs heap vs trie vs bloom).
- Recall complexity rows cold (FLASHCARDS 80%+ first-try).
- Write edge-safe client code: empty checks, null policy, comparator/hashCode correctness.

## Level 2 — From-scratch implementer (next 2 weeks)
- Reimplement `Trie` blind: layout, invariant, all of insert-word, search, startsWith, delete-word, count-prefix.
- Derive amortized / height / FPR math (MATH_FOUNDATION §7 without notes).
- Benchmark scaling and explain every bend in the curve.

## Level 3 — System selector (month 2)
- Choose across families with a 1-page tradeoff memo (throughput, latency p99, memory, ordering, durability).
- Examples: hash vs tree for index; heap vs sorted array for top-K; trie vs hash for prefix; bloom pre-filter before disk.
- Know concurrent variants: `ConcurrentHashMap`, copy-on-write, lock-striped queues, off-heap stores.

## Level 4 — Designer (month 3+)
- Adapt the structure: bounded/LRU variant, compressed trie, counting bloom, B-tree paging, d-ary heap tuning.
- Reason about persistence/IO: serialization, SSTable + bloom, mmap, cache lines.
- Teach it: 10-min whiteboard of tries invariant → ops → costs → failure modes.

## Milestones & signals
- [ ] L1: QUIZ ≥13/15 closed-book; EXERCISES E1–E3 green.
- [ ] L2: blind reimplementation + oracle test 5k ops green.
- [ ] L3: MINI_PROJECT benchmark memo with a justified recommendation.
- [ ] L4: REAL_WORLD_PROJECT deployed/toy-prod with metrics + postmortem of one bug.

## Anti-goals
- Memorizing without deriving; benchmarking without warmup; using bloom as source of truth.
- Premature custom structures when stdlib suffices — custom code must earn its complexity.

## 2-week plan (5h/week)
| Week | Sessions | Exit proof |
|---|---|---|
| 1 | THEORY + E1–E3 + QUIZ | blind skeleton compiles, edge battery green |
| 2 | MATH §7 pen work + E4–E5 + MINI_PROJECT | benchmark memo with justified pick |

## Resources (verify links before citing)
- OpenDSA visualizers + CLRS chapters matching tries.
- Your JDK's stdlib source (`src.zip`): read the real `resize`/`sift`/`rotate` once.
- JMH samples if you outgrow `nanoTime` harnesses.

## Next labs
- Pair with neighbors: arrays↔linked, stacks↔queues, hash↔tree, heap↔sorted, trie↔hash, bloom↔LSM.
- Then tackle the matching `advanced-*` / `*-deep` lab in this repo for production hardening.
