# Lab 06: APEX Migration — Vision

## Where this lab takes you
From "20 screens" to an accurate estimate and a staged delivery — knowing that
the migration is 340 triggers, that 165 of them are deleted rather than
converted, and that 37% of the application can disappear.

## The Arc
1. **Inventory** — query the source, never estimate from screen count.
2. **Classify** — 1:1, simplified, redundant, new; and delete accordingly.
3. **Relocate** — client-tier logic moves server-side.
4. **Delete** — POST-QUERY and KEY-QUERY absorbed into region SQL.
5. **Convert** — remaining triggers mapped by event, not by syntax.
6. **Validate** — database constraints plus APEX validations plus LOVs.
7. **Navigate** — redesign from the work, not the menu tree.
8. **Stage** — read-only first, complex transactions last.

## Milestones (checkable)
- [ ] M1: Produce the inventory by querying Forms source.
- [ ] M2: Classify all objects and identify the redundant percentage.
- [ ] M3: Delete a POST-QUERY by absorbing its logic into a region join.
- [ ] M4: Convert a WHEN-NEW-ITEM-INSTANT to a Dynamic Action.
- [ ] M5: Convert PRE-UPDATE validation to a constraint plus APEX validation.
- [ ] M6: Handle a return-value LOV with a Dynamic Action.
- [ ] M7: Confirm level-3 constraint coverage is unchanged after migration.
- [ ] M8: Design navigation from user workflow and stage the cutover.

## Anti-Goals
- Estimating from screen count (4.6× under).
- Converting POST-QUERY instead of deleting it.
- Leaving business logic in the client tier.
- Dropping database constraints because APEX validates.
- Replicating savepoint semantics.
- Copying the Forms menu tree.
- Migrating everything 1:1.
- Big-bang cutover.

## The one-sentence thesis
A Forms migration is an inventory and deletion exercise wearing a build
exercise's clothes — 340 triggers, of which 165 should disappear.