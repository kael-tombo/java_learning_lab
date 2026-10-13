# Math Foundation: Class File Format

Only counting and bounds arithmetic this lab actually uses. No
continuous mathematics appears in the format; everything below is
directly observable in dumps.

## Pool count identity

```text
real_entries = constant_pool_count - 1
```

Index 0 is the phantom. A pool reporting count 47 holds entries
`#1..#46`. Any tool allocating an array for the pool needs exactly
`count` slots (0 unused) or `count - 1` entries — off-by-one here
shifts every symbolic reference.

## Double-slot stride

```text
next_index(i) = i + 2   if tag(i) in {Long, Double}
                i + 1   otherwise
```

For a pool with L Long/Double entries and N stored items, the highest
used index is N + L (each wide entry donates one dead slot). The
probe's `#12 = Long → #14` is the minimal instance. A parser loop
must branch on the tag, not assume unit stride.

## Header byte reconstruction

```text
major = (b[6] * 256) + b[7]        (unsigned bytes, big-endian)
minor = (b[4] * 256) + b[5]
magic = b[0]*2^24 + b[1]*2^16 + b[2]*2^8 + b[3]  = 0xCAFEBABE
```

Major 61 = bytes `00 3D`; 52 = `00 34`; 65 = `00 41`; 67 = `00 43`.
Range check used by the probe: 45 ≤ major ≤ 67.

## Local-slot partition (probe method `(IZ)I`)

```text
locals = 1 (receiver) + 2 (params x, neg) + 1 (local y) = 4
args_size = 1 + 2 = 3
extra_locals = locals - args_size = 1   (the y slot)
```

In general `max_locals ≥ args_size`, with equality only when the
method declares no locals. Long/double locals additionally consume
two local slots each (parallel to the pool rule).

## Stack-depth bound

`max_stack = 3` in the probe is the maximum over all program points
of (pushes − pops) along any path. The verifier recomputes this bound
and rejects any path exceeding it. Appending straight-line pushes
raises the bound additively; a branch's bound is the max of its arms.

## Frame-count rule

```text
frames_needed = number of control-flow merge points (v50+ code)
```

Straight-line method: 0 merges → 0 frames (attribute absent).
`branchy` (one conditional): 1 merge → ≥1 frame. Each additional
join point (loop back-edge, catch handler, switch arm merge) adds
frames; no other code shape does.
