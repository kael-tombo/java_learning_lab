# Reflection: Combinatorics

## The Single Question That Fixes Most Errors

Nearly every miscount in this lab collapsed to one ambiguity: *are the objects labeled and ordered, or unlabeled and unordered?* Slots-vs-stars, permutation-vs-combination, nⁿ-vs-n! — all the same fork. Writing the objects down explicitly for a small case (n = 3, k = 2) before committing to a formula takes thirty seconds and eliminates the class of error where the formula is applied to the wrong universe.

## Counting as a Feasibility Check, Not a Homework Exercise

The habit worth keeping: before building anything that generates combinations, compute the count first. 2¹⁰ = 1024 is a loop; 2⁵⁰ is a decision to not loop. I now treat binomial and factorial estimates as the first line of any design note — a step that also communicates intent to reviewers ("this API caps n at 20 because output ≤ 2²⁰ ≈ 10⁶").

## What the Two-Method Verification Taught

Deriving the bitstrings-without-"00" count by state recurrence (5 for n = 3) and by complement (8 − 3 = 5) and seeing them agree is more convincing than either alone. The general principle: when a counting argument has a clean complement or a brute-force oracle for small n, always run both — disagreement localizes the mistake (transition table vs. exclusion list), agreement certifies it.

## Pascal's Triangle Is Infrastructure

Seeing Pascal's rule as *both* the proof and the DP recurrence — the same equation serving mathematics and code — was the clearest moment of the lab. It also explains why a single audited `binomial(n,k)` implementation serves later labs (spanning-tree counts in lab 04, coefficient extraction in lab 05, factorial-based modular arithmetic in lab 06).

## The Gap Between Counting and Listing

n! can be written in one line while listing 10! = 3.6 million rows takes minutes and 20! ≈ 2.4×10¹⁸ is forever. This asymmetry — trivially countable, infeasibly enumerable — is the seed of the whole complexity-theory distinction between decision and search, and of #P-hardness (counting paths vs finding one). Combinatorics is where that gap first becomes visceral rather than theoretical.

## On the History

That the triangle appears in a 1303 Chinese text and in al-Karaji's work around 1000, and only "belongs" to Pascal because he wrote the systematic treatise, is a useful correction to how math history is usually told. Likewise, Pascal's triangle solving a gambling dispute reminds me that these tools were built for concrete, funded questions — a good model for choosing which abstractions deserve to exist.

## Carry-Forward Notes

- Lab 04 will need: counting labeled trees (nⁿ⁻²), degree sequences, and subsets of vertices — the bijection discipline transfers directly.
- Lab 05 will re-derive Catalan numbers and the Fibonacci-like recurrences *from generating functions*, giving closed forms where the state machine only gives tables.
- The overflow discipline (checked arithmetic at the counting boundary, `BigInteger` beyond 20! or C(67,33)) is a software habit, not a math one, and I will keep it in any code that returns a count.
