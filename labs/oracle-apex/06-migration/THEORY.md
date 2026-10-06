# Lab 06: APEX Migration — Theory

## The Scenario

Convert a Forms-based Inventory Management system — 20+ canvases, 50+ data
blocks — into an APEX application.

## Principle 1: The migration is an inventory exercise before it is a build exercise

Forms applications resist summarisation. A director asking "how big is it?"
receives "about 20 screens". The actual inventory:

```
Canvases:                    23
Data blocks:                 57
Triggers:                   340   ← the actual size
LOVs:                        48
Alerts:                      31
Menus / stacks:              12
Form-level procedures:       19
Window triggers:              8
```

**Triggers are the migration.** 340 triggers is the work; 23 canvases is the
navigation. Anyone estimating from screen count will be out by an order of
magnitude.

```
Estimate from screens:   23 screens × 2 days  = 46 days   ← wrong
Estimate from triggers:  340 × 0.5 day + 46   = 216 days   ← roughly right
```

The inventory must therefore be produced by **querying the Forms source**, not by
interviewing the developer who wrote it.

## Principle 2: The client tier no longer exists

This is the structural change that makes migration more than a UI exercise.

```
Forms:  business logic lives in the CLIENT tier
        WHEN-NEW-RECORD-INSTANCE runs in the user's session
        POST-QUERY runs per record
        A user with Forms open holds that logic in their workstation

APEX:   business logic lives in the SERVER tier
        Processes run in the database session
        Every user runs the same logic against the same data
```

**The benefit is not just "modernisation" — it is correctness.** In Forms, logic
lives on 60 workstations and can diverge between them. In APEX there is one
implementation.

The cost is that logic that *appears* to be client-side must be understood and
relocated, not mechanically converted.

## Principle 3: The mapping table

| Forms construct | APEX equivalent | Notes |
|-----------------|-----------------|-------|
| Canvas | **Page** | One canvas → one page, usually |
| Frame | Layout grid row | |
| Data block | **Interactive Report** (display) or **Form** (edit) | Depends on edit frequency |
| Item | Page item | Types map differently |
| View | Region | |
| LOV | Popup LOV / select list | |
| Trigger (WHEN-NEW-...) | **Page process** with condition | |
| WHEN-NEW-FORM | Page process: On Page Load | |
| POST-QUERY | Not needed — regions query directly | **Usually deleted, not converted** |
| PRE-INSERT / PRE-UPDATE | Process condition + validation | |
| POST-INSERT / POST-UPDATE | Process after the DML | |
| KEY-QUERY | Not needed — query is the region source | **Usually deleted** |
| WHEN-BUTTON-PRESSED | Process condition on that button | |
| Alert | `APEX_APPLICATION.ALERT` or a display item | |
| LOV | Popup LOV with filtering | |
| Savepoint / COMMIT | Process with a commit | |
| Menu stack | Navigation menu / breadcrumbs / tabs | |
| Post query | Collection population | |

**The most important row is POST-QUERY and KEY-QUERY: they are usually deleted,
not converted.** They exist to populate the client-side record group. With
server-side regions, the query already did that work. Converting them produces a
query that runs twice.

## Principle 4: POST-QUERY is the highest-volume deletion opportunity

In a 50-block Forms application, POST-QUERY triggers are numerous and often heavy:

```
Typical POST-QUERY:
  SELECT description INTO :v_label FROM lookup WHERE id = :id;

In Forms:   runs on every record navigated to. 50 records = 50 queries.
In APEX:    the join is in the region SQL. 50 records = 1 query.
```

```
Forms: 50 records × 1 query = 50 queries, in the client session
APEX:  1 query with a LEFT JOIN covering all 50
```

**Deleting POST-QUERY and moving the logic into the region SQL is often the
single biggest performance improvement in a Forms migration** — and it reduces
code rather than adding it.

## Principle 5: Trigger conversion is about intent, not syntax

A Forms trigger does something in response to an event. An APEX process does the
same thing on submit. The mapping is mechanical; deciding *which* process is not.

```sql
-- Forms: WHEN-NEW-RECORD-INSTANCE on ONTBL.ITEMWHEN
-- "when the item changes, default the description from the master"
```

```
APEX equivalent: a Dynamic Action on the ITEM page item
  Event:  Change
  True action: Set Value on DESCRIPTION page item from a SQL expression
```

```sql
-- Forms: PRE-INSERT on ONTBL
-- "validate before saving"
```

```
APEX equivalent: a Page Validation with condition On Page Load When Processing,
                PLUS a database constraint.
                The validation gives the message; the constraint guarantees it.
```

```sql
-- Forms: KEY-QUERY
-- "populate a record group from a query"
```

```
APEX equivalent: DELETE. The region query already does this.
```

The discipline: **for each trigger, ask what event it responds to, then find the
APEX mechanism for that event.** Most conversions are then obvious; the residue
is the genuinely Forms-specific behaviour.

## Principle 6: Validation moves to two places

Forms validation is spread across three levels. APEX has better homes for all
three.

