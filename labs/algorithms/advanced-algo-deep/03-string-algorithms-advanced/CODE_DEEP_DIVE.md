# Code Deep Dive — String Algorithms Advanced

A compact but complete Java implementation of the lab's core algorithm(s), with the pitfalls annotated.

```java
public final class KMP {
    public static int[] prefix(String p) {
        int[] pi = new int[p.length()];
        for (int i = 1, j = 0; i < p.length(); i++) {
            while (j > 0 && p.charAt(i) != p.charAt(j)) j = pi[j - 1];
            if (p.charAt(i) == p.charAt(j)) j++;
            pi[i] = j;
        }
        return pi;
    }

    /** Returns the index of the first occurrence of p in t, or -1. */
    public static int search(String t, String p) {
        if (p.isEmpty()) return 0;
        int[] pi = prefix(p);
        for (int i = 0, j = 0; i < t.length(); i++) {
            while (j > 0 && t.charAt(i) != p.charAt(j)) j = pi[j - 1];
            if (t.charAt(i) == p.charAt(j)) j++;
            if (j == p.length()) return i - j + 1;
        }
        return -1;
    }

    /** Z-array: Z[i] = longest prefix of s matching s starting at i. */
    public static int[] z(String s) {
        int n = s.length(), l = 0, r = 0;
        int[] Z = new int[n];
        for (int i = 1; i < n; i++) {
            if (i <= r) Z[i] = Math.min(r - i + 1, Z[i - l]);
            while (i + Z[i] < n && s.charAt(Z[i]) == s.charAt(i + Z[i])) Z[i]++;
            if (i + Z[i] - 1 > r) { l = i; r = i + Z[i] - 1; }
        }
        return Z;
    }
}
```

## Pitfalls

- Resetting the text index on mismatch silently restores Θ(n·m).
- π is indexed on the pattern; the text pointer is never rewound.
- Rabin–Karp must confirm a hash hit with a character comparison.
- A full RK match needs the sentinel to stop Z-entries spanning the boundary.
- Z[0] is undefined/0 by convention — do not use it as a match length.
- Manacher radii are per-centre; off-by-one between "radius" and "length" shifts every answer by one.

## Why the bounds hold

- **KMP search**: Θ(n+m) time, Θ(m) — text pointer never retreats.
- **Rabin–Karp search**: Θ(n+m) expected time, Θ(1) — hash confirm on hit.
- **Z-array build**: Θ(n) time, Θ(n) — right-edge window moves only right.
- **Manacher**: Θ(n) time, Θ(n) — mirror palindrome reuse.
- **Suffix automaton build**: Θ(n) alphabet-dependent time, Θ(n) — ≤ 2n-1 states.
- **Naive matching**: Θ(n·m) time, Θ(1) — the baseline to beat.

## Takeaway

# Theory — String Algorithms Advanced
