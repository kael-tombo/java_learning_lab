# Vision: Scheduling Algorithms

## Direction

This lab covers three scheduling views: greedy interval selection for
maximizing throughput on one resource, EDF with its utilization test for
periodic deadlines, and list scheduling with its makespan guarantee for
parallel machines. The practical skill is stating each rule, its bound, and
when the bound applies.

## What to learn

- Interval scheduling: earliest-finish greedy is optimal; O(n log n).
- Exchange argument: why earliest finish can always replace a later pick.
- EDF: feasible on one processor exactly when utilization is at most 1.
- Makespan: total work and longest job both lower-bound the optimum.
- List scheduling: greedy least-loaded gives the 2 - 1/m guarantee.

## Non-coverage

- This lab does not cover multiprocessor real-time schedulability theory.
- It does not cover priority inversion, locks, or resource sharing.
- It does not cover stochastic scheduling or queueing theory.
- It does not cover OS scheduler internals or thread-pool tuning.
- All inputs here are fixed arrays; no live workload tracing is required.

## How to use this lab

Implement the interval greedy from MOCK_INTERVIEW Q1, the utilization test
from Q2, and the list scheduler from Q3. Then run MINI_PROJECT on a room
booking dataset and verify the greedy count against brute force.

## Pitfalls

- Sorting intervals by start time and losing optimality.
- Testing EDF feasibility with rate-monotonic bounds.
- Citing makespan without stating both lower bounds first.

## Done when

- You can prove interval optimality with the exchange argument out loud.
- You can state the EDF utilization test and its exact condition.
- You can name both makespan lower bounds before computing anything.
- You can state the list-scheduling bound and what LPT changes.
