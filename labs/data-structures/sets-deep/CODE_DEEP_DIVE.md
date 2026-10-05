# CODE_DEEP_DIVE — Sets Deep

## HashSet internals
- `private final HashMap<E, Object> map;` with `PRESENT = new Object();`.
- add → `map.put(e, PRESENT) == null` to report true only when the key was absent.
- equals on elements drives `hash`; contract: equal objects must have equal hashCodes.

Pitfall: mutating an element after it is added breaks contains().

## TreeSet internals
- `private final NavigableMap<E, Object> m;`.
- add → `m.put(e, PRESENT) == null`.
- Uses comparators or Comparable for ordering; 0 from compare == equal.

Pitfall: a comparator inconsistent with equals yields surprising set behavior vs HashSet.

## LinkedHashSet
- `extends HashSet` and uses a LinkedHashMap under the hood.
- add → LinkedHashMap.put; iteration visits nodes in insertion order.

## BitSet
- `long[] words`.
- `set(i)` = `words[i>>6] |= (1L << i)`.
- `and/or/xor` iterate min/max words arrays.
- cardinality uses Long.bitCount.

Pitfall: BitSet grows but does not shrink on clear; calling size() returns allocated-ish words*64.

## EnumSet
- Uses one or more long masks; `RegularEnumSet` uses a long; `JumboEnumSet` uses long[].
- Static factories: allOf/of/rangeOf/complementOf.

## Choosing
- HashSet: de-dup only.
- TreeSet: sorted iteration / navigation constraints.
- LinkedHashSet: insertion-stable iteration.
- BitSet: dense integer domain, SIMD-friendly word ops.
- EnumSet: enum flags flags.

## Debug tips
- Verify equals/hashCode before blaming HashSet.
- For TreeSet, verify compareTo is consistent with equals (iteantis 0 → same identity).
- BitSet: remember its iterator-less API; call nextSetBit in a loop.
