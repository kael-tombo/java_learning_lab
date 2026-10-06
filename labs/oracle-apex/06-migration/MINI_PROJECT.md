# Lab 06: APEX Migration — Mini Project

## Goal
Convert a small Forms application — 3 canvases, 6 blocks, 20 triggers — into
APEX in 90 minutes, classifying every object first.

## Requirements
- R1: Inventory of the Forms application produced from its source.
- R2: Classification of every object as 1:1, simplified, redundant, or new.
- R3: At least two POST-QUERY triggers deleted via region SQL joins.
- R4: A KEY-QUERY trigger deleted.
- R5: A WHEN-NEW-ITEM-INSTANT converted to a Dynamic Action.
- R6: A PRE-INSERT validation converted to a constraint plus an APEX validation.
- R7: A return-value LOV handled with a Dynamic Action.
- R8: Before/after constraint coverage comparison.

## Steps
1. Inventory the Forms source; count objects by trigger type.
2. Classify each object, confirming redundant ones with a user.
3. Build the APEX data model and confirm constraints are unchanged.
4. Build the stock list page; absorb two POST-QUERY lookups into its joins.
5. Verify the list page needs no POST-QUERY equivalent.
6. Build the stock form page with a WHEN-NEW-ITEM Dynamic Action.
7. Add the quantity validation as both a constraint and a page validation.
8. Build a popup LOV with a dependent item via Dynamic Action.
9. Confirm level-3 constraint coverage matches the Forms original.
10. Produce the mapping table and the effort estimate.

## Acceptance criteria
- Every Forms object is classified with a justification.
- The two POST-QUERY objects are deleted, not converted.
- The Dynamic Action defaults the price only on value change, not on refresh.
- The quantity rule is enforced by the database constraint.
- The dependent item populates from the LOV selection.
- Constraint coverage before and after is identical.

## Stretch
- Identify one object as REDUNDANT and delete it, recording the saving.
- Compare the list-page query count before and after deleting POST-QUERY.