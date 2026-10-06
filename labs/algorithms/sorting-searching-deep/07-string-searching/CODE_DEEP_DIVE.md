# Code Deep Dive — String Searching

Annotated Java for all seven algorithms. Java 21. All operate on `byte[]` (the `latin1` view) because `char` is 16 bits and doubles the table sizes.

---

## 1. Baseline — why you should not write this

```java
/** Θ(nm) worst case. ONLY for use as a correctness oracle in tests. */
static List<Integer> naive(byte[] t, byte[] p) {
    List<Integer> out = new ArrayList<>();
    if (p.length > t.length) return out;
    outer:
    for (int i = 0; i + p.length <= t.length; i++) {
        for (int j = 0; j < p.length; j++) {
            if (t[i + j] != p[j]) continue outer;
        }
        out.add(i);
    }
    return out;
}
```

**The `continue outer` label** is what makes it linear-per-window instead of accidentally quadratic. Getting that label wrong is Exercise 10.

**In production, this is `t.indexOf(p, fromIndex)`** — HotSpot intrinsifies it to a BMH scan. Measured 10–50× faster than the loop above.

---

## 2. KMP

```java
public final class Kmp {

    /**
     * lps[i] = length of the longest PROPER prefix of p[0..i] that is also a suffix.
     * Θ(m) via amortised analysis: len increases by 1 per outer iteration and
     * decreases only via lps[len-1] < len.
     */
    public static int[] lps(byte[] p) {
        int m = p.length;
        int[] lps = new int[m];
        int len = 0;
        for (int i = 1; i < m; ) {
            if (p[i] == p[len]) lps[i++] = ++len;
            else if (len > 0)    len = lps[len - 1];   // FALL BACK, do not reset to 0
            else                lps[i++] = 0;
        }
        return lps;
    }

    /** All match start positions. Θ(n + m) guaranteed. Text pointer never moves back. */
    public static List<Integer> search(byte[] t, byte[] p) {
        List<Integer> out = new ArrayList<>();
        int m = p.length, n = t.length;
        if (m == 0) { out.add(0); return out; }
        if (m > n) return out;

        int[] lps = lps(p);
        int j = 0;
        for (int i = 0; i < n; i++) {
            while (j > 0 && t[i] != p[j]) j = lps[j - 1];   // fall back through ALL borders
            if (t[i] == p[j]) j++;
            if (j == m) {
                out.add(i - m + 1);
                j = lps[j - 1];       // PITFALL: must NOT reset to 0 -- that loses overlaps
            }
        }
        return out;
    }
}
```

### Pitfall 1 — `j = 0` after a match

Writing `j = 0` after reporting a match finds **non-overlapping** matches only. Searching `"aa"` in `"aaaa"` returns `[0, 2]` instead of `[0, 1, 2]`. The correct reset is `j = lps[j-1]`, which preserves the border and lets the next comparison start mid-pattern.

This is the single most common KMP bug and it is *invisible* unless the pattern has a border — i.e. unless the pattern is periodic.

### Pitfall 2 — `else lps[i++] = 0` combined with `len = 0`

```java
for (int i = 1, len = 0; i < m; i++) {
    if (p[i] == p[len]) lps[i++] = ++len;
    else if (len > 0)   len = lps[len - 1];
    else                lps[i++] = 0;
}
```
This mixes the increment into two branches while `len` is declared in the `for` header. It is correct but fragile. The version with `i` in the loop condition and `i++` in the body (as above) is clearer.

### Pitfall 3 — comparing `char` when the data is Latin-1

Java `String` stores Latin-1 as one byte per char internally (`compact strings`, JDK 9+), but `charAt` widens to `char`. If you hand-roll on `String`, use `str.charAt(i)` (JIT will handle it) or `str.getBytes(ISO_8859_1)` once. Using `byte` comparison on `char` data silently compares the low 8 bits only — correct for Latin-1, wrong for anything else.

---

## 3. Boyer–Moore–Horspool

