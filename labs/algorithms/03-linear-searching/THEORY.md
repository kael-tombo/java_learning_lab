# THEORY — Linear Searching
> Mechanics + invariants + complexity proof sketch for linear search.

## 1. Problem Statement
- Input: array/list `a[0..n-1]`, key `k` (any comparable/equality type).
- Output: smallest `i` with `a[i]==k`, or `-1` if absent.
- No ordering precondition; works on linked lists, streams (single pass).
- Success metric: correctness on empty, singleton, duplicate, null-adjacent inputs.
- Contrast: binary search needs sorted input; hashing needs extra space.

## 2. Algorithm Mechanics
- Step 1: if `n==0` return `-1` immediately (guard clause).
- Step 2: `for i in 0..n-1: if equals(a[i],k) return i`.
- Step 3: fall through → return `-1` (exhaustion = absence).
- Sentinel variant: place `k` at `a[n]` to remove bounds check per iteration.
- Early-exit is the only optimization; order of scan defines "first" semantics.
- Stable choice: returns first occurrence — document it, test duplicates.
- Equality: use `.equals`/comparator, never `==` on objects in Java.
- Null handling: decide policy (`Objects.equals` tolerates nulls).
- Stream variant: `IntStream.range(...).filter(...).findFirst()` same mechanics.

## 3. Invariants (Loop + Termination)
- Invariant I: before iteration `i`, `k ∉ {a[0..i-1]}` (prefix clean).
- Initialization: `i=0`, empty prefix — I holds vacuously.
- Maintenance: if `a[i]!=k`, prefix extends, I preserved; else return (correct).
- Termination: `i==n` with I → `k` absent → `-1` correct.
- Variant function: `n - i` strictly decreases → terminates in ≤ n steps.
- First-occurrence corollary: returned `i` is minimal by I.
- Broken-invariant demo: skipping indices or `<=` off-by-one voids minimality.

## 4. Worked Trace
- `a=[5,2,9,2], k=2`: i=0 (5≠2), i=1 (2==2) → return 1.
- `k=7`: scan 0..3, no hit → -1 after 4 probes.
- Empty `[]`: 0 probes → -1. Singleton hit: 1 probe.
- Duplicate `[2,2,2]`: returns 0 — first, not any.
- Null-tolerant: `[null,"a"], k=null` → 0 with `Objects.equals`.

## 5. Complexity Proof Sketch
- Model: one probe = one equality + index step, cost `c`.
- Worst case: `k` absent or last → `n` probes → `T(n)=c·n = Θ(n)`.
- Best case: `k` at 0 → 1 probe → `Θ(1)`.
- Average (uniform present): `E[probes]=(n+1)/2` → `Θ(n)`; absent adds `n`.
- Lower bound: adversary forces any deterministic scan to probe all `n` slots.
- Space: index + key refs → `Θ(1)` auxiliary.
- Sentinel saves one comparison/iter, not asymptotic class.

## 6. Correctness Argument
- Partial correctness from invariant I (above) + postcondition.
- Total correctness adds variant `n-i` → termination.
- Proof by induction on `i` that prefix is clean.
- Counter-example if broken: returning `i+1` or 1-based index shifts contract.

## 7. When NOT to Use
- Sorted + many queries → binary search (`log n`) or index.
- Membership-heavy → `HashSet` (`O(1)` avg) if memory allows.
- Huge unsorted + repeated queries → sort once (`n log n`) then binary search.
- Use linear when: `n` small (<~50), one-shot, or order unknown.

## 8. Java Notes
- `Objects.equals(a[i], k)` for null safety.
- For primitives, `==` is fine; generics need `equals`.
- Enhanced for loses index — use indexed loop when index matters.

## 9. Common Misconceptions
- "Always O(n)" — best is O(1); report all three cases.
- "Sentinel makes it O(log n)" — no, constant-factor only.
- "Return boolean enough" — index enables downstream use; prefer index.

## 10. Checklist
- [ ] Empty/singleton/duplicate/null traces pass.
- [ ] First-occurrence documented + tested.
- [ ] Best/avg/worst stated with probe counts.
- [ ] `.equals` vs `==` correct.
