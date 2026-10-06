# EBS Customization and Extension — Mini Project

## Goal
Deliver one requirement three different ways and compare their upgrade cost, in
90 minutes.

## Requirements
- R1: A written requirement — "approvers must see the invoice image inline".
- R2: A configuration solution (or a documented reason it is not possible).
- R3: A personalization solution, plus how to revert it completely.
- R4: An extension solution using a public API or AME/workflow.
- R5: A modification option, with its upgrade cost stated explicitly.
- R6: A customization decision record comparing all four options.
- R7: A regression check list that would run on every future upgrade.
- R8: A naming and versioning standard for your custom objects.

## Steps
1. Write the requirement and its acceptance criteria.
2. Check the profile option catalog; record what exists.
3. Build the personalization; verify it, then revert it and confirm clean.
4. Build the extension via a public API or AME rule; test escalation.
5. Sketch the modification and list exactly what an upgrade would force you to do.
6. Compare footprint, reversibility, and upgrade cost across all options.
7. Choose one and write the decision record with the reasoning.
8. Write the regression checklist that future upgrades will run.

## Acceptance criteria
- All four options are considered with real evidence, not assertion.
- The chosen solution is the smallest one that fully meets the requirement.
- The decision record names an owner and a review date.
- The regression checklist is specific enough to run without the author.

## Stretch
- Add a localization variant of the requirement and explain its separate
  maintenance path.
- Prototype an XML Gateway integration instead of a custom interface table.