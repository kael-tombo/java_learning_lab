# Lab 09: Security (SOD Remediation) — Exercises

## Exercise 1: Build the SOD Risk Matrix
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Enumerate duties and conflicts so SOD becomes enforceable.

### Steps
1. Define at least 6 duties with their EBS functions.
2. Define at least 5 conflicts with type, severity, and rationale.
3. Write the rationale for the approve/pay conflict.
4. Explain why the matrix is the artefact an auditor requests.

### Verification
- [ ] Six or more duties with EBS function names
- [ ] Five or more conflicts with written rationale
- [ ] Severity assigned to each conflict
- [ ] Explanation that "SOD conflicts" is unenforceable without enumeration

---

## Exercise 2: Detection at Assignment Level
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Write the detection query and contrast it with the wrong approach.

### Steps
1. Build a `user_duties` CTE joining users to duties.
2. Self-join on `user_id` with `duty_a < duty_b`.
3. Join the conflict matrix.
4. Write the responsibility-level query and confirm it returns nothing.

### Verification
- [ ] Detection query finds the planted conflicts
- [ ] Responsibility-level query returns zero
- [ ] `duty_code < duty_code` predicate present to avoid double counting
- [ ] Explanation of why the violation is a property of the assignment set

---

## Exercise 3: Risk Ranking
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Prioritise remediation by exposure, not by count.

### Steps
1. Attach an annual value to each duty held.
2. Score each user as severity weight × value.
3. Rank the users.
4. Identify the tier covering most of the exposure.

### Verification
- [ ] Severity weights stated (HIGH=3, MEDIUM=2, LOW=1)
- [ ] Ranking computed
- [ ] Tier identified with its share of total exposure

---

## Exercise 4: Targeted Remediation
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Remove only the conflicting duty, with an alternate path.

### Steps
1. Implement the remediation procedure with approver and reference required.
2. Log the action before executing the revocation.
3. Revoke only the conflicting responsibility.
4. Verify the user's other duties are untouched.

### Verification
- [ ] Procedure rejects a call with no approver
- [ ] Audit row written before the revocation
- [ ] Only the conflicting responsibility deleted
- [ ] Alternate path recorded

---

## Exercise 5: Over-Remediation Awareness
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Explain why revoking whole roles is worse than the violation.

### Steps
1. Identify how many of the 45 users need an alternate path.
2. Enumerate the workarounds that arise without one.
3. Explain why a shared login is a worse control than the original conflict.
4. Recommend the mitigation.

### Verification
- [ ] Workarounds listed with control-quality assessment
- [ ] Shared login explained as removing attribution entirely
- [ ] Mitigation recommended (alternate path per removed duty)

---

## Exercise 6: Preventive Control
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Block conflicting assignments at grant time.

### Steps
1. Implement the preventive check on responsibility assignment.
2. Attempt a conflicting grant; confirm it is blocked.
3. Confirm the error names both duties and the severity.
4. Discuss why a trigger on a standard table is upgrade-risk in production.

### Verification
- [ ] Conflicting grant rejected
- [ ] Error message names both duties
- [ ] HIGH severity blocked; MEDIUM routes to approval
- [ ] Production alternative identified (workflow or scheduled validation)

---

## Exercise 7: Exception Management
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Create time-bound exceptions with compensating controls.

### Steps
1. Create the exception table with `expires_on NOT NULL`.
2. Insert two exceptions with owner, compensating control, and expiry.
3. Set one to a past date and run the overdue query.
4. Confirm "indefinite" cannot be expressed.

### Verification
- [ ] Expiry is enforced by the schema
- [ ] Compensating control required
- [ ] Overdue query returns the expired exception
- [ ] "Indefinite" rejected by the schema

---

## Exercise 8: Hardening Sweep
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Close the password exposure and the dormant account risk.

### Steps
1. Scan every profile level for `FND_HIDE_DB_PASSWORD`.
2. Find a safe value at application level and an unsafe one at system level.
3. Fix the unsafe level and re-scan.
4. Identify dormant accounts with elevated access.

### Verification
- [ ] All levels scanned, not just application
- [ ] The more permissive value identified as the effective one
- [ ] Post-fix scan returns clean
- [ ] Dormant elevated accounts listed with days since login

---

## Exercise 9: Certification Workflow
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Build certification with attestation and outstanding-item reporting.

### Steps
1. Create the certification table with a constrained decision column.
2. Certify 80% of in-scope users.
3. Run the outstanding-items report.
4. Explain why an unsigned report proves nothing.

### Verification
- [ ] Certification records who and when
- [ ] Outstanding query identifies uncertified users
- [ ] Explanation given for the value of attestation over reporting

---

## Exercise 10: Evidence Pack
**Time**: 20 minutes | **Difficulty**: Beginner

### Objective
Assemble artefacts so the auditor needs no further queries.

### Steps
1. Build the evidence pack query.
2. Confirm every artefact exists in a table.
3. Identify anything that would require a bespoke query.
4. Add the missing artefact.

### Verification
- [ ] Evidence query returns counts for every artefact
- [ ] No artefact requires a new query at committee time
- [ ] Remediation and verification records both present