# CODE_DEEP_DIVE — Linear Search
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.Objects;
public final class LinearSearch { // Θ(n) worst/avg, Θ(1) best/space
    public static <T> int indexOf(T[] a, T key) { // O(n) probes
        if (a == null) throw new IllegalArgumentException("null array"); // O(1) guard
        for (int i = 0; i < a.length; i++)        // n iters worst
            if (Objects.equals(a[i], key))        // O(1) null-safe probe
                return i;                         // first occurrence
        return -1;                                // exhaustion = absent
    }
    public static int indexOf(int[] a, int key) { // primitive overload, == safe
        for (int i = 0; i < a.length; i++)        // O(n)
            if (a[i] == key) return i;            // O(1)
        return -1;
    }
    public static <T> int sentinel(T[] a, T key) { // fewer branches; same O(n)
        // caller places key at a[n-1] sentinel; loop without bounds check
        int i = 0; while (!Objects.equals(a[i], key)) i++; // O(n)
        return i;
    }
}
```

## 2. Complexity Annotations
- Loop `n` iters worst; `1` best (index 0); avg `(n+1)/2` present-uniform.
- `Objects.equals` O(1) (reference + equals); expensive `equals` multiplies constant.
- Space O(1): index + refs. Sentinel saves 1 cmp/iter (constant only).

## 3. Pitfalls (5 + fixes)
1. `==` on objects → identity bug. Fix: `Objects.equals`.
2. Enhanced-for loses index → use indexed loop when index needed.
3. Null array vs null key conflated → guard array, tolerate key.
4. Returning boolean loses position → return index (-1 miss).
5. Sentinel without restore corrupts data → document ownership or copy.

## 4. Micro-Opts
- Unroll 4× for huge primitive scans (JIT often does it).
- Early length-0 return avoids loop setup (trivial but clean).

## 5. Test Snippets
```java
assert LinearSearch.indexOf(new Integer[]{5,2,9}, 2) == 1;
assert LinearSearch.indexOf(new Integer[]{}, 1) == -1; // empty
assert LinearSearch.indexOf(new String[]{null,"a"}, null) == 0; // null key
assert LinearSearch.indexOf(new Integer[]{2,2,2}, 2) == 0; // first
```

## 6. Checklist
- [ ] `.equals` null-safe. [ ] First-occurrence tested. [ ] Empty/null/duplicate green.
- [ ] Best/avg/worst comment on method.
