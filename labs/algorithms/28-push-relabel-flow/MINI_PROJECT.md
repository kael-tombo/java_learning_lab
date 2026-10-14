# Mini-Project: Bipartite Matching via Flow

## Goal

Solve maximum bipartite matching by reduction to max flow on a fixed
applicants-to-jobs graph, and verify the matching size by hand.

## Inputs

- Applicants A1, A2, A3 and jobs J1, J2, J3 with fixed edges below.
- Edges: A1-J1, A1-J2, A2-J2, A2-J3, A3-J1 (5 edges, unit capacity).

## Steps

1. Build a flow network: source to applicants, edges as given, jobs to sink.
2. Set every capacity to 1 so paths carry single assignments.
3. Run Edmonds-Karp from this lab to compute max flow.
4. Recover the matching: applicant-job edges carrying flow 1.
5. Print each matched pair and the total matching size.
6. Assert the size equals 3 with all jobs distinct and all edges real.
7. Show one augmenting path found in the first iteration.
8. State why unit capacities make flow value equal matching size.

## Acceptance criteria

1. Reported matching size is 3 (perfect for this fixture).
2. Every pair printed uses an edge from the fixed list.
3. No job appears in more than one printed pair.
4. Assert on size, distinctness, and edge membership all pass.
5. First augmenting path printed as a node id sequence.
6. Reason statement cites unit capacities and path-to-pair mapping.
7. All output uses plain ASCII characters.

## Grading note

- Matching size 3 with all pairs from the fixed edge list.
- Job distinctness and edge membership asserts must pass.
- First augmenting path printed as a node id sequence.

## Stretch

- Remove edge A3-J1 and report the new maximum with reasoning.
- Add applicant A4 with edge A4-J3 only; re-run and explain the result.
