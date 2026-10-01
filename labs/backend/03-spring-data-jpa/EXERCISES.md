# Exercises: Spring Data JPA / Pagination

## Exercise 1: Offset vs Keyset Benchmark
Seed 100k rows. Compare page 5000 via offset (`PageRequest`) vs keyset seek on
indexed `id`. Record timings and explain the gap using the query plans.

## Exercise 2: Stable Sorting
Paginate `ORDER BY salary DESC` without a tiebreaker, then with `id` as
tiebreaker. Show duplicates/shifts in the first version and their absence in
the second.

## Exercise 3: N+1 Hunt
Page an entity with a `@ManyToOne` association. Enable SQL logging, observe N+1,
then fix it with `@EntityGraph` and show the query count drop.

## Exercise 4: Slice for Export
Implement a streaming export endpoint using `Slice` (no total count) that writes
CSV in chunks. Verify constant memory usage on a large table.

## Exercise 5: Null Handling
Write a test asserting `NULLS LAST` vs `NULLS FIRST` ordering on a nullable
column, and wire it through a multi-column `Sort` (nullable column + id).
