# Mock Interview: Pagination/Sorting Framework for Large Datasets (Lab 03)

**Role:** Senior Backend Engineer
**Duration:** 55 minutes
**Difficulty:** Easy to Medium to Hard

---

## Round 1: Easy Problem and API Design (5 min)

**Interviewer:** Design a generic pagination and sorting framework. What are the core components?

**Candidate:** The framework has two sides: the request (Pageable) and the response (Page). Pageable contains page number, page size, sort criteria, and optionally a cursor for keyset pagination. Page contains the items list, total count, pagination metadata (hasNext, hasPrevious, totalPages), and the next cursor. The framework must support offset-based pagination (LIMIT/OFFSET) for small datasets and simple UIs, and cursor-based (keyset pagination) for large, real-time datasets.

**Interviewer:** What is wrong with offset-based pagination for large datasets?

**Candidate:** Deep offset pagination is O(offset + limit) because the database must scan and discard offset rows. At offset 1,000,000, the database scans a million rows even though only 20 are returned. The OFFSET clause in SQL does exactly this. Additionally, under high write load, offset-based pagination can miss or duplicate rows because the ordering may change between pages. Cursor-based pagination avoids these issues by using WHERE id > lastSeen ORDER BY id LIMIT 20 which leverages the primary key index for O(log n + limit) performance.

**Interviewer:** What is the structure of your Sort specification?

**Candidate:** Sort is a list of SortOrder records, each with a property name, direction (ASC/DESC), and null handling (NULLS FIRST/NULLS LAST). Multiple sort orders create a composite sort. Explicit null handling is important because NULL comparison behavior differs across databases: PostgreSQL treats NULL as larger than any value, MySQL treats NULL as smaller. Making null handling explicit ensures predictable behavior regardless of database.

---

## Round 2: Medium Keyset Pagination Deep Dive (10 min)

**Interviewer:** Explain keyset pagination in detail. What are the prerequisites for using it?

**Candidate:** Keyset pagination requires a unique, ordered column to serve as the cursor, typically the primary key or a composite of (sort_column, id). The query pattern is: SELECT FROM table WHERE (sort_col, id) > (lastSortVal, lastId) ORDER BY sort_col, id LIMIT 20. No OFFSET is needed. The database uses a composite index on (sort_col, id) for an efficient index seek. Prerequisites: (1) The cursor column must be indexed. (2) The cursor value must be unique. (3) The client must send the last cursor from the previous page.

**Interviewer:** How do you handle the no OFFSET constraint when the user wants page 5?

**Candidate:** Keyset pagination does not support arbitrary page jumps. Solutions include: (1) Hybrid approach use offset-based for the first few pages and keyset for deeper pages. (2) Estimate the cursor for the desired page using inverse distribution functions. (3) Use a different sorting strategy that maps page numbers to cursors. Most infinite-scroll and load more UIs do not need page numbers, making keyset the natural choice.

**Interviewer:** How does your Pageable.cursor work? How do you encode the cursor?

**Candidate:** The cursor is an opaque string encoding the last seen sort values. I use Base-64 encoding of the composite cursor value. For a single-column sort on id, the cursor is just the last id as a string. For multi-column sort on (score, name, id), I serialize the tuple and Base-64 encode it. The client sends this cursor back in the next request. The server decodes and uses it in the WHERE clause. I add an HMAC signature to prevent clients from manipulating the cursor.

---

## Round 3: Medium-Hard Sorting and Comparison (10 min)

**Interviewer:** How does your framework handle sorting on computed fields or nested paths like address.city?

**Candidate:** I support nested property paths using dot notation. The framework splits the path by . and navigates the object graph. For SQL generation, nested paths become JOINs and ORDER BY on the joined column. For performance, I recommend denormalizing commonly sorted nested fields or using computed columns with indexes.

**Interviewer:** Case-insensitive sorting how would you add it?

**Candidate:** I would add a caseInsensitive flag to SortOrder. When enabled, the comparator converts both values to lowercase before comparison. For SQL it becomes ORDER BY LOWER(name) ASC. I would also add locale-aware collation via a Collator parameter for internationalized data.

**Interviewer:** How do you handle sorting by nullable columns?

**Candidate:** The NullHandling enum (NULLS_FIRST, NULLS_LAST) defines insertion behavior. In the comparator if both are null they are equal. If one is null, null handling decides first or last. For SQL it becomes ORDER BY score ASC NULLS LAST or using CASE WHEN score IS NULL THEN 1 ELSE 0 END for databases without native nulls clause support.

---

## Round 4: Hard Performance and Production (15 min)

**Interviewer:** The COUNT query for totalCount is expensive on large tables. How do you avoid it?

**Candidate:** Several strategies: (1) Estimate using EXPLAIN or pg_class.reltuples. (2) Cache the count and update asynchronously every few seconds. (3) Add an includeCount flag defaulting to false. (4) Use the hasNext trick fetch size + 1 rows, return size, set hasNext = rows.size() > size. This completely avoids COUNT. (5) For keyset pagination, total count is often irrelevant. I would use strategy (4) as the default.

**Interviewer:** How would you implement streaming export of 10 million records?

**Candidate:** Return a Stream backed by keyset pagination that fetches records in batches of 1000. The Spliterator implementation fetches the next page when the current buffer is nearly empty. The HTTP response uses chunked transfer encoding. For database streaming, I use a forward-only read-only JDBC cursor with fetchSize set appropriately to avoid loading the entire result set into memory.

**Interviewer:** How does your framework handle cursor invalidation when a row is deleted between pages?

**Candidate:** If a row is deleted, the next page starts from the cursor position and returns the next available row. No rows are missed because the cursor is the last successfully returned value. The WHERE clause correctly skips the deleted row. The only issue is if the cursor value itself changes due to an update. Using an immutable sort column or snapshot isolation prevents this. For most applications this edge case is rare enough to accept.

**Interviewer:** How do you test a pagination framework?

**Candidate:** I test: (1) Correct page boundaries first/last/out-of-bounds pages. (2) Sort correctness ascending/descending/multi-column/null handling. (3) Keyset pagination sequential pages return consecutive non-overlapping results. (4) Edge cases empty dataset, single page, page size larger than dataset, duplicate sort values. (5) Concurrent modifications verify no inconsistent results. (6) Streaming verifies all records are returned without memory exhaustion.

---

## Round 5: Wrap-up (5 min)

**Interviewer:** What is the most important lesson about pagination for a junior developer?

**Candidate:** Never use OFFSET-based pagination beyond the first few pages on a large or write-heavy dataset. Always prefer keyset pagination for production systems. The performance difference between OFFSET 1000000 LIMIT 20 (scans 1M rows) and WHERE id > 1000000 LIMIT 20 (scans 20 rows via index) is three to four orders of magnitude. Always include a unique tiebreaker column in your ORDER BY to avoid row skipping or duplication. The primary key is the natural choice.
