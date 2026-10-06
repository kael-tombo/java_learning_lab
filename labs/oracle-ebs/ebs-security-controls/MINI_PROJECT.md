# EBS Security Controls — Mini Project

## Goal
Design and prove a complete security control set for a small EBS application in
90 minutes.

## Requirements
- R1: An authentication flow diagram with named failure points.
- R2: A responsibility design showing which role grants what function.
- R3: Function security narrowing one function out of a broad responsibility.
- R4: Row-level security scoping users to their own branch via VPD/`FND_MOBS`.
- R5: A password policy with enforced complexity and 5-strike lockout.
- R6: An SOD conflict matrix with at least 3 mutually exclusive duties.
- R7: An SOD detection query that finds a planted conflict.
- R8: An audit trail and review report for the created users and accesses.

## Steps
1. Draw the sign-on flow and annotate each place it can fail.
2. Design two responsibilities and specify the functions each should expose.
3. Apply function security to remove one function from the broad role.
4. Add a branch column and VPD policy; verify two users see different rows.
5. Configure the password policy and prove lockout after the fifth failure.
6. Write the SOD conflict matrix mapping duties to conflicts.
7. Run the detection query against a deliberately planted violation.
8. Remediate the violation and produce the audit review report.

## Acceptance criteria
- Two users with the same responsibility see different data rows.
- The SOD query finds the planted conflict and names both roles.
- Lockout triggers at exactly the configured attempt count and recovers.
- The audit report lists who accessed what and when.

## Stretch
- Add encryption at rest for the sensitive tablespace and verify it.
- Break the flow deliberately to find one point your control did not cover.