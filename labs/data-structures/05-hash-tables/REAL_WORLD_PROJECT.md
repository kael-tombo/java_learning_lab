# Lab Notebook: Hash Table from Scratch to Session Cache

Day 1 - array with a hash. Buckets as chains, String keys, djb2-style
mix, resize at load 0.75. By evening: put/get/remove pass 2k randomized
ops against HashMap with zero mismatches. First surprise logged: sorted
keys cluster when the mixer is weak.

Day 2 - the mixer earns its keep. Swap in a finalizer avalanche step,
rerun the cluster probe, record max chain length before and after. Note
the exact commit where p99 get latency drops; keep both numbers.

Day 3 - open addressing spike. Linear probing variant behind the same
interface, tombstone deletes, probe-count histogram. Compare with chains
at load factors 0.5, 0.7, 0.9 and write down where probing degrades.

Day 4 - session cache on top. TTL map over the chaining table: put with
expiry, lazy sweep on access plus a periodic purge, eviction count
metric. Session storm script: 50k logins, 20 percent immediate logouts,
expiry correctness checked against a LinkedHashMap model.

Day 5 - failure week in miniature. Adversarial keys sharing hashCode,
null handling policy, remove-during-iteration guard, resize under load
with concurrent reads forbidden and documented. Each gets a regression
test named after the incident.

Day 6 - numbers. Insert/get/delete timings at 100k entries, bytes per
entry from heap deltas, max chain and probe histograms, resize count vs
theory. No invented targets: report measured values beside Big-O
expectations (average O(1), resize amortized).

Day 7 - writeup. Which variant backs the cache and why, the mixer
evidence, the load factor chosen with data, and the one bug the oracle
caught. Attach notebook log, histograms, and the storm reconciliation.

Bar. Oracle parity across both variants 12, adversarial plus TTL
correctness 10, measurement honesty 8.
## Presenter notes
- Demo the cluster probe live.
- Show both chain histograms.
- End with the chosen load factor.
