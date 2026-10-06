# Lab 05: Technical Foundations — Quiz

**1.** Why use one concurrent program with a mode parameter instead of three?

A. Fewer programs to register
B. Validation logic stays a single source of truth, so VALIDATE_ONLY is a genuine rehearsal
C. It runs faster
D. Oracle requires it

<details><summary>Answer</summary><b>B</b> — Three programs duplicate validation and drift apart. One program makes the rehearsal real.</details>

---

**2.** What makes VALIDATE_ONLY an honest rehearsal?

A. It uses a different query
B. It calls the exact same `validate` procedure that PROCESS calls
C. It runs first chronologically
D. It uses a faster path

<details><summary>Answer</summary><b>B</b> — Reimplemented validation diverges within two releases.</details>

---

**3.** Why avoid direct DML on `PO_HEADERS_ALL` even when it is faster?

A. It is not actually faster with indexes
B. It skips validation, propagation, and audit, and breaks on the next patch
C. Oracle forbids it outright
D. It requires more memory

<details><summary>Answer</summary><b>B</b> — The overhead is ~8 minutes against a 3-day manual process. That is 1.5% for permanent correctness.</details>

---

**4.** What is the danger of 10,000 API calls in one transaction?

A. It will fail
B. Undo growth, long lock duration, and a full restart on any failure
C. It is slow only
D. It cannot be logged

<details><summary>Answer</summary><b>B</b> — The real cost is the restart: ~12.5 minutes redone versus ~2 minutes with batching.</details>

---

**5.** Why commit every ~500 rows?

A. Oracle requires it
B. Bounded undo and bounded restart cost, enabling resume
C. It improves throughput
D. It reduces errors

<details><summary>Answer</summary><b>B</b> — Resume is the point. Restarting 10,000 rows is not a rerun; it is a duplicate risk.</details>

---

**6.** Why does the error log use `PRAGMA AUTONOMOUS_TRANSACTION`?

A. To commit the business data too
B. So the log commits independently and survives the failure that wipes the caller's transaction
C. To improve speed
D. It is required by MOAC

<details><summary>Answer</summary><b>B</b> — Without it, the error rows are lost exactly when you need them. The problem is atomicity, not size.</details>

---

**7.** What should happen when MOAC access to an operating unit is absent?

A. Process anyway using a default org
B. Raise a clear error and stop
C. Skip that org silently
D. Process all orgs

<details><summary>Answer</summary><b>B</b> — Silently processing all orgs is the failure mode found during an audit. In the lab, that is $33M of exposure.</details>

---

**8.** Why separate the log from the XML report?

A. Different file formats
B. The log is for operators during failure; the XML is for business detail per line
C. XML is faster
D. Oracle limits log length

<details><summary>Answer</summary><b>B</b> — Packing 10,000 result rows into the log makes the log unreadable when it is needed.</details>

---

**9.** What makes ROLLBACK possible rather than guesswork?

A. Database backups
B. An audit row per change, keyed by run ID, with old values
C. A read-only mode
D. Manual notes

<details><summary>Answer</summary><b>B</b> — A change with no audit row is permanently unreversible. Rollback becomes a lookup, not archaeology.</details>

---

**10.** Which registration step is most often missed and causes 2am escalations?

A. Creating the application
B. Assigning the program to a responsibility — operators get no privilege
C. Adding the executable
D. Creating parameters

<details><summary>Answer</summary><b>B</b> — Test submission with a real operator account. The fix is five minutes; discovery is an escalation.</details>

---

## Scoring
- **9–10**: Ready to build production concurrent programs.
- **7–8**: Solid; revisit batching and audit completeness.
- **5–6**: Re-read THEORY on modes, durability, and MOAC.
- **<5**: Work through EXERCISES 3, 4, and 5 again.