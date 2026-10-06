# Code Deep Dive — Knapsack Variants

Annotated Java for all six variants plus the two axis-swaps. Java 21.

---

## 1. 0/1 knapsack

```java
public final class Knapsack {

    public record Item(int weight, int value) {}

    /** dp[w] = max value with total weight AT MOST w. */
    public static int solve01(Item[] items, int W) {
        if (W <= 0) return 0;
        int[] dp = new int[W + 1];              // 0 initialisation == the "at most" convention
        for (Item it : items) {
            if (it.weight() <= 0 || it.value() <= 0) continue;
            // DESCENDING -- this is the specification, not an optimisation.
            for (int w = W; w >= it.weight(); w--) {
                dp[w] = Math.max(dp[w], dp[w - it.weight()] + it.value());
            }
        }
        return dp[W];
    }

    /** EXACT weight: dp[w] = max value with total weight EXACTLY w. Returns -1 if W is unreachable. */
    public static int solveExact(Item[] items, int W) {
        final int NEG = Integer.MIN_VALUE / 2;   // PITFALL: NOT 0 -- 0 means "reachable with value 0"
        int[] dp = new int[W + 1];
        Arrays.fill(dp, NEG);
        dp[0] = 0;
        for (Item it : items)
            for (int w = W; w >= it.weight(); w--)
                if (dp[w - it.weight()] != NEG)
                    dp[w] = Math.max(dp[w], dp[w - it.weight()] + it.value());
        return dp[W] == NEG ? -1 : dp[W];
    }

    public static int solveUnbounded(Item[] items, int W) {
        int[] dp = new int[W + 1];
        for (Item it : items)
            for (int w = it.weight(); w <= W; w++)   // ASCENDING -- the item is reusable
                dp[w] = Math.max(dp[w], dp[w - it.weight()] + it.value());
        return dp[W];
    }
}
```

### The one-line difference between 0/1 and unbounded

```java
for (int w = W; w >= it.weight(); w--)   // 0/1
for (int w = it.weight(); w <= W; w++)   // unbounded
```

**Both loops start at an index where `dp[w - weight]` reads the correct row — one reading the previous item's row, one reading the current item's already-updated row.** Test: `items = [(1,3)]`, `W = 10` → `solve01` = `3`, `solveUnbounded` = `30`. **If your test suite does not contain an instance where the two differ, it cannot catch the swap.**

### `NEG` and overflow

`NEG + it.value()` with `NEG = Integer.MIN_VALUE / 2` is safe (stays negative, no wraparound). With `NEG = Integer.MIN_VALUE`, adding a positive value **overflows to a positive number** and `dp[w]` becomes a large positive — the exact-weight version then reports a huge value for an unreachable weight. Use `MAX_VALUE / 2` and check reachability explicitly.

---

## 2. Reconstruction with a `bitset` (memory `Θ(nW/8)` bytes)

```java
public record Plan(int value, boolean[] chosen) {}

public static Plan solve01WithPlan(Item[] items, int W) {
    int n = items.length;
    int[] dp = new int[W + 1];

    // take[i] is a bitset over capacities: bit w set means item i improved dp[w].
    // Memory: n * (W+1)/8 bytes instead of n * (W+1) booleans.
    long[][] take = new long[n][];
    for (int i = 0; i < n; i++) take[i] = new long[(W >>> 6) + 1];

    for (int i = 0; i < n; i++) {
        Item it = items[i];
        for (int w = W; w >= it.weight(); w--) {
            int cand = dp[w - it.weight()] + it.value();
            if (cand > dp[w]) {
                dp[w] = cand;
                take[i][w >>> 6] |= 1L << (w & 63);
            }
        }
    }

    boolean[] chosen = new boolean[n];
    int w = W;
    for (int i = n - 1; i >= 0; i--) {
        if ((take[i][w >>> 6] & (1L << (w & 63))) != 0) { chosen[i] = true; w -= items[i].weight(); }
    }
    return new Plan(dp[W], chosen);
}
```

**Why this matters:** `boolean[][] take` for `n = 200`, `W = 10⁵` is `20 MB` (Java `boolean[][]` has per-array overhead, so more). The `long[][]` bitset version is `200 × 12504 × 8 = 20 MB` too... the real saving is against `int[][]` (`80 MB`). Using `long[]` bitsets: `n × ⌈W/64⌉ × 8` bytes = `n × W / 8` = **2.5 MB** for `n = 200`, `W = 10⁵`. **8× smaller than `int[][]`, 64× smaller than a naive `boolean[][]` with row overhead.**

---

## 3. Bounded knapsack — binary splitting

