# CODE_DEEP_DIVE — Recursion
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
import java.util.Arrays;
public final class Recursion { // countdown O(n); fib-naive O(φⁿ); memo O(n)
    public static long fact(int n) { // T(n)=T(n-1)+O(1) → O(n) time, O(n) stack
        if (n < 0) throw new IllegalArgumentException("n<0"); // O(1) guard
        if (n <= 1) return 1;                    // O(1) base
        return n * fact(n - 1);                  // O(1) + recurse
    }
    public static long fibNaive(int n) { // Θ(φⁿ) — demo only
        if (n <= 1) return n;                    // base
        return fibNaive(n - 1) + fibNaive(n - 2); // two branches
    }
    public static long fibMemo(int n) { // O(n) states × O(1)
        long[] m = new long[n + 1]; Arrays.fill(m, -1); // O(n) init
        return dfs(n, m);                         // O(n)
    }
    private static long dfs(int n, long[] m) { // memo invariant: stored=final
        if (n <= 1) return n;                    // O(1)
        if (m[n] != -1) return m[n];             // O(1) hit
        return m[n] = dfs(n - 1, m) + dfs(n - 2, m); // compute once
    }
    public static long fibLoop(int n) { // O(n) time, O(1) space — depth-safe
        if (n <= 1) return n;                    // O(1)
        long a = 0, b = 1;                       // O(1)
        for (int i = 2; i <= n; i++) { long c = a + b; a = b; b = c; } // O(n)
        return b;                                // O(1)
    }
}
```

## 2. Complexity Annotations
- `fact`: depth n, frames O(n); Java overflows stack ~10⁴ — loop for big n.
- `fibNaive`: tree ~φⁿ nodes; `fibMemo`: n states once each.
- `fibLoop`: same O(n), no stack; preferred for n>5000.
- Sentinel `-1` valid only because fib ≥0; else use boolean[] computed.

## 3. Pitfalls (5 + fixes)
1. Missing base → infinite recursion/StackOverflow. Fix: bases first, test 0/1.
2. `fact` int overflow at 13! → long/BigInteger + document.
3. Memo sentinel collides with valid -1 answers → separate boolean[].
4. Deep recursion (n=10⁵) → StackOverflow; rewrite iterative.
5. Exponential naive in production → memo/tab mandatory; time n=40 demo.

## 4. Micro-Opts
- Tail countdown → explicit loop (Java has no TCO).
- `Arrays.fill` O(n) dominates tiny n — lazy HashMap memo alternative.

## 5. Test Snippets
```java
assert Recursion.fact(5) == 120;
assert Recursion.fibMemo(10) == Recursion.fibLoop(10);
assert Recursion.fibMemo(0) == 0; // base
try { Recursion.fact(-1); assert false; } catch (IllegalArgumentException ok) {}
```

## 6. Checklist
- [ ] Bases + negative guard. [ ] Sentinel safety. [ ] Depth note.
- [ ] Naive/memo/loop timed (n=40 gap).
