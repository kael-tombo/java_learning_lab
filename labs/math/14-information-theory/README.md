# Information Theory — Lab 14 of the Legacy Math Track

The lab measures surprise in exact fractions — a dyadic distribution
whose entropy is exactly 7/4 bits — then compresses it with Huffman,
approximates the same event's codes on a non-dyadic alphabet, prices
disagreement between two distributions with KL (exact 1/2 versus
5/8 in opposite directions), and reads a genuine 0.311278-bit
correlation out of a 2x2 table. All numbers came from captured runs.

## The six files at a glance

- MATH_FOUNDATION.md: entropy of (1/2, 1/4, 1/8, 1/8) computed
  exactly (contributions 1/2, 1/2, 3/8, 3/8 → 7/4), the uniform and
  two-symbol comparison bounds (log2 4 = 2 caps it; (2/3, 1/3)
  yields the irrational log2 3 − 2/3 ≈ 0.9183), Huffman on both
  alphabets with exact code lengths [1, 2, 3, 3] and [2, 2, 2, 3, 3],
  average lengths 7/4 (gap 0) and 11/5 (gap 0.0781) with Kraft sum 1
  both times, the exact KL bookkeeping 1/2 ≠ 5/8 for a swapped dyadic
  pair, positivity and asymmetry statements, and a mutual information
  verified two ways (H(X)+H(Y)−H(X,Y) and the direct double sum) with
  H(Y|X) = 1/2 exactly.
- CODE_DEEP_DIVE.md: three runnable stdlib-only programs — the
  dyadic entropy with float cross-check, the Huffman builder with
  Kraft audit on two alphabets, and the KL/MI program pairing exact
  dyadic KL against float KL and double-checked MI.
- EXERCISES.md: five worked problems — contribution bookkeeping,
  H(3/4, 1/4) = 0.811278 bits, a fresh Huffman run on
  (3/8, 3/8, 1/4) with average 13/8 and gap 0.0637, the exact-strength
  KL pair, and an XOR independence exhibit where MI(X, Y) and
  MI(X, Z) both compute to exactly 0.
- FLASHCARDS.md: cards carrying run numbers — the 7/4 entropy, both
  code-length tables, gap 0.0781, the 1/2-vs-5/8 KL pair, MI's
  0.311278 and its chain rule decomposition H(Y) − H(Y|X).
- COMMON_MISTAKES.md: log-base confusion (bits vs nats, and why
  mixing them poisons Kraft's sum), double-counting joint mass in
  marginalization, treating Huffman's gap as "suboptimal" rather
  than as the dyadic-existence gap, assuming KL symmetry from
  coincidentally-close floats, and reading MI=0 as "no relationship"
  when it means no linear-in-count dependence.

## Prerequisites and where they are taught

Logarithms from 01-arithmetic, probability mass functions from
03-probability/08-probability, disjoint-event counting from
06-combinatorics. The exact-fraction summation discipline recurs in
15-numerical-methods as a measurement-accuracy exhibit; the Huffman heap walk
pairs with 07-graph-theory's tree views.

## One possible route

THEORY.md, MATH_FOUNDATION.md with pencil, deep-dive programs at
PYTHONHASHSEED=0, EXERCISES.md, then the flashcard/mistake pair while
working MINI_PROJECT.
