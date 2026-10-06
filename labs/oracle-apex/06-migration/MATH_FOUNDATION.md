# Lab 06: APEX Migration — Math Foundation

## 1. Why Screen Count Is the Wrong Estimate

The application as described: "20+ canvases, 50+ data blocks".

### The actual inventory

| Object type | Count |
|--------------|-------|
| Canvases | 23 |
| Data blocks | 57 |
| **Triggers** | **340** |
| LOVs | 48 |
| Alerts | 31 |
| Menus/stacks | 12 |
| Form procedures | 19 |
| Window triggers | 8 |
| **Total objects** | **538** |

### Two estimates

```
Estimate from screens:
  23 canvases × 2 days each = 46 days

Estimate from objects:
  340 triggers × 0.5 day        = 170 days
   48 LOVs × 0.25 day           =  12 days
   31 alerts × 0.1 day          =   3 days
  Navigation design               =   5 days
  Data model validation           =   8 days
  Testing and cutover             =  15 days
                                   --------
                                   213 days
```

```
Underestimate from screen count: 213 / 46 = 4.6x
```

**Anyone estimating from what the client describes will be out by 4–5×.** The
inventory must come from querying the source.

## 2. Trigger Distribution Decides the Effort

| Trigger type | Count | Migration mechanism | Unit effort |
|--------------|-------|---------------------|-------------|
| POST-QUERY | 118 | **Delete** (region SQL) | 0.25 day each |
| KEY-QUERY | 47 | **Delete** (region SQL) | 0.1 day each |
| WHEN-NEW-ITEM | 71 | Dynamic Action | 0.5 day each |
| WHEN-BUTTON | 66 | Process + condition | 0.4 day each |
| PRE-DML | 38 | Validation + constraint | 0.5 day each |
| WHEN-NEW-RECORD | 38 | Computation + process | 0.5 day each |
| **Total** | **378** | | |

### Effort by mechanism

```
Deletions:      165 × 0.2 day  =  33 days
Conversions:    213 × 0.46 day =  98 days
                                    ------
                                    131 days of trigger work
```

**43% of the trigger effort is deletion.** That reframes the project from "convert
340 triggers" to "delete 165, convert 213" — a materially different proposition,
and one that makes the estimate credible.

## 3. POST-QUERY Deletion Saves Real Work

```
Typical POST-QUERY: one lookup query per record

Forms, user viewing a block of 50 records:
  50 records × 1 query = 50 queries in the client session
  At ~4 ms each (client→server round trip): 200 ms of pure waiting

APEX, same 50 records:
  1 query with a LEFT JOIN = 1 query
  At ~15 ms: 15 ms
```

```
Round trips: 50 → 1        (50x fewer)
Latency:     200 ms → 15 ms
```

Across a workday with 200 block navigations:

```
Forms: 200 × 200 ms = 40 seconds/day of pure waiting
APEX:  200 × 15 ms  =  3 seconds/day
```

And this is only what is **visible** to the user. POST-QUERY queries also consume
database resources, and in Forms they do so from 60 concurrent client sessions.

## 4. Functional Classification — The Payoff

| Class | Count | Share | Effort | Delivered value |
|-------|-------|-------|--------|-----------------|
| 1:1 | 186 | 35% | ~90 days | Feature parity |
| SIMPLIFIED | 84 | 16% | ~12 days | Better UX, same function |
| **REDUNDANT** | **197** | **37%** | **~8 days** | **Risk removed** |
| NEW | 61 | 12% | ~30 days | Gap filled |

### What REDUNDANT gives you

```
197 objects cost ~8 days total (mostly inventory and confirmation)
They deliver:  zero new functionality
They remove:    maintenance, support load, and upgrade risk

37% of the Forms application disappears for 4% of the total effort.
```

**This is where a migration pays for itself.** A project that maps everything
1:1 spends 90 days preserving functionality nobody uses and every old problem
with it.

## 5. Validation Migration — Coverage and Risk

```
Forms validation levels in the source:
  Level 1 (item LOV / when validated):     62 objects
  Level 2 (when validate item):            118 objects
  Level 3 (database NOT NULL / check):     38 objects
```

### Bad migration: APEX validations only

```
Level 2 → APEX validation:  118 objects, 118 covered
Level 3 → dropped as "the database already has it, APEX checks it":  38 UNENFORCED
Level 1 → item LOVs:        62 covered

Enforcement in the database:  38 of 156 = 24%
```

**The system now looks more validated than before while enforcing less.** A
direct SQL insert — from a batch job, an interface, or an API — bypasses every
APEX validation.

### Good migration: all three homes

```
Level 3 → database constraint:  38 objects, unchanged, still enforced
Level 2 → APEX validation:     118 objects, now with better messages
Level 1 → item LOV / default:  62 objects, better usability

Enforcement in the database:  38 of 156 = 24% (same as before, by design)
Plus 180 objects now validated with good messages at the point of entry
```

**The insight**: level 3 coverage should be *identical* before and after. What
improves is levels 1 and 2. If level 3 drops, the migration made things worse.

## 6. Savepoint Semantics — What Is Lost

```
Forms transaction options per form:
  Savepoint          — commit within a form, continue editing
  Commit             — save
  Rollback           — discard
  Save and Close     — save, exit
  Cancel             — discard, exit

APEX equivalents:
  Save and Close     — save process + branch
  Cancel             — branch away (nothing was submitted, nothing to discard)
  Commit             — automatic at request end
  Savepoint          — NO EQUIVALENT
```

