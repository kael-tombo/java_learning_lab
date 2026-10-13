# Vision: Longest Common Subsequence
> Two-string DP that turns diff, alignment, and edit problems into table-filling.

## Where this leads
- Edit distance and diff utilities: LCS is the skeleton that edit scripts hang on.
- Sequence alignment thinking used in version control, plagiarism detection, and bioinformatics.
- The general 2D-DP-over-prefixes pattern reused by many later dynamic programming labs.
## What mastering it unlocks
- Write the LCS recurrence from the last-character case split without looking it up.
- Reconstruct an actual common subsequence with parent pointers, not just its length.
- Reduce space to one row when only the length is needed, and explain what is lost.
- Recognize when a new problem is really two-prefix DP in disguise.
- Predict the O(m*n) cost from the state count before writing any code.
## What it does not cover
- Approximate matching: this lab is exact matches only, not edit tolerance or k-differences.
- Multiple-sequence alignment, whose cost grows exponentially with the sequence count.
- Subquadratic LCS algorithms, which are research territory, not lab material.
## Core questions you will answer
- Why does comparing the last characters of both prefixes split the problem correctly?
- Why must the table be filled row by row (or column by column) and never diagonally first?
- What breaks in reconstruction if parent pointers are recorded after the max is chosen?
- When is the full table required and when does a rolling row suffice?
## How to judge progress
- Derive dp[i][j] for a 4x4 example by hand with no off-by-one errors.
- Convert the length-only version to the reconstruction version on demand.
- Name the time and space bounds and the input shapes that attain them.
## Common misuse
- Using full O(m*n) memory out of habit when only the length is asked for.
- Treating LCS length as a similarity score without normalizing by the input lengths.
## After this lab
- 14-dp-lis for 1D DP over sequences and the patience-sorting speedup.
- 15-dp-matrix for DP over intervals, the next structural step up.
One-line self-test: State the LCS recurrence and its boundary conditions from memory, correctly.
