# JDBC and JPA — Mini Project

## Brief
Six focused exercises on JDBC DriverManager and DataSource access with JPA EntityManager mapping, each ending with a visible artifact and a one-line explanation.

## Setup
Prepare seed rows for products and stock, sized so the output fits on one screen.

## Exercises
1. Exercise on DriverManager query reading product rows with closed resources: trace it and record what changes in the output.
2. Exercise on DataSource sketch routing through a pool: draft it, then note the one surprise worth remembering.
3. Exercise on parameterized statement binding a product id safely: load it and capture the check query beside it.
4. Exercise on Product entity mapping columns to fields: run it, then explain the result to a reviewer aloud.
5. Exercise on EntityManager persist-and-find round trip: shape it and file the script where the next step finds it.
6. Exercise on transaction-boundary note around a two-write edit: assemble it while keeping every statement re-runnable.

## Reference snippet
```text
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement("SELECT id FROM products WHERE id = ?")) {
  ps.setInt(1, 7);
}
```

## Acceptance
- All six exercises finish with artifacts a reviewer can open.
- The write-up quotes the rule that DriverManager opens direct connections while DataSource enables pooling.
- A second run reproduces identical row counts.
- Each exercise names its own failure signal.

## Reflection
- Which step surprised you, and which fact explains it?
- What access shortcut would you forbid on a shared database?
- The reflection stays inside the project folder beside the scripts.

## Setup checklist
- Shared databases stay untouched because a scratch schema is reserved here.
- Seed rows for products and stock loaded and counted.
- Anything surprising enough to quote goes into the open notes file.
- Before editing anything, the rollback or re-seed path is confirmed.

## Hand-off
- Tag the scripts folder when done, so the next lab starts without re-reading all files.
- The notes file changes hands with the exercises, and the surprises survive with it.
- The checklist gets its done mark after a peer reruns every script, edits free.

