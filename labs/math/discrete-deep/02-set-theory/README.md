# Set Theory — Lab 02 of Discrete Deep

Exhaustive algebra checks, an explicit power-set bijection with both
directions verified, exact pairing values, and a diagonal-refutation
machine that beats any list you hand it. All numbers from captured runs.

## What each file contains

- THEORY.md: sets built from ∅ by von Neumann's 0={∅} successors; the
  operation algebra with De Morgan machine-checked over 64 subset
  pairs; inclusion–exclusion with a three-set census (6 = 4+5+3−1−2−2+1);
  |P(S)| = 2ⁿ and the bit-string bijection; countability via the Cantor
  pairing; Cantor diagonalization stated per-row; Schröder–Bernstein
  applied to Q.
- MATH_FOUNDATION.md: the same numbers with derivations — 64 pair
  checks, the six-term formula at 6, sizes 1 through 1024, the decoded
  integers forming exactly {0,...,7}, π-values 0..9, the 9-rational
  filtered list, and the finite anti-diagonal 11111111.
- CODE_DEEP_DIVE.md: two executed Python programs — set algebra by
  exhaustion; the power-set bijection, anti-diagonal refutation
  machine, Cantor pairing, and the rational filter.
- EXERCISES.md: five worked problems (exhaustive De Morgan, the
  3,4-overlap census, power-set size and bijection, the 12-cell
  rational grid losing 3 cells to reduction, Cantor twice).
- FLASHCARDS.md: twelve cards carrying only run-verified figures.

## Prerequisites within the track

Lab 01's counting of assignments gives the membership-vector view of
power sets (2ⁿ = number of bit vectors) and its induction pattern
underlies the finite bijection checks. Cartesian products here feed
Lab 03's counting arguments; the diagonal method here is the template
for proof-by-construction lists in Lab 05's generating functions.

## Do this

Run program 2 last and read the machine's verdict column by column:
each row loses at exactly one position, yours. Then re-derive π's
first ten values by hand against the printout — the diagonal walk is
the mental model for every later "inject then Schröder–Bernstein"
argument on this track.