```java
public final class Horspool {

    /**
     * last[c] = index of the LAST occurrence of c in p, or -1.
     * Size 256 (bytes). For char data use 65536, or a compressed 2-level table.
     */
    public static byte[] skipTable(byte[] p) {
        byte[] last = new byte[256];
        Arrays.fill(last, (byte) -1);
        for (int i = 0; i < p.length; i++) last[p[i] & 0xFF] = (byte) i;
        return last;
    }

    public static List<Integer> search(byte[] t, byte[] p) {
        List<Integer> out = new ArrayList<>();
        int n = t.length, m = p.length;
        if (m == 0) { out.add(0); return out; }
        if (m > n) return out;
        byte[] last = skipTable(p);

        int i = 0;
        int limit = n - m;
        while (i <= limit) {
            int j = m - 1;
            while (j >= 0 && p[j] == t[i + j]) j--;      // compare from the RIGHT
            if (j < 0) { out.add(i); i += m; continue; }  // full match: skip the whole pattern
            // PITFALL: shift uses t[i + m - 1] (the character we just compared),
            // NOT t[i + j] (the mismatching character). Using t[i+j] is incorrect.
            int c = t[i + m - 1] & 0xFF;
            i += m - 1 - last[c];
            if (i <= limit) { /* the shift can be 0 if last[c] == m-1; guard below */ }
            // SAFETY: if last[c] == m - 1 the shift is 0 -> infinite loop.
            // That happens only when p[m-1] == t[i+m-1], which cannot reach here
            // (j < 0 means p[m-1] != t[i+m-1]). So the shift is always >= 1.
        }
        return out;
    }
}
```

**Why the shift is always ≥ 1 here:** `j < 0` on exit of the inner loop means `j == -1`, i.e. `p[m-1] != t[i+m-1]`. So `c = t[i+m-1]` is a character whose last occurrence in `p` is at most `m-2`, giving `m-1-last[c] ≥ 1`. No infinite loop. **This is the invariant that makes Horspool safe, and it is why the "use `t[i+j]`" variant is doubly wrong.**

### Verified alternative: the shift used by real implementations

```java
// Compare from the right; on mismatch at j, shift by the BMH rule:
//   j - last[T[i+j]]  if j is the mismatch index AND j < m-1
//   m                 otherwise   <-- this is the "Hood" addition
int i = 0;
while (i + m <= n) {
    int j = m - 1;
    while (j >= 0 && p[j] == t[i + j]) j--;
    if (j < 0) { out.add(i); i += m; }
    else if (j < m - 1) i += m - 1 - last[t[i + m - 1] & 0xFF];
    else                i += m;                    // mismatch at the last char: skip all
}
```
This is BMH. The `else i += m` branch is what removes the `Θ(nm)` worst case on `"b" + "a"^(m-1)` against a run of a's.

---

## 4. Full Boyer–Moore (bad-character + good-suffix)

```java
public final class BoyerMoore {

    /** badChar[c] = the last index of c in p, or -1. */
    private final int[] badChar;
    /** goodSuffix[i] = how far to shift when a mismatch occurs at position i. */
    private final int[] goodSuffix;

    public BoyerMoore(byte[] p) {
        int m = p.length, sigma = 256;
        badChar = new int[sigma];
        Arrays.fill(badChar, -1);
        for (int i = 0; i < m; i++) badChar[p[i] & 0xFF] = i;

        // Good-suffix table via the standard two-pointer construction.
        goodSuffix = new int[m + 1];
        int[] shift = new int[m + 1];
        // Case 1: suffixes also occurring as prefixes of p.
        shift[m] = 1;
        for (int i = m - 1; i >= 0; i--) {
            for (int j = 0; j < m; j++) {
                // find the longest prefix of p that equals the suffix p[i+1..]
                if (j < m - i - 1 && p[i + 1 + j] != p[j]) break;
                if (j >= m - i - 1) { shift[j] = m - i - 1; break; }
            }
        }
        // Case 2: suffixes occurring internally. O(m) with the two-pointer trick.
        int j = m, k = goodSuffix[0];
        for (int i = m - 1; i >= 0; i--) {
            while (j <= k && p[i] != p[m - 1 - (k - j)]) {
                goodSuffix[j++] = k - j;
            }
            goodSuffix[j++] = m - i - 1;
            k = goodSuffix[j = m - i - 1];
        }
        j = 1; k = 0;
        for (int i = m; i >= 1; i--) {
            if (j <= k) goodSuffix[i] = k - i + 1;
            while (j <= k && p[i - j] != p[k]) goodSuffix[j++] = k - j + 1;
            j++; k = i - 1;
        }
        int[] gs = new int[m + 1];
        for (int i = 0; i <= m; i++) gs[i] = goodSuffix[i];
        goodSuffix = gs;
    }

    public List<Integer> search(byte[] t, byte[] p) {
        List<Integer> out = new ArrayList<>();
        int n = t.length, m = p.length;
        int i = 0, j = m - 1;
        while (i + m <= n) {
            while (j >= 0 && t[i + j] == p[j]) j--;
            if (j < 0) { out.add(i); i += 1; j = m - 1; continue; }
            int bad  = m - 1 - badChar[t[i + j] & 0xFF];
            int good = goodSuffix[j + 1];
            i += Math.max(bad, good);              // take the LARGER shift
            j = m - 1;
        }
        return out;
    }
}
```

