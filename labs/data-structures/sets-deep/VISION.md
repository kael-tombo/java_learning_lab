# VISION — Sets Deep

Vision: pick the set by ordering needs and memory density, not by habit.

## Mental models
- HashSet = HashMap keys: O(1) unordered de-dup.
- TreeSet = RB tree: O(log n) sorted set with navigation.
- LinkedHashSet = HashSet + insertion-order iteration.
- BitSet = words of bits for dense integer domains.
- EnumSet = bitmask over enum ordinals.

## Decision table
| Workload | Pick |
|---|---|
| De-dup unordered | HashSet |
| Sorted set + floor/ceiling | TreeSet |
| Insertion-order set | LinkedHashSet |
| Dense int-domain set | BitSet |
| Flags from an enum | EnumSet |

## Career path
- Shows up in: interviews, flag/feature systems, de-dup pipelines.
- Story: "I know why TreeSet needs compareTo(equals consistency) and why BitSet beats HashSet for dense domains."

## Done when
- [ ] Pick the right set for a workload
- [ ] Explain BitSet memory win
- [ ] Mini + real-world projects shipped
