# Visual Guide

## Buffer States

Empty buffer (capacity=5):
`
head=0, tail=0, size=0
[0] [1] [2] [3] [4]
 H/T
`

After adding A, B, C:
`
head=0, tail=3, size=3
[A] [B] [C] [·] [·]
 H        T
`

After polling A, B and adding D, E:
`
head=2, tail=5→0, size=3
[D] [E] [C] [·] [·]
     T    H
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: CircularBuffer.java

The generic circular buffer uses an Object array internally. The offer method returns false if full (non-blocking). The add method overwrites the oldest element when full. The poll method returns null if empty.

Key patterns:
- Use Object[] for generic array (no generic array creation in Java)
- @SuppressWarnings("unchecked") for casts
- Separate head/tail management from element access
