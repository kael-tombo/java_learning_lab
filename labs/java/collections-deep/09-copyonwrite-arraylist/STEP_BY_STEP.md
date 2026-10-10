# Step by Step: Copies and Snapshots

Start: `list = [A, B]` (array V1).

## add(C)

1. Lock. `es = V1`. `copyOf` → V2 = `[A, B, _]`.
2. `V2[2] = C`. `setArray(V2)`. Unlock. List is now V2.
3. V1 (`[A,B]`) still exists in memory — any iterator holding it is
   unaffected.

## Snapshot divergence

4. `it1 = iterator()` → pins V2.
5. `remove(A)`: scan V2 → index 0 → lock → copy minus slot 0 → V3 = `[B,C]`
   → publish. `it1` still walks `[A, B, C]`-minus-nothing — visits A, B.
6. `it2 = iterator()` → pins V3, walks `[B, C]`.
7. `it1.next()` sequence: A, B (C invisible — added... actually C was in
   V2; adjust: it1 sees exactly V2 = [A,B,C]... trace your own V-numbers;
   the rule never changes: iterator sees its pinned array, nothing else).

## Lost-race drill

8. Thread T1 scans V3 for B → index 0 (no lock yet).
9. Thread T2 `remove(B)` publishes V4 = `[C]` first.
10. T1 locks, sees `snapshot(V3) != current(V4)`, re-scans: B absent in V4
    → returns false instead of deleting index 0 (which now holds C).
    Stale index 0 would have removed C — the wrong element.

## set-same heartbeat

11. `set(0, B)` on `[B, C]` (equal value): copies anyway, publishes the
    copy. Content identical, ordering progress broadcast.
