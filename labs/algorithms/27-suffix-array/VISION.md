# Vision: Suffix Arrays

## Direction

This lab covers suffix arrays for substring search: doubling construction,
Kasai's linear LCP pass, and binary-searched pattern counting. The practical
skill is building the array on a small string by hand and stating each
phase's cost without reaching for a library.

## What to learn

- Suffix array: sorted starting positions; the sorted-substring index.
- Doubling: pair-rank sorting with k doubling; O(n log n) with radix steps.
- Kasai: text-order scan with carried match length; O(n) LCP.
- Pattern query: contiguous match block via two binary searches.
- LCP use: longest repeated substring is the maximum LCP value.

## Non-coverage

- This lab does not cover suffix trees or suffix automata.
- It does not cover induced sorting (SA-IS) or library-grade builders.
- It does not cover Burrows-Wheeler transforms or FM-indexes.
- It does not cover approximate matching or edit-distance search.
- All strings here are short ASCII teaching examples.

## How to use this lab

Hand-sort the suffixes of "banana" before running Q1, trace Kasai's h value
per position for Q2, then count three patterns of your own with Q3's
bisector. Finish with MINI_PROJECT's repeated-substring finder.

## Pitfalls

- Printing LCP values in text order instead of SA order.
- Searching patterns with one binary bound instead of two.
- Forgetting the separator when concatenating multiple strings.

## Done when

- You can write the SA of a 6-character string without notes.
- You can explain why h carries over between Kasai iterations.
- You can state the O(m log n) query bound and its assumption.
- You can read longest repeats directly off an LCP array.
