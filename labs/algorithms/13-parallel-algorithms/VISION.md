# Vision: Parallel Algorithms
> Work/span reasoning that tells you what speedup is possible before you write a thread.

## Where this leads
- Multicore programming with threads, pools, and parallel loops used correctly.
- Performance analysis that separates algorithmic work from parallel overhead.
- Later labs on scheduling and load balancing, which assume work/span vocabulary.
## What mastering it unlocks
- Compute work and span for a parallel loop and the resulting parallelism ratio.
- Apply Amdahl's law to bound speedup from a measured sequential fraction.
- Spot a data race by naming the shared state and the interleaving that breaks it.
- Choose chunking that balances load without drowning in task overhead.
- Explain why more threads can slow a program down, with the overhead term named.
## What it does not cover
- Distributed systems: this lab is shared-memory parallelism, not networks and partitions.
- Lock-free data structure design, which needs memory-model reasoning beyond this lab.
- Automatic parallelization by compilers, which is a separate specialty.
## Core questions you will answer
- What is the difference between work, span, and wall-clock time?
- If 10 percent of a program is sequential, what speedup cap does Amdahl give on 16 cores?
- Which variables in a chunked sum need synchronization, and which provably do not?
- Why is a reproducible fixed-seed test valuable for parallel code?
## How to judge progress
- Annotate a loop nest with its work, span, and the bottleneck step.
- Rewrite a racy counter so the result is exact, and explain why the fix works.
- Predict whether parallelizing a given loop is worth it, with numbers.
## Common misuse
- Measuring speedup against an unoptimized baseline, which inflates the ratio.
- Sharing one Random or counter across threads and wondering why results drift.
## After this lab
- 24-scheduling-algorithms for assigning work to machines over time.
- 23-load-balancing for distributing work evenly at runtime.
One-line self-test: Define work and span for parallel sum over n elements with p chunks.
