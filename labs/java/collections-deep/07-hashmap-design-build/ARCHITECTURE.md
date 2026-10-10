# Architecture: Open-Addressing HashMap

## Components

- `Entry[] table` — keys, values, and state (`EMPTY` / `LIVE` / `DELETED`)
  inline. Power-of-two length so index = `spread(hash) & (n-1)`.
- `int size` — live entries only. `int tombstones` (or DELETED count) —
  tracked separately because probes must skip them but iteration must hide
  them.
- `float loadFactor` cap (e.g. 0.7) — trigger: `(size + tombstones) / n`.

## Data flow: put(k, v)

1. `h = (k == null ? 0 : k.hashCode() ^ (h >>> 16))`, `i = h & (n-1)`.
2. Probe `i, i+1, ...` remembering the first tombstone seen.
3. Hit (equals) → overwrite value, return old. Else insert at first
   tombstone (or first empty), `size++`.
4. If `(size + tombstones) > cap * loadFactor` → resize(2n).

## Data flow: get(k) / remove(k)

- `get`: probe until EMPTY (miss) or equals-hit. Probes pass through
  DELETED slots — stopping at a tombstone would lose keys placed beyond it.
- `remove`: same probe; on hit mark DELETED, `size--`, null key/value for
  GC. Tombstone stays until resize.

## Data flow: resize(2n)

Allocate fresh table; re-insert **live entries only** (recompute
`h & (newN-1)`); reset `size` by recounting, `tombstones = 0`. O(n)
hash-and-place — the amortized-O(1)-insert argument, same shape as
ArrayList growth.

## Boundaries

- Full table (no EMPTY) cannot insert — unlike chaining there is no
  fallback. The load cap must fire first; probe loops need a full-cycle
  guard.
- Iteration is O(capacity): must skip EMPTY and DELETED slots.