```java
public static int solveBoundedSplit(Item[] items, int[] count, int W) {
    List<Item> bundles = new ArrayList<>();
    for (int i = 0; i < items.length; i++) {
        int c = count[i], w = items[i].weight(), v = items[i].value();
        int remaining = c;
        for (int size = 1; remaining > 0; size <<= 1) {
            int take = Math.min(size, remaining);
            bundles.add(new Item(w * take, v * take));
            remaining -= take;
        }
    }
    return solve01(bundles.toArray(new Item[0]), W);
}
```

**Trace for `c = 13`:** `size = 1 → take 1` (remaining 12), `size = 2 → take 2` (remaining 10), `size = 4 → take 4` (remaining 6), `size = 8 → take 6` (remaining 0). Bundles: `1, 2, 4, 6`. ✔ `⌈log₂(14)⌉ = 4` bundles.

**Pitfall 1 — bundle weights must not exceed `W`.** A bundle of weight `w·take > W` can never be used; filter them out or you do useless work.

**Pitfall 2 — `size <<= 1` overflows for huge `c`.** With `c = 2³⁰`, `size` reaches `2³⁰` then wraps negative and `Math.min(size, remaining)` returns a negative `take`. Guard: `if (size > remaining) take = remaining; else take = size;` and break.

**Pitfall 3 — completeness.** The bundles must cover **every** count from `0` to `c`, not merely sum to `c`. `{1,2,4,6}` does; `{4,4,4}` does not. **Test with `c = 3` and a `W` that forces exactly 2 copies** — the `{1,2}` decomposition covers 0,1,2,3 ✓ while a bad decomposition would not.

---

## 4. Bounded knapsack — monotone queue, `Θ(nW)`

```java
/**
 * Bounded knapsack, item type by item type.
 * newDp[w] = max over k in [0, c] of ( dp[w - k*p] + k*q )
 * Reparametrised by residue r = w mod p into a sliding-window MAXIMUM.
 */
public static int solveBoundedDeque(Item[] items, int[] count, int W) {
    int[] dp = new int[W + 1];

    for (int i = 0; i < items.length; i++) {
        int p = items[i].weight(), q = items[i].value(), c = count[i];
        if (p <= 0 || c <= 0) continue;

        int[] next = new int[W + 1];
        for (int r = 0; r < p && r <= W; r++) {
            // dq holds s-values; X(s) = dp[r + s*p] - s*q, strictly decreasing in the deque
            int[] dqS = new int[(W / p) + 2];
            int[] dqX = new int[(W / p) + 2];
            int head = 0, tail = 0;

            int maxT = (W - r) / p;
            for (int t = 0; t <= maxT; t++) {
                int x = dp[r + t * p] - t * q;      // X(t)

                // Dominance pop: drop any older s whose X is <= the new (larger s, >= value).
                while (head < tail && dqX[tail - 1] <= x) tail--;
                dqS[tail] = t; dqX[tail] = x; tail++;

                // Expire s < t - c
                while (head < tail && dqS[head] < t - c) head++;

                if (head < tail) next[r + t * p] = dqX[head] + t * q;
            }
        }
        dp = next;
    }
    return dp[W];
}
```

### The four lines that matter

1. **`x = dp[r + t*p] - t*q`** — this is the reparametrised value. If you forget the `- t*q`, the answer is the *unbounded* result.
2. **`<= x` in the dominance pop** — strictly decreasing values in the deque. Using `<` keeps ties (still correct, just more memory).
3. **`< t - c` expiry** — the window is `[t-c, t]`, so `s = t-c` is **included**. Using `<= t-c` wrongly drops one copy and gives "at most `c-1`".
4. **Push before expire** — pushing first then expiring handles `c = 0` correctly (`dqS[head] < t` removes everything but the newest... actually for `c = 0` the window is `[t, t]` so the newest is the only valid one, which the expiry guarantees). Swapping the two lines breaks `c = 0`.

**Memory:** `next = new int[W+1]` per item ⇒ `n` allocations. Reuse two buffers and swap them — `n × W` allocations of `W` ints is real GC pressure.

**`dqS`/`dqX` allocation:** `new int[(W/p)+2]` inside the residue loop means `p` allocations per item. Hoist them outside the residue loop and reuse (their max size is `W/p + 2` regardless of `r`).

---

## 5. Fractional knapsack

