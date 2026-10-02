# Dynamic Programming — Theoretical Foundation

## Key Properties
### Optimal Substructure
Optimal solution contains optimal solutions to subproblems.

### Overlapping Subproblems
Same subproblems solved multiple times if naive recursion is used.

## Two Approaches

### Top-Down (Memoization)
- Recursive with caching
- Start from original problem, recurse to base cases
- Store computed results in array/HashMap
- Time: subproblems × time per subproblem
- Space: O(subproblems) + recursion stack

### Bottom-Up (Tabulation)
- Iterative
- Solve subproblems in order of increasing size
- Build table from base cases to target
- Often faster (no recursion overhead)
- Can be space-optimized (rolling arrays)

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Lecture 19: Dynamic Programming I: Fibonacci, Shortest Paths" (instructor Erik Demaine), MIT OCW 6.006 Fall 2011 — https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/resources/lecture-19-dynamic-programming-i-fibonacci-shortest-paths — frames DP as "careful exhaustive search" built on guessing + memoization + reusing subproblem solutions, matching the lab's top-down/bottom-up split — verify against the lab's memoization exercise.
- "6.006 Introduction to Algorithms, Lecture 16: Dynamic Programming Subproblems" (Demaine/Ku/Solomon), MIT OCW 6.006 Spring 2020 — https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/pages/lecture-notes — SRTBOT recipe (Subproblems, Relate, Topological order, Base cases, Original problem, Time); running time = (#subproblems) × (non-recursive work per subproblem), treating memoized recursions as O(1) — maps directly onto the lab's "Time: subproblems × time per subproblem" line.
- Same MIT 6.006 DP sequence (Spring 2020 Lecs 15–18, listed on the lecture-notes hub above) — naive Fibonacci recursion is exponential, and the single fix is a memo table so each of the O(n) subproblems is solved at most once — good proof-idea anchor for the lab's overlapping-subproblems exercise.
- Same sequence, DAG-shortest-paths-as-DP observation — a DAG relaxation order is itself a topological-order DP, which connects the lab's bottom-up tabulation exercise to graph material — confirm the lab covers DAG ordering before citing.
