# Sizing Worksheet: LSM Pre-Check and Crawler Dedup Filter

Step 1 - state the formula. False-positive rate follows
FPR = (1 - e^(-kn/m))^k with optimal k = (m/n) ln 2. Every sizing claim
below derives from this; the report shows the arithmetic, not slogans.

Step 2 - size the LSM pre-check. For n = 1M keys at 10 bits per key,
m = 10M bits (1.2 MB), k = 7, expected FPR near 0.8 percent. Build it,
then measure observed FPR on 200k absent keys and quote both numbers.

Step 3 - wire the store path. Point reads consult the filter first;
negatives skip disk, positives proceed. The win metric is disk reads
avoided on a 70-percent-absent workload, counted exactly.

Step 4 - size the crawler front-filter. n = 5M URLs at 8 bits per key,
k = 6; duplicates dropped before fetch. Missed-dup cost is zero (Bloom
never yields false negatives); the measured quantity is fetch savings.

Step 5 - hash sourcing. Double hashing from two 64-bit mixes to emulate
k functions; document the scheme and show FPR stability across seeds.

Step 6 - counting variant note. A counting Bloom with 4-bit counters
supports deletes for the crawl frontier; overflow policy stated and
overflow events counted during the churn test.

Step 7 - failure register. Undersized filter (4 bits/key) built on
purpose to show FPR pain; saturated filter with FPR alarm threshold;
serialization round-trip with bit-exact reload check.

Step 8 - hand in. Sizing sheet with formula outputs vs measurements,
read-avoidance counts, fetch savings, and the undersized-filter caution
table. Marks: formula-to-measurement agreement 12, store-path savings
10, edge and churn handling 8.
## Sizing card
- Keep n, m, k posted on the wall.
- Alarm at 2x expected FPR.
- Recount bits after each backfill.
- Never quote FPR without n.
