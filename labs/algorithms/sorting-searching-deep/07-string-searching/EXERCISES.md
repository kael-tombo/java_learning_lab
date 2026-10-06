# Exercises — String Searching

Implement in Java, trace by hand, then attack the edge cases. Java 21, package `com.alglab.strsearch`. Solutions → `SOLUTION/`, tests → `TESTS/`.

---

## Exercise 1 — Build the KMP failure function

Compute `lps` for each pattern by hand, then verify with code.

| pattern | `lps` |
|---------|-------|
| `ABABCABAB` | `0 0 1 2 0 1 2 3 4` |
| `AAAA` | `0 1 2 3` |
| `ABCDABCA` | `0 0 0 0 1 2 3 4` |
| `AABAA` | `0 1 0 1 2` |
| `ABCAB` | `0 0 0 1 2` |
| `A` | `0` |
| `` (empty) | `` (length 0) |

**Trace `ABABCABAB`:**

| `i` | `p[i]` | `len` | action | `lps[i]` |
|-----|--------|-------|--------|----------|
| 1 | B | 0 | `p[1]≠p[0]` → `lps[1]=0` | 0 |
| 2 | A | 0 | `p[2]==p[0]` → `len=1` | 1 |
| 3 | B | 1 | `p[3]==p[1]` → `len=2` | 2 |
| 4 | C | 2 | `p[4]≠p[2]`, `len>0` → `len=lps[1]=0` | |
| | | | `p[4]≠p[0]` → `lps[4]=0` | 0 |
| 5 | A | 0 | `p[5]==p[0]` → `len=1` | 1 |
| 6 | B | 1 | `p[6]==p[1]` → `len=2` | 2 |
| 7 | A | 2 | `p[7]==p[2]` → `len=3` | 3 |
| 8 | B | 3 | `p[8]==p[3]` → `len=4` | 4 |

**Then:** explain why `lps[n-1]` for `"AAAA"` is 3 — the pattern overlaps itself by 3, so after a match you can resume matching at offset 1.

---

## Exercise 2 — The overlap bug hunt

Implement KMP three ways and find the smallest input where they disagree:

| Variant | After a match |
|---------|----------------|
| A (correct) | `j = lps[j-1]` |
| B (bug) | `j = 0` |
| C (bug) | `j = lps[j-2]` |

Find the smallest witness for B: `p = "aa"`, `t = "aaaa"` — B returns `[0, 2]`, correct is `[0, 1, 2]`.

Find the smallest witness for C: search exhaustively over all `(t, p)` with `|t| ≤ 6`, `|p| ≤ 4`, alphabet `{a, b}`.

Then answer: **why does this bug survive casual testing?** (Because a periodic pattern with overlaps is required to trigger it; most real patterns — words, IDs, tokens — have no self-overlap, so `[0]` and `[0,1,2]` look the same when there is at most one match.)

---

## Exercise 3 — Character-comparison accounting

Instrument all of KMP, Z, and naive with a comparison counter and record comparisons on these inputs (`n = 10⁶`, `m = 10³`):

| `#` | `p` | `t` | naive | KMP | Z | BMH |
|-----|-----|-----|-------|-----|---|-----|
| 1 | `a`×1000 | `a`×10⁶ | | | | |
| 2 | `a`×999 + `b` | `a`×10⁶ | | | | |
| 3 | `b` + `a`×999 | `a`×10⁶ | | | | |
| 4 | random over 2 symbols | random over 2 symbols | | | | |
| 5 | random over 26 symbols | random over 26 symbols | | | | |
| 6 | random over 256 symbols | random over 256 symbols | | | | |
| 7 | `a`×1000 | `b`×10⁶ | | | | |
| 8 | random | `a`×10⁶ | | | | |

**Predictions before running:** naive is `Θ(nm)` on #1, #2, #3; KMP is `≤ 2n` on *every* row; BMH is ~`n` on rows 1–3 (bad) and well below `n` on rows 5–6 (good); row 7 is best for BMH (immediate skip by `m`).

**Then:** explain why KMP is `Θ(n)` on row 7 (it is!) while naive is also `Θ(n)` there (early failure) — i.e. row 7 does not distinguish the algorithms. **Which rows discriminate, and why?**

