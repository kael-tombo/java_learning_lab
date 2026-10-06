# Quiz — String Searching

15 questions. Each key gives the reason.

---

## Q1
KMP's text pointer never moves backwards. Prove the algorithm is `Θ(n + m)` using two counters.

<details><summary>Answer</summary>

Let `U` = total increases of `j`, `D` = total decreases. Since `j` starts at 0, never goes negative, and ends at `j_f ≤ m`:

```
U − D = j_f   ⟹   U = D + j_f ≤ D + m
```

`U ≤ n` (at most one increase per text character). Each `while` iteration decreases `j` by ≥ 1, so `iterations ≤ D = U − j_f ≤ n`.

**Total: `≤ n` increments + `≤ n` decrements + `Θ(m)` for the lps build = `Θ(n + m)`.**

The pointer monotonicity is the *result* of the fallback chain never needing to re-examine text — which is the whole design.
</details>

## Q2
Why must the post-match reset be `j = lps[j-1]` and not `j = 0`?

<details><summary>Answer</summary>

After a match, the last `lps[m-1]` characters of the pattern are **also a prefix of the pattern**, and they coincide with the text just consumed. So matching can resume at offset `m − lps[m-1]` without re-reading text.

`j = 0` discards that and forces a full re-scan from `i+1`, which both loses overlaps (`"aa"` in `"aaaa"` returns `[0,2]` instead of `[0,1,2]`) and reintroduces backtracking.

**Why it survives testing:** most real patterns have no self-overlap, so a test with at most one match cannot distinguish the two.
</details>

## Q3
Give the tightest known worst-case bound on KMP's character comparisons, and the adversarial input for naive.

<details><summary>Answer</summary>

**KMP: at most `2n + m − 2` character comparisons** for `n ≥ m`.

**Naive's worst case:** `p = "a"^m + "b"` against `t = "a"^n`. Every one of the `n − m + 1` windows matches `m` a's then fails on `b` ⇒ `Θ(nm)`.

Ratio for `n = 10⁶`, `m = 10³`: `10⁹` vs `2·10⁶` — **500×**.
</details>

## Q4
In Boyer–Moore–Horspool, why must the shift use `t[i+m-1]` and not the mismatching character `t[i+j]`?

<details><summary>Answer</summary>

The Horspool skip rule is justified by the character that was **compared last** (position `i+m−1`): the next alignment that could match must bring some `P` character onto that text position. Shifting by `m − 1 − last[t[i+m−1]]` aligns `P`'s last occurrence of that character with it.

Using `t[i+j]` assumes the mismatch occurred at the pattern's last position, which is false — that is a *bad-character* rule, not Horspool, and it is **incorrect** because the justification (only `P[m−1]` aligns with `T[i+m−1]`) no longer holds.

It can also produce a **zero shift → infinite loop**, since `t[i+j]` may equal `p[m−1]`... no, that can't reach `j < 0`. The real symptom is **skipped matches** on short patterns.
</details>

## Q5
Why is Horspool guaranteed not to loop forever?

<details><summary>Answer</summary>

The inner loop exits with `j < 0` only after successfully comparing `p[m−1] == t[i+m−1]`... **no** — `j = m−1` is the *first* comparison, so `j < 0` means `p[m−1] != t[i+m−1]`.

Therefore `last[t[i+m−1]] ≤ m−2`, and the shift `m − 1 − last[c] ≥ 1`.

`i` strictly increases ⇒ termination. **This invariant is exactly what breaks if you substitute `t[i+j]`**, which is why that "simplification" produces infinite loops as well as wrong answers.
</details>

## Q6
Boyer–Moore is called sublinear. When is that legitimate, and when is it false?

<details><summary>Answer</summary>

**Legitimate** for large `m` and large alphabet: expected comparisons `≈ n·m/σ`, which for `m = 1000`, `σ = 95` is `≈ 10.5n`... so it is sublinear only if `m < σ` *and* you amortise over a skip. Precisely: `E[skip] = min(m, m/σ + 1)`, so `E[comparisons] = n/E[skip] ≈ nσ/m`. For `m = 10⁴`, `σ = 65 536`: `6.5n`... still not sublinear.

**Sublinear requires `σ > m`**, i.e. a huge alphabet (full Unicode code points) *and* `m` large. Measured in practice, BM beats KMP mainly on a **constant factor**, not on order — `Θ(n)` either way.

**False** for `m = 1, 2`, for DNA/binary text (`σ = 2`), and worst case `Θ(nm)` for `p = "b" + "a"^(m-1)` against a run of a's.
</details>

## Q7
Why does BMH (`Knuth–Morris–Pratt–Horspool`) fix the `Θ(nm)` worst case, and what is the rule?

<details><summary>Answer</summary>

The problematic case is a mismatch at position `m−1` (the last character), where Horspool's shift degenerates to `m − 1 − last[c]`, which can be small.

**BMH's rule:** if the mismatch is at position `j = m−1`, shift by the **full pattern length** `m`.

Rationale: the mismatch is at the pattern's rightmost character, so no alignment in the next `m−1` positions can succeed — the entire window is dead. This single clause removes the `Θ(nm)` case while keeping the average-case skip.
</details>

## Q8
Rabin–Karp is usually described as `O(n + m)`. What is actually true?

<details><summary>Answer</summary>

`Θ(n + m)` **hash operations**, where each is `Θ(w)` machine words. Plus:

- **Collisions**: each triggers a `Θ(m)` verification. With a random prime modulus `p`, per-window false-positive probability `≈ 1/p`, so expected extra cost `Θ(n·m/p)`.
- Requiring `p ≫ nm` for a negligible error rate means `Θ(log(nm))`-bit arithmetic, which is **not** a single machine-word multiply.
- **Without** verification it is **Monte Carlo** (can report a false match, never a false miss).

