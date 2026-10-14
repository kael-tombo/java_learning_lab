# MINI_PROJECT — Data Stream Algorithms
> Build a one-pass sketch toolkit (reservoir, Misra-Gries, Count-Min) that reports its own error against exact counts.

## Inputs
- Integer event stream file, one id per line; reference stream of 11 items from MOCK Q2 and 8-item stream from MOCK Q3.
- Parameters: reservoir k, MG counter budget m, sketch width/depth with explicit hash seeds.

## Build steps
1. Implement reservoir sampling (Algorithm R) with injectable Random; verify seed 42 on stream 1..10 with k=3 prints [6, 2, 8].
2. Implement Misra-Gries with m=2; on the reference stream report candidates {1=4, 2=1} beside exact counts.
3. Implement Count-Min with 2 rows, width 5, fixed hashes; print est vs true per queried key and assert est >= true.
4. Add an `--exact` audit mode: hash-map exact counts on the same file, then a comparison table (key, true, MG est, CM est).
5. Document per-structure memory in bytes as a function of its parameters.

## Acceptance criteria
1. Reservoir output matches [6, 2, 8] exactly for seed 42 on 1..10.
2. MG output matches candidates {1=4, 2=1} with true_count_1=6 shown beside it.
3. CM asserts est >= true for every queried key on the 8-item stream (q=5 est 5, q=2 est 3, q=7 est 3).
4. Audit mode table prints all three columns from a single pass plus one exact pass.
5. Memory formulas (k slots, m counters, w*d cells) are stated with the element size used.
6. Re-running with the same seed reproduces byte-identical output.

## Analysis prompts
1. How does the MG shortfall for key 1 relate to the number of decrement rounds?
2. Which key inflates most under CM, and which hash collision causes it?
3. What breaks if the stream distribution shifts mid-file (sliding-window need)?

## Non-goals
- Sliding-window and time-decayed variants, distributed sketches, and HyperLogLog (named in VISION only).

## Worked reference (verified outputs)
- Reservoir k=3, seed 42, stream 1..10 prints [6, 2, 8]; same seed must give byte-identical output.
- MG(m=2) prints candidates {1=4, 2=1} with true_count_1=6; CM prints ests 5/3/3 for q=5/2/7, each >= true.

## Stretch
- Add a Morris-counter demo (increment with probability 2^-c) and compare its estimate spread against exact over 10 seeds.
- Add tumbling windows (reset every N items) and show how recall changes vs landmark mode.
