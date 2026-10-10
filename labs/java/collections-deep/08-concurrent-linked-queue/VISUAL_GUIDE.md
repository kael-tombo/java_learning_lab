# Visual Guide: Lagging Pointers and Self-Links

## Healthy queue with lag

```
head     tail(real end: C)
  ↓        ↓
  H(dummy)→ A(1) → B(2) → C(3) → null
  └ lag 2 ┘        └ tail 1 behind: allowed
```

Both pointers stale, chain exact. Correctness lives in `next` links, not
in the pointers.

## Two racing offers at B

```
T1: CAS(B.next: null → C1)  ✓ wins → C1 member
T2: CAS(B.next: null → C2)  ✗ loses, sees q=C1 → appends after C1
Result: B → C1 → C2
```

One CAS serializes both threads — no mutex, no queueing.

## Poll leaves dummies; head lags

```
poll → returns 1:   H ⇢(self)   A(dead) → B(2) → C(3)
head ──────────────→ A           straggler at H restarts
```

## Self-link detector

```
walker at P:  P.next == P   ⟹   p == q   ⟹   restart from head
```

## Slack-2 rule of thumb

```
staleness 0–1: tolerate (no CAS)     ← common case, zero extra traffic
staleness ≥ 2: CAS pointer forward   ← amortized 1 CAS per ~2 ops
```

Tail-CAS traffic halves; worst walk length grows by a small constant.
That exchange — bounded staleness for halved contention — is the design's
economic center.