So the honest statement is: *expected* `Θ(n + m)` word-RAM operations for a negligible error probability, and in practice **slower than KMP and BMH**.
</details>

## Q9
State the Z-algorithm's linear-time argument.

<details><summary>Answer</summary>

`[L, R]` is the box with maximum `R` found so far, with `T[L..R] = T[0..R−L]`.

- If `i < R`, `Z[i] ≥ min(R−i, Z[i−L])` is obtained in `O(1)` by copying.
- The inner `while` only does real work past `R`, and each such step **increases `R`**.
- `R` is monotone from 0 to `n`, so total inner work `≤ n`, plus `n−1` outer iterations.

**`Θ(n)` total.** The copy-from-the-box is what makes it linear rather than `Θ(n²)`.
</details>

## Q10
Show that the Z-algorithm on `P + sep + T` implements KMP.

<details><summary>Answer</summary>

Let `S = P + sep + T` with `sep` a character not in `P` or `T`, `|P| = m`. Then `Z[0..m−1]` describes `P`'s self-overlap and, for `i ≥ m+1`, `Z[i]` = length of the common prefix of `T` and `T[i−(m+1)..]`.

`P` occurs at text position `j` ⟺ `Z[m+1+j] ≥ m`.

Same power, more memory (`Θ(n+m)` vs `Θ(m)`) and a slightly worse constant. **But** `Z` also gives every `LCP(T, T[i..])` for free, which is what makes it the tool for suffix-array/LCE work.
</details>

## Q11
Aho–Corasick: state the total complexity in terms of `S = Σ|Pᵢ|`, `σ`, `n`, `M` (match count).

<details><summary>Answer</summary>

| Representation | Build | Scan | Total |
|----------------|-------|------|-------|
| Dense `goto[node][σ]` | `Θ(S·σ)` | `Θ(n + M)` | **`Θ(S·σ + n + M)`** |
| Sparse map | `Θ(S)` | `Θ(n + M)` amortised | **`Θ(S + n + M)`** |
| Dense + DFA completion | `Θ(S·σ)` | `Θ(n + M)` with an O(1) transition | `Θ(S·σ + n + M)` |

Independent of `k` except through `S`. **This is the whole reason Aho–Corasick beats running KMP `k` times (`Θ(k·n)`).**
</details>

## Q12
Why are output links necessary, and what breaks without them?

<details><summary>Answer</summary>

Patterns `{"he", "she"}` and text `"she"`: at the state `she`, the match `she` ends, and so does `he` (a suffix). Without an output link you must walk the `fail` chain to discover `he`.

With **k** patterns all nested (`{"a","aa",...,"a"^k}`) in a run of a's, the chain walk is `Θ(k)` per position ⇒ **`Θ(nk)`** or worse if you collect all matches naively.

With output links, navigation between consecutive reports is `O(1)` amortised, so reporting is **`Θ(n + M)`** — optimal, since `M` is the output size.
</details>

## Q13

Your dense Aho–Corasick automaton has 10⁶ pattern bytes. How much heap does it need and what do you do?

<details><summary>Answer</summary>

`int[256]` per node = 1 KB/node, and nodes ≈ `S` = 10⁶ ⇒ **~1 GB**. Plus the object headers and `int[]` overhead ⇒ over 1 GB.

**Options:**
1. **Sparse transitions** (`int[][]` sorted pairs, or a single `HashMap<Long,Integer>` keyed by `node*256 + c`) → `Θ(S)` memory, slower scan.
2. **Intern identical goto rows** — most nodes near the leaves have identical rows; `HashMap<List<Integer>, Integer>` row interning typically cuts memory 3–5×.
3. **Bloom-filter prefilter** on the pattern set: drop 90%+ of patterns before automaton construction.
4. **Sharding** across workers.
5. Use a library engine (Hyperscan, RE2) that compiles to a bounded-memory DFA.

Never ship a 1 GB automaton for a 1 GB-heap service.
</details>

## Q14
Why does `String.indexOf` beat your hand-written KMP by 10–50× in Java, if both are `Θ(n)`?

<details><summary>Answer</summary>

1. **It is BMH, not KMP.** Fewer comparisons and better skipping — measured ~1.5–3× on random data.
2. **It is intrinsified.** HotSpot compiles `StringLatin1.indexOf` to machine code via `@IntrinsicCandidate`, so the inner loop has no bounds checks, no `charAt` widening, and no array-length reload.
3. **It operates on the compact Latin-1 `byte[]`** internally, so `char`↔`byte` widening is eliminated.
4. **Tighter loop structure** with the skip hoisted and the mismatch path predicted well.

**Lesson:** in Java, the library beats hand-written code by ~10× on primitive-array loops. Implement algorithms to understand them, then use the library.
</details>

## Q15
Fibonacci words are the worst case for every linear-time string algorithm. Why, and does the `Θ(n)` bound break?

<details><summary>Answer</summary>

`F_{k+1} = F_k · F_{k-1}` means every proper prefix is highly self-similar: `F_k` contains `F_{k-1}` as a prefix and suffix, so borders are long and nested.

Consequences:
- **KMP:** the fallback chain is maximally long at every mismatch.
- **Z:** the box always extends by exactly 1, so you get no useful copying.
- **BM good-suffix:** `γ` values are all small, so shifts are minimal.

**The bound does NOT break** — it is still `Θ(n)`. What degrades is the **constant factor**, which is exactly what benchmark numbers report. Any honest benchmark suite must include Fibonacci words or it will report optimistic numbers.
</details>