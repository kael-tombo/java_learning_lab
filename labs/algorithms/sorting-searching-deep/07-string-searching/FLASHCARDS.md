# Flashcards — String Searching

Format: **Q → A**.

---

| # | Question | Answer |
|---|----------|--------|
| 1 | The three string-searching problems | single pattern; **many patterns**; substring/prefix queries |
| 2 | Canonical algorithm for many patterns | **Aho–Corasick**, `Θ(Σ|Pᵢ| + n)` |
| 3 | Naive worst case | `Θ(nm)` — `p = "a"^m + "b"` vs `t = "a"^n` |
| 4 | KMP build cost | `Θ(m)` — amortised `j` accounting in the lps loop |
| 5 | KMP search cost | **`Θ(n + m)` guaranteed**, text pointer never moves back |
| 6 | KMP worst-case comparison bound | `≤ 2n + m − 2` |
| 7 | KMP post-match reset | **`j = lps[j-1]`** — preserves overlaps |
| 8 | KMP fallback chain | `j, lps[j-1], lps[lps[j-1]-1], …` — enumerates **all** borders |
| 9 | KMP invariant | after `t[i]`, `j` = longest prefix of `P` that is a suffix of `t[0..i]` |
| 10 | BM/Horspool compare direction | **right to left** |
| 11 | Horspool shift character | **`t[i+m-1]`** — NOT the mismatching `t[i+j]` |
| 12 | Horspool expected skip | `min(m, m/σ + 1)` |
| 13 | Horspool expected comparisons | `n·m/σ` |
| 14 | BM worst case | `Θ(nm)` — `p = "b" + "a"^(m-1)` vs a run of a's |
| 15 | BMH's fix | if the mismatch is at `m−1`, shift by the full `m` |
| 16 | BM takes which of the two shifts | **`Math.max(badChar, goodSuffix)`** |
| 17 | BM sublinearity requires | `σ > m` and a large alphabet — usually it is a **constant-factor** win |
| 18 | Rabbit–Karp window update | `O(1)` per slide via the rolling hash |
| 19 | RK true cost | `Θ(n+m)` hash ops, each `Θ(w)` words, plus `Θ(n·m/p)` for collisions |
| 20 | RK error type | **Monte Carlo** — false matches possible, false misses impossible |
| 21 | RK modulus requirement | `p ≫ n·m` for a negligible false-positive rate |
| 22 | RK security issue | fixed base ⇒ chosen-plaintext collisions (`"Aa"`/`"BB"` share `hashCode`) |
| 23 | Z-array definition | `Z[i]` = length of `lcp(T, T[i..])` |
| 24 | Z-algorithm complexity | `Θ(n)` — monotone box right-edge `R` |
| 25 | Z on `P + sep + T` | implements KMP (same power, more memory) |
| 26 | Z's separator requirement | must not appear in `P` **or** `T` — a real bug on binary data |
| 27 | Z vs KMP | Z gives all `LCP(T, T[i..])` for free; that is its real value |
| 28 | Z memory | `Θ(n + m)` — `int[] z` is 4 bytes per text character |
| 29 | Aho–Corasick trie size | `Θ(S)` nodes, `S = Σ|Pᵢ|` |
| 30 | Aho–Corasick dense total | **`Θ(S·σ + n + M)`** |
| 31 | Aho–Corasick sparse total | **`Θ(S + n + M)`** |
| 32 | Failure link definition | longest proper suffix of the node's string that is also a trie prefix |
| 33 | Failure-link build order | **BFS** — children are finalised before their `c` children |
| 34 | DFA completion | fill missing `goto` from `fail` — turns the scan into one array index per char |
| 35 | Output link | nearest proper-suffix node that IS a pattern end |
| 36 | Output-link benefit | reporting is `Θ(n + M)` instead of `Θ(n + k²)` on nested patterns |
| 37 | Dense AC memory | `int[256]` = **1 KB per node**; `S = 10⁶` ⇒ 1 GB |
| 38 | Production single-pattern choice | **`String.indexOf` / `String.contains`** — intrinsified BMH |
| 39 | Why `indexOf` wins | BMH + `@IntrinsicCandidate` + compact Latin-1 `byte[]` |
| 40 | `indexOf` advantage over hand-written KMP | ~10–50× on large inputs |
| 41 | Aho–Corasick vs running KMP `k` times | `Θ(S + n)` vs `Θ(k·n)` |
| 42 | Sunday / Quick Search | BM-family with a 20-line skip table; strong on ASCII |
| 43 | Adversarial input for naive/BM | `Fibonacci words F_{k+1} = F_k·F_{k-1}` — worst constant, bound still `Θ(n)` |
| 44 | Adversarial input for AC reporting | nested patterns `{"a","aa",…}` in `"aaa…"` |
| 45 | Manacher's algorithm | `Θ(n)` palindrome detection — the odd/even `Z` variant |
| 46 | KMP lps ≡ Aho–Corasick fail link | AC generalises KMP from one chain to a whole trie |
| 47 | Longest common extension (`LCE`) | mirror string + `Z`, or a suffix array + LCP + RMQ |
| 48 | Number of KMP `j` decreases | `≤ U = D + j_f ≤ n + m` |
| 49 | `String.indexOf` with `m = 1` | BM degenerates; the JDK special-cases it |
| 50 | Cross-validation rule | fuzz with a **1–2 symbol alphabet** or you will never hit border fallbacks |

## Self-test (one line each)

1. KMP's post-match reset and why? → **`j = lps[j−1]`** — it preserves self-overlap so matches aren't skipped
2. Horspool's shift character and the safety invariant? → **`t[i+m−1]`**; `j<0` implies `last[c] ≤ m−2` so the shift is `≥ 1`
3. Aho–Corasick dense vs sparse total? → **`Θ(S·σ + n + M)`** vs **`Θ(S + n + M)`**
4. Why does the Z-algorithm stay linear? → **the box's right edge `R` is monotone; inner work only past `R`**
5. Production choice for one pattern in Java? → **`String.indexOf`** — intrinsified BMH on compact Latin-1 bytes