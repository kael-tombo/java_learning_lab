# Real-World Project: Line Diff for Config Files
> Build a small diff tool: LCS over lines, then unified hunks a reviewer can read.

## Problem
Two revisions of a config file differ in a few lines; reviewers need the exact added, removed, and kept lines.
Naive line-by-line comparison misaligns everything after one insertion; LCS alignment fixes that.
## Inputs
- old.txt and new.txt, UTF-8 text, one entry per line, up to 2000 lines each.
- Optional flag to ignore leading/trailing whitespace when comparing lines.
- Golden directory with 4 fixture pairs and their expected hunk outputs.
## Steps
1. Read both files into line lists A (m lines) and B (n lines), normalizing line endings.
2. Fill the LCS length table dp over prefixes of A and B, row by row.
3. Backtrack from dp[m][n] with parent decisions to recover one LCS.
4. Walk both files with the LCS to emit added, removed, and context lines.
5. Group changes into hunks with 3 context lines, in unified-diff style.
6. Print LCS length, hunk count, and per-hunk headers to stdout.
## Acceptance criteria
- Identical 200-line files produce an empty diff and report LCS length 200.
- Empty old file vs 100-line new file reports exactly 100 additions.
- Fixture pair with 10 changed lines yields byte-identical expected hunks.
- 1000-by-1000 line inputs finish in under 5 seconds on the lab machine.
- Whitespace flag flips the known whitespace-only fixture from changed to unchanged.
## Failure modes
- Inputs over the line cap are rejected with a clear error instead of exhausting memory.
- Mixed CRLF/LF endings are normalized before comparison so endings never fake a change.
- Non-UTF-8 bytes fail fast with the offending filename, not a stack trace.
## Extensions
- Word-level diff inside changed lines using the same LCS core.
- Length-only mode with a rolling row for inputs where hunks are not needed.
## How to demo
- Run the tool on the sample pair and paste the hunk output next to the expected file.
- Time the 1000-by-1000 case and record table-fill vs backtrack milliseconds.
