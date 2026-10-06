# Lab 06: APEX Migration — Flashcards

## Inventory

---
**Q**: What is the real size of a "20-screen" Forms app?
**A**: 538 objects: 340 triggers, 57 blocks, 48 LOVs, 31 alerts, 23 canvases.

---
**Q**: Screen-count estimate vs object estimate here?
**A**: 46 days vs 213 days. **4.6× underestimate.**

---
**Q**: Why query the source?
**A**: Interviews produce screen counts; the source produces trigger counts. Only the latter is the work.

---

## Classification

---
**Q**: Four migration classes?
**A**: 1:1 · SIMPLIFIED · REDUNDANT · NEW.

---
**Q**: Typical distribution here?
**A**: 35% / 16% / 37% / 12%.

---
**Q**: What does REDUNDANT buy?
**A**: 37% of the app removed for ~4% of the effort, plus less maintenance and less risk.

---
**Q**: Why not map everything 1:1?
**A**: It preserves every old problem. Some Forms functionality exists because it
was the only option in 1998.

---

## Component Mapping

| Forms | APEX |
|-------|------|
| Canvas | Page |
| Data block | Interactive Report or Form |
| Item | Page item |
| View | Region |
| LOV | Popup LOV |
| Alert | Validation (preferred) or `APEX_APPLICATION.ALERT` |
| WHEN-NEW-FORM | Process: On Page Load |
| WHEN-NEW-ITEM | Dynamic Action |
| WHEN-BUTTON | Process condition on `:REQUEST` |
| PRE-DML | Validation + constraint |
| POST-QUERY | **Delete** |
| KEY-QUERY | **Delete** |
| Menu stack | Breadcrumbs + navigation |
| Savepoint | **No equivalent** |

---

## Deletion

---
**Q**: POST-QUERY count here, and fate?
**A**: 118, deleted — region SQL joins absorb them.

---
**Q**: KEY-QUERY count here, and fate?
**A**: 47, deleted — no equivalent needed; converting would run the query twice.

---
**Q**: Query count for 50 records, POST-QUERY vs joined region?
**A**: 50 queries → 1 query.

---
**Q**: Share of trigger effort that is deletion?
**A**: ~43%.

---

## Conversion

---
**Q**: Convert by syntax or by intent?
**A**: By intent — ask what event the trigger responds to, then find the APEX mechanism for that event.

---
**Q**: WHEN-NEW-ITEM-INSTANT → ?
**A**: Dynamic Action: Event Change, condition non-null, Set Value.

---
**Q**: WHEN-NEW-RECORD-INSTANCE `INSERTING` → ?
**A**: Computation (defaults) + a process whose condition is `:P1_ID IS NULL`.

---
**Q**: Hardest LOV type to convert, and why?
**A**: Return-value LOVs (7 of 48). Forms assigns return values automatically; APEX
needs a Dynamic Action. 65% of LOV effort, 17% of objects.

---

## Validation

---
**Q**: Three validation homes?
**A**: Database constraint (enforcement) · APEX validation (message) · item LOV or
default (usability).

---
**Q**: What must not change during migration?
**A**: Level-3 constraint coverage. Dropping it while adding APEX validations makes
the system look safer while enforcing less.

---
**Q**: How do you distinguish create from update in APEX?
**A**: Primary key item null (create) vs non-null (update).

---

## Transactions and Navigation

---
**Q**: Forms savepoint → APEX?
**A**: No equivalent. A page process commits at request end. Accept the loss (~2
user-hours/week); 20 days of design is not a trade.

---
**Q**: Why not copy the Forms menu tree?
**A**: Users don't navigate hierarchically. Breadcrumbs beyond 3–4 levels are
ignored; 31 menu items require memorising. Redesign from the work (5 days vs 1).

---

## Staging

---
**Q**: Stage order?
**A**: Inventory → read-only → core CRUD → complex transactions → parallel run.

---
**Q**: Why read-only first?
**A**: Delivers value in 3 weeks, builds APEX familiarity on low-risk pages, no data
corruption risk, and survives programme cancellation.

---
**Q**: Big-bang alternative?
**A**: 20 weeks with nothing delivered until week 20 and corruption risk from week 4.

---
**Q**: Cutover gate?
**A**: Zero stop-the-line cases and zero "wrong data written" — not zero total
discrepancies, because rounding differences are not bugs.

---

## Numbers to Remember

| Metric | Value |
|--------|-------|
| Total objects | 538 |
| Triggers | 340 |
| POST-QUERY + KEY-QUERY | 165 (43% of trigger effort) |
| Redundant share | 37% of app, ~4% of effort |
| Screen-count underestimate | 4.6× |
| Corrected estimate | ~301 days |
| Contingency | 12% |
| Level-3 constraint coverage | must be identical before/after |
| Expected cosmetic discrepancies in parallel run | 8% |

---

## Quick Reference

| Task | Mechanism |
|------|-----------|
| Forms source inventory | Query `ALL_SOURCE` for trigger patterns |
| Default new-record values | Computation, Before Header |
| Item change effect | Dynamic Action |
| Business rule before DML | Process + `RAISE_APPLICATION_ERROR` |
| Enum rule | Database constraint + APEX validation |
| LOV filtering | Popup LOV with depends-on |
| LOV return values | Dynamic Action on Selection |
| User message | `APEX_APPLICATION.ALERT` (validation preferred) |

---

## Anti-Patterns

1. Estimating from screen count.
2. Converting POST-QUERY instead of deleting it.
3. Leaving logic in the client tier.
4. Dropping level-3 constraints.
5. Replicating savepoint semantics.
6. Copying the Forms menu tree.
7. Migrating everything 1:1.
8. Big-bang cutover.
9. Deleting a "redundant" object without user confirmation.

---

## Study Tips
1. Reproduce the inventory counts from memory.
2. Explain in one sentence why POST-QUERY is deleted rather than converted.
3. State why level-3 constraint coverage must not drop.
4. Name the LOV type that costs the most effort and why.