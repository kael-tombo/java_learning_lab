# Visual Guide: Runs, Tombstones, Resize

## Clustering (linear probing's signature)

```
slots:  0   1   2   3   4   5   6   7
        .   A   B   C   .   .   .   .
            └───── run ─────┘
```

A, B, C hashed to 1, 1, 2 — one run of length 3. Next insert hashing to
1–3 extends it to 4. Runs attract: the longer the run, the more hashes
land in it. This positive feedback is *clustering*.

## Tombstone keeps the chain

```
remove(A):  .   ✝   B   C   .   .   .   .
                ↑ probes pass through
get(B):     idx1 ✝(go) → idx2 HIT
```

## Reuse on insert

```
put(D,idx1): .  D   B   C   .   .   .   .
               ↑ first tombstone reused
```

## Resize dissolves runs (n=8 → 16)

```
before (mask 7):  A@1 B@2 C@3        one run
after  (mask 15): A@1 B@9 C@3        scattered — high bits now matter
```

Rehashing with the wider mask uses previously-ignored hash bits, so runs
shatter. This is also why the spread step matters more after growth.

## Probe-cost curve (linear probing)

```
avg miss probes
 50│                                              × α=0.9: 50
  6│                                  × α=0.7: 6
  2│              × α=0.5: 2.5
    └────────────────────────────────── α →
     0.5     0.7     0.9
```

The knee between 0.7 and 0.9 is the load-cap decision made visible: cap
early (cheap), or pay 50-probe misses (broken).
