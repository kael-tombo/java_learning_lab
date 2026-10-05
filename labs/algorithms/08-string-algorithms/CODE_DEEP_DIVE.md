# CODE_DEEP_DIVE — String Algorithms (KMP + Rolling Hash)
> Java implementation with complexity annotations + pitfalls.

## 1. Complete Implementation
```java
public final class Strings { // KMP O(n+m); RK O(n+m) expected
    public static int[] prefix(String p) { // π table O(m) amortized
        int m = p.length(); int[] pi = new int[m]; // O(m)
        for (int i = 1, j = 0; i < m; i++) { // O(m) total (j only falls ≤ rises)
            while (j > 0 && p.charAt(i) != p.charAt(j)) j = pi[j - 1]; // amortized O(1)
            if (p.charAt(i) == p.charAt(j)) j++; // O(1)
            pi[i] = j;                       // longest border
        }
        return pi;                           // O(1)
    }
    public static int kmp(String t, String p) { // O(n) scan
        if (p.isEmpty()) return 0;           // O(1) convention
        int[] pi = prefix(p);                // O(m)
        for (int i = 0, j = 0; i < t.length(); i++) { // O(n) amortized
            while (j > 0 && t.charAt(i) != p.charAt(j)) j = pi[j - 1]; // fallback
            if (t.charAt(i) == p.charAt(j)) j++; // O(1)
            if (j == p.length()) return i - j + 1; // match
        }
        return -1;                           // O(1)
    }
    public static int rabinKarp(String t, String p) { // expected O(n+m)
        int n = t.length(), m = p.length();  // O(1)
        if (m > n) return -1;                // O(1)
        long base = 256, mod = 1_000_000_007L, h = 1, hp = 0, ht = 0; // O(1)
        for (int i = 0; i < m - 1; i++) h = h * base % mod; // O(m) power
        for (int i = 0; i < m; i++) { hp = (hp * base + p.charAt(i)) % mod; ht = (ht * base + t.charAt(i)) % mod; } // O(m)
        for (int i = 0; i <= n - m; i++) {    // O(n) slides
            if (hp == ht && t.startsWith(p, i)) return i; // O(m) verify only on hit
            if (i < n - m) ht = (ht - t.charAt(i) * h % mod + mod) % mod * base % mod + t.charAt(i + m), ht %= mod; // O(1) roll — careful precedence
        }
        return -1;                           // worst O(nm) adversarial
    }
}
```

## 2. Complexity Annotations
- `prefix`: j increments ≤ m total; fallbacks ≤ increments → ≤2m steps.
- `kmp`: same potential Φ=j over text scan → O(n).
- RK: O(1) roll; verification charged to hash hits (adversary → O(nm)).

## 3. Pitfalls (5 + fixes)
1. Empty pattern convention → define 0 (document).
2. `char` vs code points (emoji) → use codePoints for non-BMP.
3. RK mod overflow in `*h` → long + mod each mult.
4. Hash-only equality → false positives; always verify.
5. KMP `pi` off-by-one (`pi[j]` vs `pi[j-1]`) → trace "ababaca" fixture.

## 4. Micro-Opts
- Dual mod / verify to kill FPs; precompute powers for multi-query.

## 5. Test Snippets
```java
assert Strings.kmp("ababcab", "abc") == 2;
assert Strings.prefix("ababaca").length == 7; // [0,0,1,2,3,1,1]
assert Strings.rabinKarp("hello", "ll") == 2;
```

## 6. Checklist
- [ ] π fixture. [ ] Empty-pattern policy. [ ] Verify-on-hit. [ ] Surrogate note.
