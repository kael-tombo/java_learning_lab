# Real-World Project: Log Template Miner

## Problem

A service writes thousands of near-duplicate log lines. Operators want the
most repeated substrings to turn into alert templates. Build a miner that
finds top repeated substrings via suffix array plus LCP.

## Inputs

- `logs.txt`: one log line per line, ASCII, at most 200 lines.
- Minimum substring length k passed as a program argument.
- Concatenation uses a separator character absent from the input.

## Steps

1. Read all lines; pick a separator not present in any line.
2. Join lines with the separator into one text; record line boundaries.
3. Build the suffix array with the doubling method from this lab.
4. Compute the LCP array with Kasai's method.
5. Discard LCP entries below k or spanning a separator boundary.
6. Rank surviving entries by (length, occurrence count) descending.
7. Emit `templates.txt` with the top 10 substrings and their counts.
8. Write a two-paragraph note mapping the top 3 to alert rules.

## Acceptance criteria

1. Reference fixture reports "ana" with count 2 for input "banana", k=2.
2. No reported template contains the separator character.
3. Counts verified by brute-force substring search on the fixture.
4. Top-10 list sorted by length then count, both descending.
5. Missing input file exits with a message, not a stack trace.
6. `templates.txt` contains substring, length, and count per row.
7. All output uses plain ASCII characters.

## Constraints

- Plain Java only, no external libraries; deterministic single run.
- Joined text capped at 100k characters with a documented error past it.
- Separator choice printed so results are reproducible.