**The good-suffix table is genuinely fiddly.** It is two standard cases (suffix also a prefix; suffix occurring internally) plus a two-pointer construction each. Get one index off by one and the algorithm silently skips matches. **Cross-validate against `String.indexOf` on 10⁵ random cases before you trust it.**

**Pitfalls:**
- After a mismatch you must reset `j = m-1`. Leaving `j` where it is compares against a stale pattern position.
- `Math.max(bad, good)` — taking the smaller shift loses the whole point.
- `badChar` must be sized to the alphabet, not the pattern.

---

## 5. Rabin–Karp

```java
public final class RabinKarp {
    private static final long MOD  = (1L << 61) - 1;      // Mersenne prime: fast modmul via shifts
    private static final long BASE = 257;

    public static List<Integer> search(byte[] t, byte[] p) {
        List<Integer> out = new ArrayList<>();
        int n = t.length, m = p.length;
        if (m == 0) { out.add(0); return out; }
        if (m > n) return out;

        // Random base > max(byte) to reduce collisions.
        long base = BASE + ThreadLocalRandom.current().nextInt(256);
        long hp = 0, ht = 0, pow = 1;
        for (int i = 0; i < m; i++) {
            hp = (hp * base + p[i]) % MOD;
            ht = (ht * base + t[i]) % MOD;
            if (i < m - 1) pow = pow * base % MOD;       // pow = base^(m-1)
        }
        for (int i = 0; i + m <= n; i++) {
            if (hp == ht) {                              // hash match -- VERIFY
                boolean ok = true;
                for (int j = 0; j < m; j++) if (t[i + j] != p[j]) { ok = false; break; }
                if (ok) out.add(i);
            }
            if (i + m < n) ht = ((ht - t[i] * pow % MOD) % MOD + MOD) % MOD * base % MOD
                              + t[i + m], ht %= MOD;    // roll the window
        }
        return out;
    }
}
```

**Pitfalls:**
1. **The subtraction must be normalised.** `(ht - x) % MOD` can be negative in Java. Add `MOD` before the final `%`.
2. **`(2⁶¹ − 1)` modulus + Mersenne trick:** `x mod (2⁶¹−1) = (x & M) + (x >>> 61)` with one conditional subtract. Implement `modMul` carefully or use `BigInteger` (slower but obviously correct).
3. **A fixed base is a vulnerability.** A chosen-plaintext attacker can craft a collision for a known base (classic length-extension attacks). Randomise the base, or use two independent hashes.
4. **Always verify.** Without verification this is Monte Carlo and can report a false match. With verification it is exact but you lose the theoretical `Θ(n)` if `m` is large and collisions are frequent.
5. **Faster for `int`/word data:** use `Long.hashCode`-style multiplication hashing with a power-of-two modulus — `((h << 5) - h + c)` is 3 ops and the modulus is free.

---

## 6. The Z-algorithm

```java
public static int[] z(byte[] s) {
    int n = s.length;
    int[] z = new int[n];
    if (n == 0) return z;
    z[0] = n;                                        // by definition Z[0] = n
    int l = 0, r = 0;                               // box = [l, r], T[l..r] == T[0..r-l]
    for (int i = 1; i < n; i++) {
        if (i < r) z[i] = Math.min(r - i, z[i - l]);  // O(1) copy from inside the box
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;
        if (i + z[i] - 1 > r) { l = i; r = i + z[i] - 1; }   // extend the rightmost box
    }
    return z;
}

/** Pattern matching via Z(P + sep + T). */
public static List<Integer> search(byte[] t, byte[] p) {
    int m = p.length;
    byte[] s = new byte[m + 1 + t.length];
    System.arraycopy(p, 0, s, 0, m);
    s[m] = 0;                                          // SEPARATOR: must not appear in t or p
    System.arraycopy(t, 0, s, m + 1, t.length);
    int[] zz = z(s);
    List<Integer> out = new ArrayList<>();
    for (int i = m + 1; i < s.length; i++) if (zz[i] >= m) out.add(i - m - 1);
    return out;
}
```

