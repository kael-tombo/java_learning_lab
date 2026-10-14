# VISION — Data Stream Algorithms
> Direction: from storing streams to summarizing them — exact when small, bounded-error when huge.

## Where this sits
- Streaming summaries trade exactness for O(1)-ish memory: sampling (reservoir), frequency (Misra-Gries, Count-Min, Count Sketch), distinct counting (HyperLogLog), and binary counting (Morris).
- The error direction matters: MG undercounts, CM overcounts, reservoir is exact-uniform but partial.
- Windowing (tumbling/sliding/decay) turns infinite streams into answerable questions.

## 4-week direction
- Week 1: hand-run reservoir on 1..10 with seed 42 until [6,2,8] is unsurprising; prove the k/i rule.
- Week 2: finish MINI_PROJECT; write the MG shortfall argument from decrement rounds.
- Week 3: size a CM sketch from (epsilon, delta) for a concrete key space and rate.
- Week 4: REAL_WORLD_PROJECT review; whiteboard est>=true proof for CM in 5 minutes.

## Done criteria
- State each structure's guarantee and error direction from memory.
- Derive the reservoir uniformity invariant by induction.
- Choose MG vs CM vs exact map for a given (rate, memory, query) triple.

## Non-coverage
- This lab does not implement HyperLogLog or the Morris counter (both are named, sketched, and left as extensions).
- No sliding-window algorithms; all guarantees here assume whole-stream (landmark) windows.
- Adversarial streams against fixed hashes are handled by seed rotation policy, not by new theory.

## Pitfalls
- Treating MG counts as exact; they are lower bounds, short by the decrement count.
- Treating CM estimates as exact; collisions inflate, so capacity-plan from the overestimate side.
- Forgetting the audit sampler; without exact samples, error claims are untestable.

## Adjacent labs
- Pair with 36-bloom-filter-variants (sister sketch family, opposite error direction) and 31-online-algorithms (one-pass decisions under uncertainty).
- Revisit when any pipeline says "store everything first"; the sketch menu is the alternative.

## Weekly drills
- Prove the reservoir k/n invariant for arrivals n and n+1 aloud in under 3 minutes.
- Bound an MG shortfall from the decrement-round count on a fresh example.
- Size CM width/depth from an (epsilon, delta) pair without looking them up.

## Anti-roadmap
- Do not quote MG counts as exact or CM estimates as exact; name the direction every time.
- Do not ship a sketch without the exact-sampled audit that prices its error.
