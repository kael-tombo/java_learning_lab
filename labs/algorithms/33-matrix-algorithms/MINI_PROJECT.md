# MINI_PROJECT — Matrix Algorithms
> Build a multiply-and-verify kit: naive O(n^3), Strassen 2x2 check, and Fibonacci-by-power, plus a timing note with no invented numbers.

## Inputs
- Fixed 3x3 pair from MOCK Q1 and fixed 2x2 pair from MOCK Q2.
- Random float matrices n = 128, 256, 512 with a fixed seed for timing only.

## Build steps
1. Implement ijk naive multiply; verify the 3x3 product rows [30,24,18] / [84,69,54] / [138,114,90].
2. Implement the 7-product Strassen step for 2x2 blocks; assert equality with naive on the fixed pair ([[36,41],[64,73]]).
3. Implement 2x2 binary matrix exponentiation; verify fib20 = 6765 from M^20[0][1].
4. Time naive at n = 128/256/512 (3 runs each, report median ms) and record machine + JDK in the table.
5. Write the crossover note: why Strassen's lower exponent does not win at small n (recursion overhead, temporaries, cache effects).

## Acceptance criteria
1. 3x3 product rows match exactly as listed above.
2. Strassen 2x2 output matches naive entry-by-entry on the fixed pair.
3. fib20 prints 6765 from the powered matrix, not from a loop.
4. Timing table shows median of 3 runs per size with machine/JDK noted; no cells copied from elsewhere.
5. Crossover note names at least two concrete overheads (temporaries, recursion base case).
6. All arithmetic in double or long is documented with the choice justified in one line each.

## Analysis prompts
1. How does transposing B before the ijk loop change your n=512 time, and why?
2. What is the temporary-memory cost of one Strassen level vs one naive level?
3. Where does exponentiation-by-squaring beat linear iteration for recurrences?

## Non-goals
- Full recursive Strassen to arbitrary n, sparse formats (CSR), and eigensolvers.

## Worked reference (verified outputs)
- 3x3 product prints rows [30, 24, 18], [84, 69, 54], [138, 114, 90]; any loop-order change must reproduce them.
- Strassen 2x2 prints [[36,41],[64,73]] matching naive; fib20 prints 6765 from the powered matrix.

## Stretch
- Add a transposed-B variant and report the n=512 delta with cache-miss reasoning.
- Implement blocked multiply with tile 128/256 and show the best tile per size from real runs.