```java
public record FractionalResult(double value, int[] wholeItems, int partialIndex, double partialFraction) {}

public static FractionalResult solveFractional(Item[] items, int W) {
    Integer[] order = new Integer[items.length];
    for (int i = 0; i < order.length; i++) order[i] = i;
    // Sort by value/weight DESCENDING. Use a cross-multiplier comparator -- do NOT
    // divide: vi/wi loses precision and can mis-order items with equal ratios.
    Arrays.sort(order, (x, y) -> {
        long l = (long) items[x].value() * items[y].weight();
        long r = (long) items[y].value() * items[x].weight();
        return Long.compare(r, l);
    });

    int remaining = W;
    double value = 0;
    List<Integer> whole = new ArrayList<>();
    int partialIdx = -1;
    double partialFrac = 0;

    for (int idx : order) {
        Item it = items[idx];
        if (remaining <= 0) break;
        if (it.weight() <= remaining) {
            whole.add(idx); value += it.value(); remaining -= it.weight();
        } else {
            partialIdx = idx;
            partialFrac = (double) remaining / it.weight();      // in (0, 1)
            value += it.value() * partialFrac;
            break;
        }
    }
    return new FractionalResult(value, whole.stream().mapToInt(Integer::intValue).toArray(), partialIdx, partialFrac);
}
```

**Pitfall 1 — dividing in the comparator.** `v[i]/(double)w[i]` introduces floating-point rounding; items with genuinely equal ratios can be ordered arbitrarily and, more importantly, nearly-equal ratios can be swapped. **Cross-multiplication with `long` is exact** (`vi·wj` vs `vj·wi`) provided the products do not overflow `long`: for `v, w ≤ 10⁹`, the product is `≤ 10¹⁸` < `2⁶³`. ✔

**Pitfall 2 — `partialFrac == 0`.** If `remaining == 0` exactly, the loop breaks before reaching the partial item and `partialIdx = -1`. That is correct, but a caller doing `items[partialIdx]` crashes. Guard.

**Pitfall 3 — the greedy solution is only optimal for the *fractional* problem.** Feeding it to a 0/1 verifier gives a valid but potentially suboptimal 0/1 solution.

---

## 6. Bitset subset sum

```java
public static boolean subsetSum(int[] a, int W) {
    long[] bits = new long[(W >>> 6) + 1];
    bits[0] = 1;                                        // sum 0 is achievable
    for (int x : a) {
        if (x <= 0 || x > W) continue;
        int wordShift = x >>> 6, bitShift = x & 63;
        // DESCENDING: bits[i - wordShift] must still be the PREVIOUS item's value.
        for (int i = bits.length - 1; i >= wordShift; i--) {
            long shifted = bits[i - wordShift] << bitShift;
            // PITFALL: `>>> (64 - bitShift)` with bitShift == 0 is `>>> 0` in Java
            // (shift counts are masked), which would OR in the wrong word. Guard it.
            if (bitShift != 0 && i - wordShift - 1 >= 0)
                shifted |= bits[i - wordShift - 1] >>> (64 - bitShift);
            bits[i] |= shifted;
        }
    }
    return ((bits[W >>> 6] >>> (W & 63)) & 1L) != 0;
}
```

### Pitfalls, all of which produce silently wrong answers

1. **Ascending loop** ⇒ unbounded subset sum. Test: `a = [5,5]`, `W = 10` must be `false` for 0/1 and `true` for unbounded.
2. **`bitShift == 0`** ⇒ the carry term must be omitted. Without the guard, `>>> 64` becomes `>>> 0` and you OR in `bits[i - wordShift - 1]` entirely.
3. **Not handling `x == 0`** — `bits |= bits << 0` is a no-op, which is harmless, but `x == 0` combined with the "0/1" framing is confusing. Skip it.
4. **`x > W`** — the shift is a no-op but you still loop. Skip early.
5. **Checking the wrong bit** — the answer is bit `W & 63` of word `W >>> 6`, not `bits[W]`.

---

## 7. Trading the axes

### By profit

```java
/** dp[p] = minimum weight to achieve value AT LEAST p. Returns the largest feasible p. */
public static int solveByProfit(Item[] items, int W) {
    int P = 0;
    for (Item it : items) P += it.value();
    if (P == 0) return 0;

    final int INF = Integer.MAX_VALUE / 4;
    int[] dp = new int[P + 1];
    Arrays.fill(dp, INF);
    dp[0] = 0;

    for (Item it : items)
        for (int p = P; p >= it.value(); p--)
            if (dp[p - it.value()] != INF)
                dp[p] = Math.min(dp[p], dp[p - it.value()] + it.weight());

    for (int p = P; p >= 0; p--) if (dp[p] <= W) return p;
    return 0;
}
```

**Pitfall:** the loop is **descending in `p`** for the same 0/1 reason. Ascending makes items reusable. And note the DP is now a **minimum cost**, not a maximum value — the roles are swapped but the machinery is identical.

### Meet-in-the-middle

