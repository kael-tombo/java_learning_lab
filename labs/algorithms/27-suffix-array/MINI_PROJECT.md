# Mini-Project: Longest Repeat Finder

## Goal

Find the longest repeated substring of a fixed string using a suffix array
plus LCP, and verify it against brute force.

## Inputs

- Fixed string "abracadabra"; no file input.
- Brute-force double loop as the cross-check oracle.

## Steps

1. Generate all suffixes with their starting indices.
2. Sort indices by suffix string order to form the SA.
3. Compute adjacent-suffix LCP values with direct comparison.
4. Take the maximum LCP value and its substring as the answer.
5. Brute-force all substring pairs to confirm the maximum length.
6. Print the SA, the LCP array, and the winning substring.
7. Print the occurrence count of the winner by scanning.
8. Assert SA, LCP length, and winner against embedded expectations.

## Acceptance criteria

1. Reported longest repeat is "abra" with length 4.
2. Occurrence count of "abra" reported as 2.
3. Brute-force maximum length equals the LCP maximum (4).
4. SA printed as 11 integers covering 0..10 exactly once.
5. LCP array printed with 11 entries, first entry 0.
6. All asserts pass on the fixed string without input files.
7. All output uses plain ASCII characters.

## Grading note

- Winner abra with length 4 and count 2 required.
- Brute-force maximum must equal the LCP maximum.
- SA must permute 0..10 exactly once, LCP first entry 0.

## Stretch

- Run on "mississippi" and state winner plus length.
- Report every maximal repeat, not just the longest one.
