# Lab 05: APEX Performance — Quiz

**1.** Why capture an APEX Debug breakdown before changing anything?

A. It is required by APEX
B. A 30-second page has one largest contributor, and optimising the wrong
   component wastes the whole effort
C. It improves caching
D. It reduces query count

<details><summary>Answer</summary><b>B</b> — In this lab, SQL is 74% and rendering 13%. Optimising rendering first addresses a seventh of the problem.</details>

---

**2.** What does a collection solve?

A. Slow queries
B. 16 regions issuing redundant queries over the same rows
C. Export performance
D. Session state size

<details><summary>Answer</summary><b>B</b> — 16 queries become 1. It removes redundant scanning, not the aggregation work itself.</details>

---

**3.** When is a collection the wrong tool?

A. When there are many regions
B. When each region genuinely needs different data — it is per-request, so
   sharing only helps when the rows are shared
C. When the data is large
D. When caching is enabled

<details><summary>Answer</summary><b>B</b> — For different aggregations over different row sets, separate queries remain correct.</details>

---

**4.** What is a cache's invalidation trigger?

A. Its TTL
B. The stated answer to "when does this become wrong" — a TTL for bounded
   staleness, or an explicit clear for a reference table
C. The session timeout
D. The cache size

<details><summary>Answer</summary><b>B</b> — A cache with no stated trigger is a latent incident that works until the day someone needs the fresh number.</details>

---

**5.** Why should you not cache a page containing per-user data?

A. It is slower
B. One user's HTML could be served to another
C. APEX does not support it
D. It uses more memory

<details><summary>Answer</summary><b>B</b> — Cache the region, not the page, when the page is personalised.</details>

---

**6.** At what request rate does caching stop being worthwhile?

A. Above 1,000/hour
B. It depends on the hit rate, which falls with request rate — below roughly
   120 requests/hour a 30 s TTL yields near-zero hits
C. Below 100/hour
D. Never

<details><summary>Answer</summary><b>B</b> — Measure the hit rate. At 6,250/hour it is 98%; at 12/hour it is ~0%, and the cache is pure overhead.</details>

---

**7.** Row-by-row vs set-based at 100,000 rows?

A. Similar
B. ~30 minutes vs ~1,500 seconds — roughly 120×
C. Row-by-row is faster
D. Set-based uses more memory

<details><summary>Answer</summary><b>B</b> — The ratio converges to ~120× because the per-row cost differs, not the fixed cost.</details>

---

**8.** Why bound an export rather than allow it to run?

A. To reduce database load only
B. An unbounded export has unpredictable time and may exceed the HTTP timeout;
   refusing in one second beats failing after four minutes
C. Exports must be CSV
D. It is a licensing requirement

<details><summary>Answer</summary><b>B</b> — A silently truncated export produces a spreadsheet that reconciles to nothing.</details>

---

**9.** Why add cascading filters?

A. They look better
B. They prevent invalid combinations, which otherwise scan the full filtered range
   just to prove emptiness — 384 of 480 combinations are invalid here
C. They are required by APEX
D. They reduce session state

<details><summary>Answer</summary><b>B</b> — ~15 minutes/day of wasted database CPU, plus better UX.</details>

---

**10.** Why report p95 rather than the average?

A. It is easier to compute
B. The mean hides the tail users actually experience — here 4.2 s average against
   30 s p95, with timeouts in p99
C. APEX reports p95
D. p95 is always lower

<details><summary>Answer</summary><b>B</b> — The requirement specifies p95, and ~2.5% of sessions (30 users/day) hit the timeout range.</details>

---

## Scoring
- **9–10**: Ready to optimise a production APEX application.
- **7–8**: Solid; revisit caching triggers and set-based rewriting.
- **5–6**: Re-read THEORY on attribution and caching.
- **<5**: Work through EXERCISES 1, 3, and 5 again.