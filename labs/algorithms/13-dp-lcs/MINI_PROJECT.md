# Mini Project: LCS Length in an Evening
> Two-string DP from recurrence to reconstruction in one sitting.

## Background
- LCS compares two strings prefix by prefix; the last-character case split gives the recurrence.
- Length needs one rolling row; reconstruction needs the full table plus parent choices.
- You already saw the recurrence in THEORY.md - this project turns it into tested code.
## Goal
Implement length-only LCS and full LCS-with-reconstruction in a single Java file.
Verify both against fixtures and against each other on random fixed-seed pairs.
## Tasks
1. Write lenOnly(a, b) with two rolling rows and return the LCS length.
2. Write full(a, b) with the complete table and parent pointers, returning one LCS string.
3. Check lenOnly equals full-length on fixtures ABCBDAB vs BDCABA (expect length 4).
4. Fuzz 200 random pairs (fixed seed, alphabet ABC, length <= 8) against a brute-force checker.
5. Measure lengths on 500-by-500 random strings and record milliseconds.
6. Write 5 lines in the README: recurrence, fill order, and why rows suffice for length.
## Acceptance criteria
- Fixture pair reports length 4 and a valid length-4 common subsequence.
- Fuzz run shows zero mismatches across all 200 pairs.
- Empty-vs-anything inputs return 0 and empty string without errors.
- 500-by-500 timing is recorded with table-fill milliseconds stated.
- README recurrence matches the code indices exactly.
## Pitfalls
- Filling the table column-major while backtracking assumes row-major parents.
- Using charAt indices directly as dp indices without the +1 shift.
- Forgetting that reconstruction needs the full table, not the rolling rows.
- Testing only on distinct-character strings, which hides tie-handling bugs.
## Stretch
- Length-only mode with a single row and a proof sketch of why it suffices.
- Edit-distance variant (insert/delete/substitute) on the same table shape.
## Timebox
One focused evening session, roughly 2 to 3 hours including the fuzz run.