---

## Exercise 4 — Boyer–Moore skip tables by hand

Build `last[]` for `p = "ABCAB"` (alphabet A–D):

| char | `last[char]` |
|------|--------------|
| A | 3 |
| B | 4 |
| C | 2 |
| D | −1 |

Now trace Horspool searching `t = "ABABCABABCAB"` for `p = "ABCAB"`:

| `i` | window | compare from right | mismatch at | `t[i+m-1]` | `last` | shift | new `i` |
|-----|--------|-------------------|-------------|-------------|--------|-------|---------|
| 0 | `ABCAB` | match | — | — | — | — | 0 (report), `i += 5` |
| 5 | `CABAB` | B vs C mismatch at 4 | 4 | B | 4 | `5-1-4 = 0` | 5 |

**PITFALL demonstrated:** the shift is `0`, so the window at `i=5` is re-examined. That is correct (and safe, because `j == m-1` mismatches can never happen — here `j` is 4 = `m-1`... **trace again carefully and identify whether this example hits the `j == m-1` case that Horspool cannot shift past.** If it does, that is the well-known Horspool weakness and your answer is "it degenerates to naive here; use BMH.")

**Repeat with BMH** and show BMH's `else i += m` branch handles it.

---

## Exercise 5 — The "wrong character" bug

Write Horspool twice: once with `i += m - 1 - last[t[i+m-1]]` and once with `i += m - 1 - last[t[i+j]]`. Fuzz both against `String.indexOf` over 200 000 random `(t, p)` pairs.

**Report:** at what trial does the buggy version first produce a wrong answer, and what is the smallest witness? (Expect a small one: `p = "abc"`, `t = "abc"`. The buggy shift computes `last['c'] = 2` so `i += 3-1-2 = 0` → infinite loop, or with `p="aba"`, `t="ababa"` it skips past position 2.)

Then fix it and **explain the invariant** that makes the correct version safe: `j < 0` on exit ⟹ `p[m-1] ≠ t[i+m-1]` ⟹ `last[t[i+m-1]] ≤ m-2` ⟹ shift `≥ 1`.

---

## Exercise 6 — Aho–Corasick construction

Patterns: `{"he", "she", "his", "hers"}`. Text: `"ushers"`.

**Draw the trie**, compute the **failure links** by hand (BFS order), and compute the **output links**.

**Trace the scan:**

| `i` | char | state | fail chain walked | reports |
|-----|------|-------|-------------------|---------|
| 0 | u | 0 | 0 | — |
| 1 | s | `s` | root | — |
| 2 | h | `sh` | root | — |
| 3 | e | `she` (pattern!) | `he` (also a pattern) | `he`@2, `she`@1 |
| 4 | r | `her` | `er`→root | — |
| 5 | s | `hers` (pattern!) | `rs`→root | `hers`@1 |

Answer: **why is the output link from `she` necessary?** (Because `he` is also a pattern; without the output link you would miss it at `i=3` unless you walked the `fail` chain.)

Then implement and confirm. Finally, **add pattern `"his"`** and verify it is reported at `i=6` if you extend the text to `"ushers his"`.

---

## Exercise 7 — The output-explosion adversarial case

Patterns: `{"a", "aa", "aaa", "aaaa", "aaaaa"}`, text: `"a"×100`.

- Expected matches: `1 + 2 + … + 100 = 5050`.
- Implement reporting **with** output links and **without** (walk the `fail` chain from the state, collecting pattern-end nodes).
- Instrument and compare `n·k`-style costs.

**Prediction:** with output links the total is `Θ(n + M) = Θ(100 + 5050)`. Without them you walk the full `fail` chain at every position (`Θ(k)` each) but you *stop* at the first pattern node, so it is also `Θ(M)` — **so when does the chain-walk actually hurt?**

Answer the harder question: implement a version that, for each position, counts the number of patterns ending there. With output links: `O(1)` per position. Without: `O(k)` per position. Now measure with `k = 200` and text `"a"×10⁴`: with output links `~10⁴` operations; without, `~2·10⁶`. **That is the real cost difference.**

---

