# Distinct-Visitor Counter on HyperLogLog

Ledger. An analytics pipe counts distinct visitors per day over 50M
events where exact counting would keep every id in memory. HyperLogLog
answers in kilobytes with a known error: standard error 1.04/sqrt(m),
so m = 16384 registers give about 0.81 percent. That formula is the
contract; everything below tests it.

Sketch core. 64-bit hash split into index bits and rank bits (leading
zeros of the remainder plus one); registers keep maxima; harmonic-mean
estimate with small-range linear counting and large-range correction.
Estimate must sit inside the stated error band on 20 seeded trials.

Redis-compatible caller. PFCOUNT-style add/count/merge over daily
sketches; union of seven dailies must match a fresh sketch over the
concatenated stream within error. Merge path tested on 10 day-pairs.

Cardinality ladder. Exact HashSet vs sketch at 1k, 100k, 10M distinct:
relative error recorded per rung, memory recorded per rung (sketch flat
at 12 KB for m = 16384 while exact grows linearly). The crossover where
exact stops fitting is computed and stated.

Adversarial notes. Poor hash (sequential ids with weak mixer) built on
purpose to show bias; duplicate-heavy stream (sketch must not drift);
single-visitor stream (small-range correction checked); empty sketch
(zero estimate, specified).

Hand in. Sketch, daily-merge CLI, ladder table with errors and bytes,
bias demo, 20-trial error histogram. Marks: error-band agreement 12,
merge correctness 10, ladder plus adversarial honesty 8.
## Error diary
- 20-trial histogram archived.
- Ladder rerun after hash changes.
- Bias demo kept runnable.
- m = 16384 default justified.
- Daily-merge check in CI.