```
Forms level 1 (LOV/when validated):  → APEX item LOV / page item default
Forms level 2 (when validate item):   → APEX page validation
Forms level 3 (NOT NULL constraint):  → Database NOT NULL constraint
```

**Level 3 is the only enforcement that cannot be bypassed.** A migration that
converts levels 1 and 2 to APEX validations but leaves level 3 unenforced has
made the system *less* safe, because it looks safe.

```
Best practice: keep the database constraints that always existed,
               add APEX validations for good messages,
               add item LOVs for usability.
```

## Principle 7: Savepoint semantics change

Forms had explicit savepoint control:

```
SAVEPOINT vs COMMIT vs ROLLBACK
Users saw "Do you want to save?" and controlled the transaction.
```

APEX has no equivalent — a page process commits at the end of the request.

**Implication**: users who relied on being able to abandon changes mid-screen lose
that. Two legitimate responses:

1. Accept it. Most users do not rely on it, and it removes a source of errors.
2. Provide a "cancel" that navigates away, accepting that entered changes are
   discarded only if not saved.

Do not attempt to replicate Forms savepoint semantics in APEX. It is not
possible and the attempt produces a worse design.

## Principle 8: LOVs need more care than they appear to

Forms LOVs are pervasive and users depend on their filtering behaviour.

| Forms LOV behaviour | APEX approach |
|---------------------|---------------|
| LOV with no filter (list of 500) | Popup LOV with `%` filter — better UX |
| LOV that executes a query | Popup LOV with `APEX_UTIL.prepare_query` |
| LOV return values to block items | Page process or Dynamic Action reading LOV return |
| LOV requiring other block values | Bind from the current record |

**The return-value case is where migrations get stuck.** In Forms, a LOV returns
values that are assigned directly to other items. In APEX this requires either a
Dynamic Action or a process:

```javascript
// Dynamic Action: Event "Selection" on the LOV item
// Set value on the dependent item from the LOV return value
```

## Principle 9: Navigation needs designing, not copying

Forms menus were a tree. APEX offers breadcrumbs, tabs, and a navigation menu.

```
Forms:  Inventory > Transactions > Stock Transfer > New
APEX:   Breadcrumbs: Home > Stock Transfer > New
        Plus a page-level "Cancel" action
```

**A Forms menu tree does not survive contact with APEX.** Users navigate
functionally, not hierarchically. Copying the tree produces a navigation model
nobody finds anything in.

Design navigation from how the work is actually done, then check the migration
against it.

## Principle 10: Sequence the migration so each stage is deliverable

```
Stage 1 (weeks 1–3):   Inventory + target data model
Stage 2 (weeks 4–6):   Low-risk read-only pages (reports, lookups)
Stage 3 (weeks 7–14):  Core CRUD pages
Stage 4 (weeks 15–18): Complex transactions with POST-QUERY and savepoints
Stage 5 (weeks 19–20): Parallel run and cutover
```

**Read-only pages first** because they carry almost no risk and give the team
APEX familiarity before the hard pages. **Complex transactions last** because they
are where the unknowns are.

The alternative — one big-bang conversion — puts all the unknowns in week 1 and
leaves no ability to course-correct.

## Principle 11: The functional gap analysis matters more than the mapping

During inventory, classify every Forms object:

```
1:1        Same behaviour, new implementation
Simplified APEX does it better; the Forms version is unnecessary
Redundant  Nobody uses it any more
New       APEX requirement with no Forms equivalent
```

**A migration that maps everything 1:1 preserves every old problem.** Some Forms
functionality exists because it was the only option available in 1998, not
because anyone needs it. This classification is where migration pays for itself.

```
Typical finding: 20-30% of Forms functionality is Redundant or Simplified
Those objects cost zero to migrate and deliver most of the risk reduction.
```

## Diagnostic Order

1. Query the Forms source — do not estimate from screen count.
2. Classify each object: 1:1, simplified, redundant, new.
3. Delete POST-QUERY and KEY-QUERY wherever the region SQL can absorb them.
4. Convert remaining triggers by event, not by syntax.
5. Move client-tier logic server-side.
6. Add database constraints alongside APEX validations.
7. Design navigation from the work, not the Forms menu tree.
8. Sequence read-only first, complex transactions last.

## Anti-Patterns

- Estimating migration size from screen count.
- Converting POST-QUERY into a process instead of deleting it.
- Leaving business logic in the client tier because it was there before.
- Enforcing validation only in APEX and dropping the database constraint.
- Attempting to replicate Forms savepoint semantics.
- Copying the Forms menu tree into APEX navigation.
- Migrating everything 1:1 and preserving every old problem.
- Big-bang cutover.

## Summary

The migration was decided by three findings: 340 triggers rather than 23 screens
set the real estimate, POST-QUERY triggers were largely deletable rather than
convertible because region SQL already does their work, and 20–30% of the
functionality could be dropped as redundant or simplified. What remained was
relocated from the client tier to the server, validated in two places, and
delivered read-only first so the team built familiarity before the hard pages.