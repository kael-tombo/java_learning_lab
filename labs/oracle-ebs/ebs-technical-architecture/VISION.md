# EBS Technical Architecture — Vision

## Where this lab takes you
From table structure to a production custom concurrent program — the internal
mechanics that decide whether your code survives the next patch.

## The Arc
1. **Table structure** — keys, `F`/`V`/`S` layers, `_ALL` vs `_B`.
2. **Key views** — which view to query and why it is safer than the table.
3. **API codes** — the public contract: what exists and what is not supported.
4. **Concurrent programs** — the wrapper, its parameters, and its logs.
5. **Forms personalization** — extending without modifying.
6. **OA Framework** — MVC in the web tier and how the pieces bind.
7. **BC4J** — the Java layer behind OAF.
8. **MDS and JTT** — metadata and the Java transaction that ties it together.

## Milestones (checkable)
- [ ] M1: For a given table, explain the `_ALL`, `_F`, `_V`, and `_S` layers.
- [ ] M2: Choose correctly between querying a table and querying a key view.
- [ ] M3: Find the public API for an operation and cite its signature.
- [ ] M4: Build a custom concurrent program that registers and runs.
- [ ] M5: Personalise a form without modifying standard objects.
- [ ] M6: Describe an OAF page's MVC components and their bindings.
- [ ] M7: Explain where BC4J sits relative to the database.
- [ ] M8: Diagnose a failing custom program from its log structure.

## Anti-Goals
- Writing to `_ALL` tables directly from custom code.
- Using an `_S` (summary) view for anything except heavy aggregation.
- Assuming an internal procedure is a supported API.
- Modifying a standard form when personalization would do.

## The one-sentence thesis
EBS gives you a supported surface and an unsupported one — knowing which side of
that line you are on is the whole technical skill.