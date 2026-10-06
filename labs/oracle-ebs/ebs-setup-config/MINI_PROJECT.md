# EBS Setup and Configuration — Mini Project

## Goal
Take a bare instance to a working configuration with multi-org, flexfields,
sequences, and auditing in 90 minutes.

## Requirements
- R1: An installation type decision document with a stated requirement.
- R2: A pre-install checklist with explanations for each check.
- R3: One profile option demonstrated at all four precedence levels.
- R4: MOAC configured for 2 operating units with an access test.
- R5: A descriptive flexfield with a validated value set.
- R6: A key flexfield with a combination rule and at least 3 valid combos.
- R7: A document sequence used by a real business document.
- R8: Table auditing enabled with a verified change trail.

## Steps
1. Write the requirement and select the installation type.
2. Run through the pre-install checklist, explaining each item's purpose.
3. Set a profile option at system, application, responsibility, and user level;
   record the observed value at each level.
4. Create 2 operating units and assign MOAC responsibilities; test access.
5. Build a descriptive flexfield on a custom table with a value set.
6. Build a key flexfield with a combination rule; verify invalids are rejected.
7. Define a document sequence and attach it to the business document.
8. Enable auditing, change a row, and confirm both values are recorded.

## Acceptance criteria
- The profile precedence demonstration shows four different values.
- MOAC correctly restricts each operating unit's visibility.
- An invalid key flexfield combination is rejected, not silently stored.
- The audit trail shows who changed what, when, and from which value.

## Stretch
- Add a flexfield segment whose validation depends on another segment.
- Demonstrate a configuration change's effect on an existing record.