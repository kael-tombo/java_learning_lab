# Mini Project: Patience Piles by Hand
> Tails array plus reconstruction on paper-sized inputs.

## Background
- The tails array keeps the smallest possible ending for each subsequence length.
- Binary search places each element; parent pointers recover the actual subsequence.
- Small inputs traced by hand expose every misunderstanding early.
## Goal
Implement tails-length and parent-pointer reconstruction with tracing output.
Hand-trace two 8-element sequences and match the program's piles exactly.
## Tasks
1. Implement length via tails and binary search (strictly increasing).
2. Implement reconstruction with parent pointers from the O(n^2) table.
3. Add a trace mode printing pile tops after each element.
4. Hand-trace 3 1 2 8 6 7 4 5 and compare pile-for-pile with the program.
5. Verify reconstruction is increasing and a subsequence on 50 fixed-seed inputs.
6. Document why tails alone cannot reconstruct the subsequence.
## Acceptance criteria
- Hand trace and program trace agree pile-for-pile on both sequences.
- All 50 reconstructions verify as increasing subsequences.
- Equal-elements fixture respects strict semantics (no extension on equals).
- Empty and single-element inputs return 0 and 1.
- README states the tails invariant in one precise paragraph.
## Pitfalls
- Using non-strict binary search and silently solving the non-decreasing variant.
- Reading the subsequence out of tails instead of parent pointers.
- Tracing only sorted inputs, where every placement looks trivially right.
- Off-by-one in the binary search bounds that only fails on duplicates.
## Stretch
- Envelope-nesting reduction with the descending-tie rule explained.
- Count of longest subsequences via DP extension on small inputs.
## Timebox
One focused session, roughly 2 hours with hand traces.
