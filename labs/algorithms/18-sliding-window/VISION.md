# Vision: Sliding Window
> O(n) subarray and substring scans with amortized pointer moves.

## Where this leads
- Longest/shortest substring with constraints, fixed-size maximums, rate limiting.
- Frequency-map maintenance: add right, shrink left, track validity incrementally.
- Amortized analysis in miniature: each index enters and leaves once.
## What mastering it unlocks
- Solve fixed-size maximum-sum with prefix-style window slides.
- Maintain a valid variable window for longest-substring-without-repeats.
- Argue O(n) from each pointer moving at most n steps.
- Decide fixed vs variable window from the problem statement.
- Maintain counts incrementally instead of rescanning the window.
## What it does not cover
- Two-pointer problems without window content (sorted two-sum lives next door).
- Deque-based sliding maximum in full generality (covered as extension only).
- Streaming algorithms with sublinear memory guarantees.
## Core questions you will answer
- Why does the left pointer never need to move backward in these problems?
- What makes a constraint shrinkable, and which constraints break the pattern?
- How does the frequency map stay consistent during shrinks?
- When is brute-force O(n^2) actually fine, and when must the window be used?
## How to judge progress
- Classify a substring problem as fixed or variable window on sight.
- Prove linearity by counting pointer moves, not by feeling.
- Handle empty input, single character, and all-identical inputs correctly.
## Common misuse
- Shrinking without restoring the invariant the shrink loop promises.
- Recomputing window contents from scratch each step, silently returning to O(n^2).
## After this lab
- 17-two-pointers for the pointer mechanics underneath windows.
- 05-dynamic-programming for subarray problems that need more than a window.
One-line self-test: Explain why the total pointer movement across the whole run is at most 2n.
