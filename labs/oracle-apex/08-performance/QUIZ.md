# Lab 08: APEX Performance — Quiz

**1.** Why capture an APEX Debug breakdown before optimising?

A. It is required by APEX
B. A 12-second page has identifiable large contributors; optimising the wrong one
   wastes the whole effort
C. It improves caching
D. It reduces queries

<details><summary>Answer</summary><b>B</b> — Here one region is 27% and rendering 25%; together 52%. The other seven regions are under 1%.</details>

---

**2.** What makes a predicate non-sargable?

A. Using a bind variable
B. Applying a function to the indexed column, as in `TRUNC(order_date) = :d`
C. Using ORDER BY
D. Using a join

<details><summary>Answer</summary><b>B</b> — The index does not contain computed values, so the database cannot use it. Functions go on the right, never the left.</details>

---

**3:** Why did enabling pagination have no effect?

A. It is not a performance feature
B. Pagination limits returned rows, not rows examined — with a non-selective
   filter the database still scans the table
C. It was applied to the wrong region
D. It requires a premium edition

<details><summary>Answer</summary><b>B</b> — It was tried twice because the underlying cause was a non-sargable predicate, which pagination cannot address.</details>

---

**4.** Why do literals in page processes cause database-wide problems?

A. They consume more CPU
B. Each literal value is a distinct statement requiring a hard parse, and parse
   activity contends on library cache latches shared by every session
C. They break the query plan
D. They use more memory

<details><summary>Answer</summary><b>B</b> — Latch contention is non-linear, so an APEX hard-parse problem is reported as "the database got slow".</details>

---

**5.** When is page cache a security problem rather than an optimisation?

A. Always
B. When the page contains per-user data — one user's rendered HTML could be served
   to another
C. When the page has many regions
D. When the user is an administrator

<details><summary>Answer</summary><b>B</b> — Cache individual regions instead. This page has 240 distinct sessions over 3,500 views.</details>

---

**6.** Match: expensive monthly aggregate across sessions?
**A**: Region cache
**B**: Page cache
**C**: Function result cache (RESULT_CACHE RELIES_ON)
**D**: Session state cache

<details><summary>Answer</summary><b>C</b> — It survives sessions, which is what a cross-session aggregate needs.</details>

---

**7:** At what request rate does a 60-second cache TTL stop paying?

A. Below ~60 requests/hour, where each request opens its own window and the hit
   rate is effectively zero
B. Below 2,400/hour
C. It always pays
D. Above 1,000/hour

<details><summary>Answer</summary><b>A</b> — At 2,400/hour the hit rate is 97.5%; at 60/hour it is 0%, and the cache is pure complexity.</details>

---

**8.** Why consolidate 10 dynamic actions into 3?

A. It is required
B. Each action costs event binding and condition evaluation on every page load;
   consolidation saves ~1,600 ms here
C. It reduces SQL
D. It improves security

<details><summary>Answer</summary><b>B</b> — One of the cheapest wins available: no SQL change, no schema change, no cache.</details>

---

**10:** Why is theme asset optimisation worth more than its size suggests?

A. It is easier
B. Transfer happens before the first region renders, so it does not appear in
   server timings but the user waits through all of it — 2.5 s here
C. It reduces database load
D. It improves query plans

<details><summary>Answer</summary><b>B</b> — The 15-minute minify-and-gzip fix outranked the four-hour PL/SQL fix by return.</details>

---

**11.** `v$system_event` shows `db file sequential read` dominating. Whose problem?

A. The application, entirely
B. Partly the application (more selective SQL reduces I/O) but the root cause is
   storage latency — escalate rather than rewrite
C. APEX
D. The network

<details><summary>Answer</summary><b>B</b> — Knowing where the application's responsibility ends is part of the work. Escalating a storage problem as "APEX is slow" wastes weeks.</details>

---

**12.** Why report p95 rather than the average?

A. It is easier to compute
B. The mean hides the tail users experience — here 3.2 s average against 14.6 s p95,
   with 5% of sessions unable to work
C. APEX only stores p95
D. p95 is always higher

<details><summary>Answer</summary><b>B</b> — Measure and report the statistic the requirement names.</details>

---

## Scoring

- **9–12**: Ready to tune production APEX applications.
- **7–8**: Solid; revisit sargability and cache-layer selection.
- **5–6**: Re-read THEORY on attribution, sargability, and caching.
- **<5**: Work through EXERCISES 1, 2, and 5 again.