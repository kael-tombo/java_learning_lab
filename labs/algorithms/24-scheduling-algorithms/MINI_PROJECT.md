# Mini-Project: Deadline Task Checker

## Goal

Build a checker that takes tasks with durations and deadlines, orders them
by earliest deadline, and reports whether the schedule meets every deadline.

## Inputs

- Fixed task set: (duration, deadline) pairs (2,5), (1,3), (3,8), (2,6).
- Single processor, tasks run back to back with no preemption.

## Steps

1. Hard-code the four tasks as pairs in program order.
2. Sort a copy by deadline ascending (EDD order).
3. Simulate completion times cumulatively along that order.
4. Flag each task met or missed against its own deadline.
5. Print the order, cumulative times, and per-task verdicts.
6. Compute maximum lateness (worst completion minus deadline, floor 0).
7. Assert the fixed set is fully feasible and print the assertion.
8. Re-run on a second set with one impossible task to show a miss.

## Acceptance criteria

1. EDD order printed as deadlines 3, 5, 6, 8 for the fixed set.
2. Completion times printed as 1, 3, 5, 8 with all verdicts met.
3. Maximum lateness reported as 0 for the feasible set.
4. Second set reports at least one missed deadline by task id.
5. Sorting and simulation verified by hand-computed asserts in code.
6. Verdict logic treats completion equal to deadline as met.
7. All output uses plain ASCII characters.

## Grading note

- EDD order 3, 5, 6, 8 with completions 1, 3, 5, 8 required.
- Second task set must show at least one miss by task id.
- Completion equal to deadline counts as met, not missed.

## Stretch

- Add release dates and show where EDD stops being optimal in one example.
- Report total tardiness alongside maximum lateness for both sets.
