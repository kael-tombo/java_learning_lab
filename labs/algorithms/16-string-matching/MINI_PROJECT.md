# Mini Project: KMP From Scratch
> Prefix function plus search, both instrumented, both hand-traced.

## Background
- pi[i] is the longest proper prefix that is also a suffix ending at i.
- Search fallbacks reuse pi; each text character is examined at most twice.
- Counters turn the linear claim into a measured fact.
## Goal
Implement prefix construction and KMP search with comparison counters.
Hand-trace pi for ababaca and match the program output exactly.
## Tasks
1. Implement pi construction with the fallback while-loop.
2. Assert pi(ababaca) equals [0,0,1,2,3,0,1].
3. Implement search reporting all match positions including overlaps.
4. Assert aba in ababa reports [0, 2].
5. Count character comparisons on repetitive vs random fixtures for naive and KMP.
6. Fuzz 100 fixed-seed pairs against direct scanning for identical hit lists.
## Acceptance criteria
- pi fixture matches exactly, and the hand trace agrees.
- Overlap fixture reports both positions.
- Fuzz shows zero hit-list mismatches.
- Repetitive fixture shows KMP with fewer comparisons than naive.
- Empty pattern and pattern-longer-than-text are handled with messages.
## Pitfalls
- Resuming at 0 instead of pi[m-1] after a match, dropping overlaps.
- Quadratic fallback loops from resetting j without the pi chain.
- Treating hash-style shortcuts as applicable to KMP (they are not).
- Tracing only non-repetitive patterns where fallbacks never trigger.
## Stretch
- Rabin-Karp third implementation for a three-way counter comparison.
- Automaton-table version of KMP with the transition table printed.
## Timebox
One evening session, roughly 2 to 3 hours with traces.
