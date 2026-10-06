# EBS Architecture — Mini Project

## Goal
Produce a complete, annotated architecture map of an EBS R12.2 instance in
90 minutes.

## Requirements
- R1: A tier diagram covering desktop, application, and database tiers.
- R2: Component inventory — OHS, Forms server, OAF, concurrent manager, admin.
- R3: A request trace from a user action through to the database and back.
- R4: File-system layout for `APPL_TOP`, `DB_TOP`, and `INSTALL_BASE`.
- R5: Public API list with at least 5 documented examples and their signature.
- R6: Concurrent processing flow showing request → queue → worker → log.
- R7: Multi-node topology showing shared `APPL_TOP` and per-node services.
- R8: An EBR (edition-based redefinition) worked example with the savepoint.

## Steps
1. Draw the three tiers and label each component that runs in them.
2. Pick a simple transaction (e.g. create a supplier) and trace it end to end.
3. Note where each step executes — app tier process or database session.
4. Map the file-system roots and what lives in each.
5. List the public APIs you would use instead of direct table writes.
6. Write out the concurrent request lifecycle with the key tables involved.
7. Sketch a 3-node cluster with services distributed and `APPL_TOP` on NFS.
8. Walk an EBR example showing prepare, run, and savepoint.

## Acceptance criteria
- Every component in the diagram is either app-tier, DB-tier, or client-side.
- The request trace names the specific tables touched at each step.
- The API list includes at least one update/insert API, not just queries.
- The EBR example shows why the savepoint matters for an upgrade.

## Stretch
- Add the technology stack versions for the R12.2 release you are targeting.
- Draw what changes in the map for a Fusion Cloud instance.