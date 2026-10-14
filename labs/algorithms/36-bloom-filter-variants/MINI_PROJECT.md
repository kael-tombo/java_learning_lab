# MINI_PROJECT — Bloom Filter Variants
> Build plain, counting, and sized Bloom filters plus an empirical-vs-formula FPR report.

## Inputs
- Word list file (one token per line, e.g. 10k dictionary words) and a disjoint query file of 5k absent words.
- Parameters m (bits), k (hashes); reference point m=1000, n=100, k=7 with FPR ~0.008194 and k_opt 6.93.

## Build steps
1. Implement plain Bloom with double hashing; verify member queries true and count false positives on the absent file.
2. Compute the theoretical FPR (1 - e^(-kn/m))^k and k_opt = (m/n) ln 2; print beside the measured rate.
3. Implement counting Bloom (byte counters); demonstrate insert/delete/query with the lab a/b sequence.
4. Sweep k in {3, 5, 7, 10} at fixed m/n and table measured vs theoretical FPR.
5. Document when to pick counting (deletes needed), cuckoo (deletes plus lower space at low FPR), quotient (cache-friendly local table) in one paragraph each.

## Acceptance criteria
1. Plain filter reports zero false negatives on all inserted words.
2. Reference point prints fpr=0.008194 and k_opt=6.93.
3. Counting demo reproduces a=false b=true after delete (lab sequence).
4. Sweep table has 4 rows of (k, measured, theoretical) from real runs.
5. Variant-choice paragraph covers all three alternatives with a distinct selection reason each.
6. Hash seeds are fixed and documented so the measured rates reproduce exactly.

## Analysis prompts
1. Where does measured FPR deviate most from theory across the sweep, and why?
2. What saturates first as n grows past design capacity: memory or the FPR budget?
3. How many bits per counter does your counting variant need before overflow risk?

## Non-goals
- Cuckoo/quotient implementations (specified, not built), scalable auto-growing filters, and adversarial-hash analysis.

## Worked reference (verified outputs)
- Reference point m=1000, n=100, k=7 prints fpr=0.008194 with k_opt=6.93; the sweep must bottom out near k=7.
- Counting demo prints a=false b=true after the delete; plain filter reports zero false negatives on members.

## Stretch
- Build a minimal cuckoo filter (2 buckets, kick-out cap) and compare measured FPR at equal bytes.
- Add a saturation experiment: grow n to 5x design and plot measured FPR against theory.
