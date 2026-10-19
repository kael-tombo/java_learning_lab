# PL SQL Advanced — Mini Project

## Brief
Six focused exercises on PL/SQL packages, bulk binds, and autonomous-transaction logging, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for a_orders and a_audit, sized so the engine-hop counts fit on one screen.

## Exercises
1. Exercise on order package specification grouping three operations: assemble it, then explain the result to a reviewer aloud.
2. Exercise on bulk-collect fetch replacing a slow row loop: compose it and file the script where the next step finds it.
3. Exercise on FORALL insert pushing the collected orders at once: frame it while keeping every statement re-runnable.
4. Exercise on autonomous audit procedure logging even on rollback: trace it and record what changes in the output.
5. Exercise on context-switch audit counting engine hops before and after: draft it, then note the one surprise worth remembering.
6. Exercise on exception-propagation note across the package boundary: load it and capture the check query beside it.

## Reference snippet
```sql
DECLARE
  v_name VARCHAR2(100);
BEGIN
  SELECT name INTO v_name
  FROM a_orders
  WHERE id = 1;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    v_name := 'none';
END;
/
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the rule that packages bundle related procedures under one specification.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What package shortcut would you forbid on a shared database?
- The reflection stays inside the project folder beside the scripts.

## Setup checklist
- Shared databases stay untouched because a scratch schema is reserved here.
- Seed rows for a_orders and a_audit loaded and counted.
- Keep a notes file open; quote-worthy surprises land there.
- Before editing anything, the rollback or re-seed path is confirmed.

## Hand-off
- A tagged scripts folder lets the next lab skip re-reading every file.
- The notes file changes hands with the exercises, and the surprises survive with it.
- Peer reruns all scripts, no edits, then the checklist can be marked done.

