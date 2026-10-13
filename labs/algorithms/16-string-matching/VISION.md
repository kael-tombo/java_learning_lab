# Vision: String Matching
> Finding patterns in linear time: naive limits, KMP automata, rolling hashes.

## Where this leads
- Log scanning, text search, and plagiarism-style exact-match tooling.
- Automaton thinking: the prefix function as a tiny state machine.
- Fingerprinting: trading certainty for speed with verifiable hashes.
## What mastering it unlocks
- Exhibit the input family that forces naive search into Theta(n*m).
- Compute the prefix function by hand and explain each fallback.
- Run KMP search and account for every character examination.
- Maintain a rolling hash update and repair negative residues correctly.
- Choose between KMP and Rabin-Karp from the problem constraints.
## What it does not cover
- Regular expression engines, backreferences, and backtracking matchers.
- Approximate matching (edit distance, k-mismatches) and multiple-pattern automata in depth.
- Suffix arrays and suffix trees, which live in advanced string labs.
## Core questions you will answer
- Why is the total fallback work of prefix construction linear, not quadratic?
- After a full match, why resume at pi[m-1] instead of 0?
- Why does a hash match still need direct verification?
- When does naive search beat KMP in practice despite worse asymptotics?
## How to judge progress
- Trace pi construction and KMP search on unseen patterns without errors.
- Implement rolling hash updates that never go negative.
- Justify the algorithm choice for a stated alphabet and pattern count.
## Common misuse
- Restarting KMP at 0 after each match and missing overlaps.
- Using hash equality as proof of a match without the confirming comparison.
## After this lab
- 08-string-algorithms for the broader string-algorithm context.
- 27-suffix-array for indexing a fixed text under many queries.
One-line self-test: Explain what pi[i] means and why it bounds the shift after a mismatch.
