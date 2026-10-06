# EBS Setup and Configuration — Vision

## Where this lab takes you
From a fresh install to a configured instance: understanding what setup data
controls behaviour, and getting it right before the business starts typing.

## The Arc
1. **Install** — installation types and what each one enables.
2. **Rapid Install** — the accelerated path and its prerequisites.
3. **Pre-install checks** — the checks that prevent a failed install.
4. **System administrator** — the responsibility that owns configuration.
5. **Profiles** — profile options as runtime behaviour switches.
6. **MOAC** — multi-org access control and why it changes everything.
7. **Flexfields** — descriptive, key, and segment flexfields.
8. **Sequences and audit** — document numbering and change tracking.

## Milestones (checkable)
- [ ] M1: Choose an installation type for a stated requirement and justify it.
- [ ] M2: Run or simulate the pre-install checklist and explain each failure.
- [ ] M3: Set a profile option at system, application, responsibility, and user
      level and explain the precedence.
- [ ] M4: Configure MOAC for two operating units and test access.
- [ ] M5: Build a descriptive flexfield with validation.
- [ ] M6: Build a key flexfield with a valid combination rule.
- [ ] M7: Define a document sequence and show where it is used.
- [ ] M8: Enable auditing on a table and verify the audit trail records changes.

## Anti-Goals
- Setting profile options at the system level by default.
- Enabling multi-org without understanding what it restricts.
- Leaving a key flexfield without a combination rule.
- Treating setup data as configuration you can redo cheaply later.

## The one-sentence thesis
Setup data is the cheapest thing to get right and the most expensive to change —
decide flexfield structure and multi-org scope before users do, not after.