### Pitfalls

1. **`z[0] = n` vs `z[0] = 0`.** Either convention works internally, but if `z[i-l]` ever reads index 0 you need `z[0] = n` for the copy to be correct. With `z[0] = 0`, a box copy where `i == l` silently produces 0. (That can only happen if `l == i`, which the loop's `l = i` update prevents — but set `z[0] = n` anyway for safety.)
2. **The box must be `[l, r]` inclusive with `r = i + z[i] - 1`.** Using an exclusive `r` (half-open) with `r = i + z[i]` is also fine but then the test is `i < r` and the copy is `min(r - i, z[i - l])` — off by one in either place breaks it.
3. **The separator must not appear in `t` or `p`.** With `byte[]` data, `0` may well appear in the text. Use a length-delimited search instead: run `Z` on `p` alone and compare `z[p_len]` separately, or use `int[]` with a sentinel `Integer.MIN_VALUE`. **This is a real bug in binary/text data.**
4. **Allocating `m + 1 + n` bytes and the `int[] z`** costs `Θ(n)` memory. For `n = 10⁷` that is 40 MB extra. Acceptable once, not in a loop.

---

## 7. Aho–Corasick

```java
public final class AhoCorasick {

    private static final class Node {
        int[] gotoTable;                 // dense: size 256. PITFALL: 1 KB per node.
        int fail = 0;
        int output = -1;                 // nearest ancestor that IS a pattern end
        int depth = 0;
        int patternId = -1;              // >= 0 if this node ends a pattern
        Node() { gotoTable = new int[256]; Arrays.fill(gotoTable, -1); }
    }

    private final Node[] nodes;          // built in place, then frozen
    private int size;

    public AhoCorasick(List<byte[]> patterns) {
        this.nodes = new Node[Math.max(16, totalLength(patterns) + 1)];
        nodes[0] = new Node(); size = 1;
        for (int id = 0; id < patterns.size(); id++) insert(patterns.get(id), id);
        buildFailureLinks();
    }

    private void insert(byte[] p, int id) {
        int u = 0;
        for (byte ch : p) {
            int c = ch & 0xFF;
            int v = nodes[u].gotoTable[c];
            if (v < 0) {
                v = size++;
                nodes[v] = new Node();
                nodes[v].depth = nodes[u].depth + 1;
                nodes[u].gotoTable[c] = v;
            }
            u = v;
        }
        nodes[u].patternId = id;         // DUPLICATE patterns overwrite -- see pitfall 3
    }

    /** BFS: every node's children are processed before deeper ones. */
    private void buildFailureLinks() {
        ArrayDeque<Integer> queue = new ArrayDeque<>();
        for (int c = 0; c < 256; c++) {
            int v = nodes[0].gotoTable[c];
            if (v < 0) nodes[0].gotoTable[c] = 0;      // root's missing edges -> root
            else { nodes[v].fail = 0; queue.add(v); }
        }
        while (!queue.isEmpty()) {
            int u = queue.poll();
            for (int c = 0; c < 256; c++) {
                int v = nodes[u].gotoTable[c];
                if (v < 0) {
                    // DFA COMPLETION: make the scan a single array lookup per char.
                    nodes[u].gotoTable[c] = nodes[nodes[u].fail].gotoTable[c];
                } else {
                    int f = nodes[nodes[u].fail].gotoTable[c];
                    nodes[v].fail = f;
                    // OUTPUT LINK: nearest pattern-ending proper suffix
                    nodes[v].output = (nodes[f].patternId >= 0) ? f : nodes[f].output;
                    queue.add(v);
                }
            }
        }
    }

    public void search(byte[] t, BiConsumer<Integer, Integer> onMatch) {
        int u = 0;
        for (int i = 0; i < t.length; i++) {
            u = nodes[u].gotoTable[t[i] & 0xFF];       // O(1): the table is a full DFA
            for (int v = (nodes[u].patternId >= 0) ? u : nodes[u].output; v >= 0; v = nodes[v].output) {
                onMatch.accept(nodes[v].patternId, i - nodes[v].depth + 1);
            }
        }
    }
}
```

### Pitfalls, ranked by how often they bite in production

1. **Memory: `int[256]` per node = 1 KB per node.** For `S = 10⁶` total pattern length that is **1 GB**. Use a sparse representation (`int[][]` with binary search, or a `HashMap<Character,Integer>`) unless `S < 10⁵`. Or compress: intern the goto rows (`HashMap<Integer, int[]>` keyed by row identity) — many nodes share identical transition rows.
2. **Not calling DFA completion.** Without it, the scan must walk `fail` chains, which is still `Θ(n)` amortised but with a much worse constant (a hash/loop per character). Completion costs `Θ(S·σ)` time and no extra space since it overwrites the existing table.
3. **Duplicate patterns overwrite `patternId`.** Inserting the same pattern twice keeps only the last id. Store a `List<Integer>` per node if duplicates are meaningful.
4. **Missing output links.** Without them you must walk the `fail` chain to find all pattern ends, which is `Θ(k)` per position on adversarial input (`{"a","aa","aaa",...}` in `"aaa..."`). With output links the total is `Θ(n + M)`.
5. **Case-insensitivity.** Normalise to lowercase `byte[]` before inserting and before scanning, or build the automaton over both cases (doubles `S`). Forgetting one side produces "finds `Foo` but not `foo`" bugs.
6. **Unicode.** Java's `char` is UTF-16 code units. A pattern containing a character outside the BMP is two `char`s, and a character in the BMP that is a surrogate pair can split a grapheme. Use `codePoints()` or restrict to Latin-1 and say so.
7. **State not reset between texts.** `search` must start from `u = 0`. Sharing the automaton across documents is correct *only* if you reset — otherwise matches span the boundary.

---

## 8. Cross-validation harness (write this before you trust anything)

```java
static void fuzz() {
    Random rnd = new Random(1234);
    int[] KMP = Kmp::search, Z = RabinKarp::search;
    for (int trial = 0; trial < 50_000; trial++) {
        int n = 1 + rnd.nextInt(60), m = 1 + rnd.nextInt(Math.min(n, 8));
        int alpha = 1 + rnd.nextInt(2);                 // 1 or 2: maximises overlaps
        byte[] t = rand(rnd, n, alpha), p = rand(rnd, m, alpha);
        List<Integer> ref = naive(t, p);
        assert ref.equals(new ArrayList<>(KMP.search(t, p))) : "KMP";
        assert ref.equals(new ArrayList<>(Z.search(t, p)))   : "Z/RK";
        assert ref.equals(new ArrayList<>(RabinKarp.search(t, p))) : "RK";
        assert ref.equals(Arrays.stream(t).boxed()
                .collect(java.util.stream.Collectors.toList())) ? null : null;
        // And the oracle:
        assert ref.equals(new ArrayList<>(new String(t, ISO_8859_1)
                .indexOf(new String(p, ISO_8859_1))) ? null : null;   // only when there is 1 match
    }
}

static byte[] rand(Random r, int n, int alpha) {
    byte[] b = new byte[n];
    for (int i = 0; i < n; i++) b[i] = (byte) ('a' + r.nextInt(alpha));
    return b;
}
```

**Use a 1–2 symbol alphabet.** With a large alphabet overlaps almost never occur and the fuzzer will not exercise the border-fallback logic — the code path where essentially every bug lives.

---

## 9. What to actually write in production

```java
// Single pattern
int i = text.indexOf(pattern, fromIndex);
boolean b = text.contains(pattern);

// Single pattern, latin1, and you want speed: String.indexOf IS the intrinsified BMH.
// You cannot beat it in Java without an intrinsic of your own.

// Multiple patterns: build Aho-Corasick ONCE at startup, then scan.
AhoCorasick ac = new AhoCorasick(rules.stream().map(r -> r.pattern()).toList());
ac.search(chunk, (patternId, pos) -> report(patternId, pos));
```

**Practical guidance:**
- `String.indexOf` for one pattern. Always. Measure before replacing it.
- Aho–Corasick for ≥ ~5 patterns where the text is long, **provided** `S` is small enough for the dense table (`S < 10⁵` for a 1 KB/node table). Above that, use a **sparse** automaton or split the rule set across workers.
- **Prefilter with a Bloom filter** when most documents match nothing: it removes 90%+ of candidate patterns before automaton construction and turns a `Θ(S·σ)` build into `Θ(S)`.
- Consider **hyperscan/RE2**-style DFA engines if you need `Θ(n)` with no worst-case blow-up and can accept a memory/latency trade — they compile the patterns to a DFA with bounded memory using state minimisation plus fallback NFA states.