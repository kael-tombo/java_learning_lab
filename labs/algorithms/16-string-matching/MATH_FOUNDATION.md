# Math Foundation: KMP Linearity and Hash Arithmetic
> Potential-method linearity for KMP, rolling-hash mod math, naive worst-case count.

## Definitions
- pi[i]: longest proper prefix of p[0..i] that is also a suffix (0 if none).
- Fallback: on mismatch at length j, resume at pi[j-1] without moving the text pointer.
- Rolling hash: window value updated by dropping the lead digit and shifting.
- Comparison count: the measured work unit for naive vs KMP contrasts.

## Counting argument
- Naive worst case: (n-m+1) alignments times m compares = Theta(n*m).
- Attained on text a^n with pattern a^(m-1)b: every alignment fails at the last char.
- KMP: text pointer advances n times; pattern pointer j rises at most n times total.
- Fallbacks only lower j, so total fallback steps are O(n): linear overall.

## Recurrence
- pi construction mirrors search: same fallback loop over the pattern itself.
- Total pi fallbacks O(m) by the same potential argument (j bounded by i).
- Rolling update: th = (B*(th - lead*h) + next) mod q in O(1) per slide.
- h = B^(m-1) mod q precomputed once in O(m).

## Derivation of the bound
- Potential Phi = j (current match length): increments <= n across the run.
- Each fallback strictly decreases Phi, so fallbacks <= increments <= n.
- Total character touches O(n); plus O(m) preprocessing: O(n + m).
- Hash collisions only add verified rescans; correctness never depends on luck.

## Worked mini-proofs
- Proof 1: Phi argument bounding total fallbacks by total increments. (4 lines)
- Proof 2: pi[i] correctness from the prefix-suffix maximality at each step. (4 lines)
- Proof 3: rolling update preserves the window value by Horner expansion. (4 lines)

## Exercises with answers
- 1. pi for ababaca. Answer: [0,0,1,2,3,0,1].
- 2. Naive compares for t = aaaaab, p = aaab. Answer: 12 with 1 hit.
- 3. Why resume at pi[m-1] after a match? Answer: longest prefix still matched.

## Pitfalls
- Claiming O(n) while resetting j to 0 instead of falling back (misses overlaps).
- Negative residues from Java remainder kept unadjusted.
- Equating hash match with string match without verification.

## Checklist
- Reproduce the Phi argument for KMP linearity cold.
- Derive the naive Theta(n*m) family with exact counts.
