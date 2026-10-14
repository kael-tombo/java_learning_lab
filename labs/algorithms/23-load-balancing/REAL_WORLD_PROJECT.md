# Real-World Project: Shard Assignment Evaluator

## Problem

A key-value service with 6 shards must add 2 more without reshuffling most
keys. Build an evaluator that compares consistent hashing, rendezvous
hashing, and modulo hashing on remap fraction and load balance.

## Inputs

- `keys.txt`: one routing key per line (at least 5,000 keys).
- `pool_before.txt`: one server name per line (6 names).
- `pool_after.txt`: one server name per line (8 names, a superset).
- Virtual-node count passed as a program argument.

## Steps

1. Load keys and both pool files; reject empty pools or key sets.
2. Implement modulo hashing as the baseline (hash key, mod pool size).
3. Implement consistent hashing with the given virtual-node count.
4. Implement rendezvous hashing with the documented weight function.
5. Assign all keys under before and after pools for each method.
6. Compute remap fraction and max-to-mean load ratio per method.
7. Emit `evaluation.csv` with rows (method, remapped, ratio_before, ratio_after).
8. Write a one-page recommendation naming the method and virtual-node count.

## Acceptance criteria

1. Modulo hashing remaps substantially more keys than the ring method.
2. Ring remap fraction is within 10 points of the ideal 2/8 for uniform keys.
3. Max-to-mean ratio is reported for every method on both pools.
4. Rendezvous and ring agree that only a minority of keys move.
5. Empty input files exit with a message instead of an exception trace.
6. `evaluation.csv` contains all three methods with four numeric columns.
7. All output uses plain ASCII characters.

## Constraints

- Plain Java only, no external libraries; deterministic hash function.
- Single-threaded run; 5,000 keys must finish in under 10 seconds.
- Recommendation must cite measured numbers, not general claims.
