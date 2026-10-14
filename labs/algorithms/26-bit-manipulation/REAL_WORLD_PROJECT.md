# Real-World Project: Permission Flag Audit

## Problem

A service stores user permissions as 16-bit flag fields. Audit tooling must
decode flags, count grants, and find user ids missing from a 0..n export.
Build a flag auditor over a CSV dump.

## Inputs

- `users.csv`: rows `id,flags` with integer id and integer flag word.
- `expected_max.txt`: single integer n; ids should cover 0..n exactly once.
- Flag layout documented in the file header: bit 0 read, 1 write, 2 admin.

## Steps

1. Parse the CSV; reject rows with negative ids or flags above 65535.
2. Decode each flag word into read/write/admin booleans with masks.
3. Count set bits per user with Kernighan's method; record the histogram.
4. XOR-scan the id column to find the single missing id in 0..n.
5. Flag any admin grants (bit 2) into a review list with user id.
6. Emit `audit.txt` with histogram, missing id, and review list.
7. Print the three most common flag words with their counts.
8. Write a two-paragraph note on which grants need human review.

## Acceptance criteria

1. Decode of flag word 7 yields read, write, and admin all true.
2. Histogram counts sum to the number of parsed rows.
3. Missing-id scan returns the planted gap on the reference fixture.
4. Admin review list contains exactly the bit-2 holders.
5. Out-of-range flags exit with a message naming the row.
6. `audit.txt` contains histogram, missing id, and review list.
7. All output uses plain ASCII characters.

## Constraints

- Plain Java only, no external libraries; 16-bit words documented.
- Single pass over rows apart from the final histogram print.
- Missing-id logic must use XOR, not a boolean array.
