# EXERCISES — Sorting & Searching Deep Track
> Implement + trace + edge cases (Java templates). Track `sorting-searching-deep`.

## E1. Quicksort vs mergesort vs heapsort
```java
import java.util.*;
public class E1 {
    // TODO: 3-way quick (random pivot), top-down merge w/ aux, in-place heap
    // Benchmark random/sorted/dupes; note stability + locality differences
    // Edge: empty, n=1, all equal
}
```

## E2. Counting + radix (LSD)
```java
public class E2 {
    // TODO: counting with offset for negatives; stable scatter via prefix
    // TODO: LSD radix base 256, 4 passes for 32-bit; stable per digit
    // Edge: k huge (reject), negative keys, stability check
}
```

## E3. Binary variants + answer-search
```java
public class E3 {
    // TODO: lowerBound/upperBound/rotated/peak (half-open discipline)
    // TODO: first-true predicate search (capacity/koko/sqrt)
    // Edge: empty, dupes, overflow-safe mid
}
```

## E4. Quickselect + dual-heap median
```java
public class E4 {
    // TODO: quickselect kth; two-heap streaming median
    // Edge: k bounds, duplicates, even/odd median
}
```

## E5. KMP + Rabin-Karp
```java
public class E5 {
    // TODO: prefix function; scan with fallback; report all matches
    // TODO: rolling hash + verify on hit (spurious check)
    // Edge: empty pattern/text, overlapping matches, hash collisions
}
```

## E6. Fuzz + benchmark harness
```java
import java.util.*;
public class E6 {
    // TODO: fuzz sorts vs Arrays.sort (10k cases); search vs linear scan
    // TODO: KMP/RK/Aho vs naive on random texts; benchmark 1k→10M
}
```

## Edge-case checklist
- [ ] Empty/singleton. [ ] All equal/dupes. [ ] Sorted/reverse.
- [ ] Overflow-safe mid/sums. [ ] Stability verified.

## Trace template
| step | state | decision | invariant holds? |
|---|---|---|---|
| 1 | init | base | yes |

## Review rubric
- [ ] All 6 compile + pass fixtures. [ ] Trace tables filled.
- [ ] Complexity stated per exercise. [ ] One pitfall noted each.