### How often savepoints mattered

```
Forms forms using savepoints:         8 of 23 canvases (35%)
Of those, users relying on it:        ~3 canvases (conservative estimate)
User-hours lost per week if removed:  ~2 hours
```

**Low cost, and unreplicable.** Two hours a week against 213 days of migration
effort is not worth designing a workaround for. The correct answer is to accept
the loss and tell users.

```
Attempting to replicate: 20+ days of design and permanent complexity
Accepting the loss:      a 5-minute user briefing
```

## 7. LOV Conversion Effort

| Forms LOV type | Count | APEX approach | Unit effort |
|----------------|-------|---------------|-------------|
| Static list | 9 | Select list | 0.05 day |
| Simple query | 21 | Popup LOV | 0.1 day |
| Filtered query | 11 | Popup LOV with depends-on | 0.2 day |
| **Return values to other items** | **7** | **Dynamic Action** | **0.75 day** |

```
Simple LOVs:  41 × 0.1 day  =  4 days
Return-value:  7 × 0.75 day =  5 days
                              -------
                               9 days, half of it in 17% of the LOVs
```

**The return-value LOVs are 65% of the effort in 17% of the objects.** They are
where the migration gets stuck because Forms assigns return values automatically
and APEX does not.

## 8. Navigation Redesign

```
Forms menu stack depth: 4 levels
Nodes:                  12 stack entries, 31 menu items

Copy the tree to APEX:
  Breadcrumbs mirroring 4 levels: 4 levels is above the comfortable limit
  Breadcrumbs beyond 3-4 levels are ignored by users
  Menu tree with no search:        finding anything needs memorising
```

```
Redesign from the work:
  6 top-level pages with clear names
  Breadcrumbs max 3 levels
  Navigation menu of 6 items, not 31
```

```
Usability change: users find things faster
Effort: 5 days versus 1 day for copying
```

**The extra 4 days is the entire reason the navigation redesign exists.**

## 9. Staging Plan

| Stage | Duration | Content | Risk |
|-------|----------|---------|------|
| 1: Inventory + model | 3 weeks | Classify all 538 objects; validate schema | None |
| 2: Read-only | 3 weeks | 31 reports + 12 lookups | Very low |
| 3: Core CRUD | 8 weeks | 57 blocks → forms + IR | Low |
| 4: Complex transactions | 4 weeks | 7 savepoint canvases, return-value LOVs | Medium |
| 5: Parallel run + cutover | 2 weeks | Comparison, discrepancy resolution | Controlled |
| **Total** | **20 weeks** | | |

### Why read-only first

```
Stage 2 delivers value immediately (31 reports live in 3 weeks)
Team learns APEX on low-risk pages
Bugs found in stage 2 do not corrupt data
If the programme stops, stage 2 is still worth having
```

```
Big-bang alternative: 20 weeks of work, nothing delivered until week 20,
and the first data corruption risk in week 4.
```

## 10. Parallel Run Discrepancy Expectations

```
Comparisons per week during parallel run: ~200 business transactions
Parallel run duration: 2 weeks
Total comparisons: ~400

Expected discrepancy rate by category:
  Rounding / display formatting:    6-10%   → cosmetic, verify
  Timing / sequence differences:     3-5%    → investigate
  Missing default values:            2-3%    → real bug
  Wrong validation behaviour:        1-2%    → real bug
  Wrong data written:                <0.5%   → stop-the-line
```

```
Cosmetic discrepancies expected:      400 × 0.08 = 32
Real bugs expected:                   400 × 0.01 = 4
Stop-the-line cases:                 400 × 0.005 = 2
```

**The gate is not zero discrepancies.** It is zero *stop-the-line* cases and zero
"wrong data written". A requirement of zero total discrepancies produces a
parallel run that never ends, because rounding differences are not bugs.

## 11. Effort Summary

| Category | Objects | Effort (days) | Share |
|----------|---------|---------------|-------|
| Trigger deletions | 165 | 33 | 12% |
| Trigger conversions | 213 | 98 | 36% |
| LOVs | 48 | 9 | 3% |
| Alerts | 31 | 3 | 1% |
| Data model | 57 blocks | 25 | 9% |
| Pages / regions | 23 canvases | 30 | 11% |
| Navigation redesign | — | 5 | 2% |
| Testing and cutover | — | 40 | 15% |
| Stage 1 inventory | 538 | 25 | 9% |
| Contingency (12%) | — | 33 | — |
| **Total** | | **~301 days** | |

```
At 3 developers:  ~100 calendar weeks of effort
Practical:         20 weeks with 4-5 people
```

**The contingency is 12% because migration unknowns are real.** A migration
without contingency will overrun, and the overrun will be blamed on the
developers rather than the estimate.

## 12. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Undocumented Forms logic found late | High | High | Source-query inventory, not interviews |
| POST-QUERY hiding business rules | Medium | High | Read each one before deleting |
| Return-value LOV behaviour differs | Medium | Medium | Convert early, test with real users |
| Parallel run shows systematic divergence | Low | Critical | Gate cutover on it |
| Users miss savepoint behaviour | High | Low | Brief users; accept the loss |
| Data model needs restructuring | Medium | High | Validate in stage 1, before building |
| Redundant objects turn out to be used | Low | Medium | Confirm with real users before deleting |