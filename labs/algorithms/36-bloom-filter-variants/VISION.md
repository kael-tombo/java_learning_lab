# VISION — Bloom Filter Variants
> Direction: from "maybe present" as a curiosity to budgeted false-positive engineering with measured rates.

## Where this sits
- Plain Bloom: 1 bit per position, no deletes, FPR = (1 - e^(-kn/m))^k, optimal k = (m/n) ln 2.
- Counting: byte counters buy deletes at ~4-8x space. Cuckoo: two buckets plus relocation, deletes natively, strong at low FPR. Quotient: quotient/remainder slots, compact and cache-friendly.
- The family answers set-membership under memory pressure; exact structures answer when memory allows.

## 4-week direction
- Week 1: hand-place apple/banana/cherry into 64 bits with double hashing; find mango's bits.
- Week 2: finish MINI_PROJECT; complete the k-sweep table from real runs.
- Week 3: write the variant-selection paragraph from measured trade-offs, not slogans.
- Week 4: REAL_WORLD_PROJECT review; whiteboard the FPR formula derivation sketch in 10 minutes.

## Done criteria
- Derive k_opt by minimizing the FPR expression (calculus sketch) without notes.
- Explain delete-safety for counting vs plain from the counter/bit mechanics.
- Size (m, k) for any (n, FPR budget) pair on demand.

## Non-coverage
- This lab does not implement cuckoo or quotient filters; selection knowledge, not implementations, is the goal.
- No adversarial-hash or cryptographic analysis; seeds are operational, not security, controls.
- Learned-index replacements are out of scope.

## Pitfalls
- Sizing m from hope instead of the formula, then discovering saturation in production.
- Deleting from a plain Bloom filter and manufacturing false negatives.
- Quoting theoretical FPR while never measuring the canary rate.

## Adjacent labs
- Pair with 34-data-stream-algorithms (Count-Min is the frequency cousin) and any caching lab for the negative-path speedup pattern.
- Revisit whenever a hot path consults an exact store for mostly-absent keys.

## Weekly drills
- Recompute k_opt = (m/n) ln 2 for a fresh (m, n) pair in under 2 minutes.
- Re-derive the FPR formula from the single-bit-set probability without notes.
- Name the delete story (safe/unsafe/how) for plain, counting, cuckoo, quotient.

## Anti-roadmap
- Do not deploy without the canary FPR measurement; theory alone is not a rate.
- Do not delete from plain bit arrays; that path manufactures false negatives.