```java
public static long solveMITM(Item[] items, int W) {
    int n = items.length;
    if (n > 44) throw new IllegalArgumentException("MITM needs n <= 44 (memory)");
    int h = n / 2;

    record Sub(long w, long v) {}
    List<Sub> left = new ArrayList<>(1 << h);
    for (long m = 0; m < (1L << h); m++) {
        long w = 0, v = 0;
        for (int b = 0; b < h; b++) if ((m & (1L << b)) != 0) { w += items[b].weight(); v += items[b].value(); }
        left.add(new Sub(w, v));
    }
    left.sort(Comparator.comparingLong(Sub::w));          // sort by weight

    long best = 0;
    for (long m = 0; m < (1L << (n - h)); m++) {
        long w = 0, v = 0;
        for (int b = 0; b < n - h; b++) if ((m & (1L << b)) != 0) { w += items[h + b].weight(); v += items[h + b].value(); }
        if (w > W) continue;
        // largest left entry with weight <= W - w
        int lo = 0, hi = left.size() - 1, pos = -1;
        while (lo <= hi) { int mid = (lo + hi) >>> 1; if (left.get(mid).w <= W - w) { pos = mid; lo = mid + 1; } else hi = mid - 1; }
        if (pos >= 0) best = Math.max(best, v + left.get(pos).v);
    }
    return best;
}
```

**Use `long` for the weights/values inside MITM** — `1 << 22` subsets is already 4 million, and a `List<Sub>` of 4 million records with boxed `long`s is the memory limit, not the algorithm.

**Better than a `List<Sub>`:** two parallel `long[]` arrays (`weights` and `values`), sorted by weight. That removes ~16 bytes/entry of object overhead. For `n = 40`, `2²⁰` entries: `16 MB` for the arrays vs `~40 MB` for the list.

---

## 8. Cross-validation harness

```java
static void fuzz() {
    Random rnd = new Random(555);
    for (int trial = 0; trial < 20_000; trial++) {
        int n = 1 + rnd.nextInt(9);
        Item[] items = new Item[n];
        int[] count = new int[n];
        int W = 1 + rnd.nextInt(40);
        for (int i = 0; i < n; i++) {
            items[i] = new Item(1 + rnd.nextInt(12), 1 + rnd.nextInt(20));
            count[i] = rnd.nextInt(4);                     // 0..3 -- INCLUDES ZERO
        }

        int base = solve01(items, W);
        int unb  = solveUnbounded(items, W);
        int spl  = solveBoundedSplit(items, count, W);
        int dq   = solveBoundedDeque(items, count, W);
        long mitm = solveMITM(items, W);
        int prof = solveByProfit(items, W);

        // 1. Bounded must lie between 0/1 and unbounded.
        assert base <= dq : "bounded < 0/1";
        assert dq  <= unb : "bounded > unbounded";
        // 2. All the exact methods must AGREE.
        assert spl == dq : "binary split != monotone queue";
        assert mitm == base : "MITM != 0/1 DP";
        // 3. By-profit must equal 0/1.
        assert prof == base : "by-profit != 0/1 DP";
        // 4. Fractional must be >= the 0/1 optimum (it is a relaxation).
        FractionalResult fr = solveFractional(items, W);
        assert fr.value() >= base - 1e-9 : "fractional < 0/1 optimum";
    }
}
```

**The chained invariants `base ≤ dq ≤ unb` and `spl == dq` are the highest-value assertions in this lab.** They catch the loop-order bugs (which break the chain), the binary-splitting completeness bugs (which break `spl == dq`), and the monotone-queue off-by-one (which breaks both).

**Include `count[i] == 0`** — it is the case where the monotone-queue expiry window is `[t, t]` and the push/expire order matters.

---

## 9. What to use in production

```java
// Exact, small W: the 0/1 DP. nW <= 10^9.
int v = solve01(items, W);

// Exact, large W, small n (<= 44): meet-in-the-middle.
long v2 = solveMITM(items, W);

// Large everything, "good enough": greedy by ratio, 11/9 guarantee.
FractionalResult v3 = solveFractional(items, W);

// Subset sum / exact change: the bitset. 64x faster than the boolean DP.
boolean ok = subsetSum(a, W);

// Bounded with big counts: the monotone queue.
int v4 = solveBoundedDeque(items, count, W);

// Real portfolio / budget allocation: fractional or LP + branch and bound,
// NOT the DP -- see the multi-dimensional blow-up in THEORY.md.
```

**The engineering judgement:** if `nW ≤ 10⁸` (≈ 0.5 s), write the `Θ(nW)` DP — it is exact, 15 lines, and reconstructable. Above that, decide between greedy-with-a-guarantee and a heuristic; the DP is not an option and pretending otherwise wastes days.