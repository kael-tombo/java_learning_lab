# Flashcards: Spring Data JPA / Pagination

## Q: Offset vs keyset pagination?
**A:** Offset = `page/size`, O(n) count + deep-page slowdown. Keyset = seek from last key, O(log n + limit), stable.

## Q: Which repository gives `Page<T> findAll(Pageable)`?
**A:** `PagingAndSortingRepository` / `JpaRepository`.

## Q: How to avoid non-deterministic pages?
**A:** Always add a unique tiebreaker sort (e.g. `id`) after non-unique columns.

## Q: What is the N+1 problem?
**A:** 1 query for the page + N lazy queries for associations; fix with `@EntityGraph` or fetch join.

## Q: `NULLS FIRST` / `NULLS LAST`?
**A:** Controls where NULLs appear in `ORDER BY` results.

## Q: When to use `Slice` or `Stream` instead of `Page`?
**A:** Large exports/scans where the total `COUNT(*)` is unnecessary or too expensive.

## Q: Keyset pagination needs what?
**A:** Indexed, unique (or unique-tiebroken) sort key for a stable `WHERE key > lastSeen` seek.

## Q: Multi-column sort example?
**A:** `Sort.by("salary").descending().and(Sort.by("id"))` — salary DESC, id tiebreaker.

## Q: Cost of `COUNT(*)` per page?
**A:** O(n) over matching rows — cache it or drop it (`Slice`) for huge tables.

## Q: Why a generic pagination framework?
**A:** One implementation of offset/cursor logic, metadata (`hasNext`, total), and null handling reused across entities.