## Exercise 8 — Memory: dense vs sparse Aho–Corasick

Build an automaton for `S = 10⁵` total pattern bytes:
- Dense `int[256]` per node → measure heap usage.
- Sparse: `int[][]` transitions stored as parallel sorted arrays (`int[] chars`, `int[] targets`) with binary search.
- Sparse: `HashMap<Character,Integer>` per node (or one `HashMap<Long,Integer>` keyed by `node*256 + c`).

Report build time, scan time, and peak memory for each. Then answer:
- At what `S` does dense stop fitting in a 1 GB heap?
- Which representation wins for **scan** speed? (Dense: one array index, no hashing. Always wins by 2–5×.)
- Which wins for **build**? (Sparse — dense is `Θ(S·256)` regardless of how few transitions each node has.)

---

## Exercise 9 — Rabin–Karp in practice

Implement RK with modulus `2⁶¹ − 1` and a random base, and separately with `Long.hashCode`-style power-of-two masking (mod `2⁶²`).

- Measure: (a) correct rolling hash cost, (b) time with an **intentionally bad** base (e.g. 31) where collisions are frequent, (c) time with no verification.
- Force collisions: use `p = "abababab..."` and a base where `a` and `b` have the same polynomial value. Find such a base. Then show the false-positive path and that **verification saves correctness but destroys the speed**.

**Then write the security argument:** why is a fixed base dangerous? (Length-extension / chosen-plaintext collision attacks. Cite the classic `Java String.hashCode` attack: two different strings, `"Aa"` and `"BB"`, share `hashCode == 2112`.)

---

## Exercise 10 — Debugging drills

1. Naive search with `break` instead of `continue outer` — what is the complexity, and does it still find all matches?
2. KMP `lps` with `len = 0` instead of `len = lps[len-1]` in the mismatch branch — is it correct? (`Θ(m²)` build, still correct.)
3. Z-algorithm with `if (i <= r)` instead of `if (i < r)` — find a failing input.
4. Z-based search with separator `0` on `byte[]` text containing `0x00` — find the false match.
5. BM with `i += Math.min(bad, good)` — find a skipped match.
6. Aho–Corasick without DFA completion, with a scan that uses `nodes[u].gotoTable[c]` directly instead of following `fail` — what happens for a character with no outgoing edge from `u`? (`−1` index → `ArrayIndexOutOfBoundsException`, or a wrong node if you guard.)
7. Aho–Corasick where the scan forgets `u = 0` at the start of `search` — reproduce a match spanning two "documents".

---

## Exercise 11 — Fibonacci-word benchmark

Generate Fibonacci words: `F₀ = "b"`, `F₁ = "a"`, `F_{k+1} = F_k · F_{k-1}`. These are the worst case for essentially every linear-time string algorithm.

- `F₂₅` is 750 25 bytes.
- Benchmark KMP, Z, BMH, and `String.indexOf` searching for `F₂₀` inside `F₂₅`.
- Report comparisons for each.

**Explain:** why are Fibonacci words adversarial? (Every proper prefix is highly self-similar, so the Z-box always extends by 1 and the good-suffix/KMP fallback chains are maximally long. The `Θ(n)` bound still holds but the constant is the worst achievable.)

---

## Exercise 12 — Deliverable

`BENCHMARK/SearchRace.java`: for text lengths `{10³, 10⁴, 10⁵, 10⁶, 10⁷}` and pattern lengths `{3, 10, 100, 1000}` over alphabets `{2, 26, 256}`, run naive / KMP / Z / BMH / BM-full / RK / `String.indexOf`; print a markdown table of ns/op and comparisons; bold the winner.

Then answer in writing:
1. **Why does `String.indexOf` win so decisively, given that all algorithms are `Θ(n)`?**
2. **Which algorithm wins where?** (Expected: `indexOf` for `m ≤ 100`; BM-full for large `m` and `σ ≥ 95`; KMP never wins against `indexOf` in Java but wins in other languages because `String.indexOf` is not available as a raw primitive.)
3. **What does this tell you about the value of implementing an algorithm vs using a library?** (Be honest: the algorithm work is what makes the library possible, and the JIT's intrinsic is the last 10×.)