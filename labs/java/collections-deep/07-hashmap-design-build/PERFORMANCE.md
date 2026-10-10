# Performance: Open-Addressing Map

| Operation | Average | Worst |
|---|---|---|
| get / put / remove | O(1) (~1.5–6 probes at α ≤ 0.7) | O(n), all keys collide |
| resize (amortized/insert) | O(1) | O(n) single grow |
| iteration | O(capacity) | scans EMPTY + tombstones |

## Why it can beat chaining

One flat array: probe steps hit adjacent slots (same cache line), no node
headers, no pointer chasing. At α = 0.5–0.7 with a good spread, "O(1)"
means ~2 array reads — faster than following a `HashMap.Node` chain.

## Where it loses

- High α: miss cost 50+ probes at 0.9 — chaining with short lists wins.
- Delete-heavy: tombstone buildup degrades every probe until resize;
  backward-shift deletion (IdentityHashMap style) or periodic rebuilds fix
  it at extra delete cost.
- Iteration: O(n) live entries cost O(capacity) time — sparse tables waste
  scans. Chaining iterates only live nodes.
- Adversarial hashes: collide-all-keys → every op O(n) with no treeify
  escape hatch (HashMap falls back to O(log n) trees past 8 per bin).

## Tuning knobs (measured, not guessed)

- Cap α at 0.5–0.7; benchmark miss-heavy vs memory trade at your n.
- Power-of-two sizes + mask avoid `%` division on every probe step.
- Resize ×2 keeps amortized insert O(1); smaller factors (×1.5) save memory
  at more frequent O(n) pauses.
