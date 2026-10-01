# Quiz: Spring Data JPA

## Q1
What is the difference between offset pagination and keyset (cursor) pagination?
a) No difference b) Offset uses `page/size` and degrades on deep pages; keyset seeks from the last seen key via an index (O(log n + limit)) c) Keyset is slower d) Offset cannot sort
**Answer: b)**

## Q2
Why is `SELECT COUNT(*)` a problem for large paginated tables?
a) It is free b) It scans/counts all matching rows — O(n) per page request c) It locks the schema d) It returns floats
**Answer: b)**

## Q3
In Spring Data, which interface gives you `Page<T> findAll(Pageable p)` for free?
a) `CrudRepository` b) `PagingAndSortingRepository` / `JpaRepository` c) `EntityManager` d) `JdbcTemplate`
**Answer: b)**

## Q4
What does `NULLS FIRST` / `NULLS LAST` control?
a) Connection pooling b) Placement of NULLs in `ORDER BY` c) Batch size d) Cache TTL
**Answer: b)**

## Q5
Which `Pageable` mistake causes non-deterministic pages?
a) Sorting by a unique key b) Sorting by a non-unique column with no tiebreaker — rows shift between pages c) Using page size 20 d) Sorting at all
**Answer: b) — always add a unique tiebreaker (e.g. id) to the sort**

## Q6
What is the N+1 problem in JPA pagination?
a) Too many pages b) One query for the page + N lazy-load queries for associations c) Off-by-one page index d) Null pages
**Answer: b) — fix with `@EntityGraph` / fetch join**

## Q7
When should you stream (`Stream<T>` / `Slice`) instead of `Page<T>`?
a) Never b) For large exports where total count is unnecessary or too expensive c) For single rows d) For DDL
**Answer: b)**

## Q8
Keyset pagination requires what on the sort key?
a) Nothing b) An indexed, preferably unique (or unique-tiebroken) ordering so the `WHERE key > lastSeen` seek is stable c) A full table scan d) A UUID only
**Answer: b)**

## Q9
What does `Sort.by("salary").descending().and(Sort.by("id"))` express?
a) Random order b) Multi-column sort: salary DESC, id ASC tiebreaker c) Two queries d) Grouping
**Answer: b)**

## Q10
Why is the lab's framework generic (`PageRequest<T>`, comparators)?
a) Style b) So pagination/sorting works for any entity type without duplicating offset/cursor, metadata, and null-handling logic c) Generics are faster d) To avoid SQL
**Answer: b)**
