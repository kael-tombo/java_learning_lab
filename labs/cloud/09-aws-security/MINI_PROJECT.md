# AWS Security - Mini Project

## Project: An IAM Model for a Three-Tier Application

### Objective
Build the complete IAM model for an ALB → app → database application — roles, policies,
permission boundaries, session-duration limits — and prove each role can only do its job.

### Requirements
1. Four roles: EC2 instance profile, CI/CD deploy role, break-glass admin, read-only auditor
2. Resource-based policies only where an identity policy cannot express the grant
3. `SessionPolicyEngine` implementing IAM evaluation order in Java
4. Tests asserting that each role can and cannot perform specific actions
5. `OversizedPolicyChecker` that flags `Action: "*"` with `Resource: "*"`

### Steps

**Step 1: Write the permission table, not the policies**
```
 Role            Allow                                    Explicitly Deny
 app-ec2         s3:GetObject on bucket/prefix only       s3:DeleteBucket*, kms:Decrypt other keys
 ci-deploy       cloudformation:*, ecr:*, ecs:*, iam:PassRole  iam:*, kms:*, s3:DeleteObject
 audit-read      *:Describe*, *:List*, Get*, cloudtrail:Lookup*  nothing (safe by nature)
 break-glass     everything, 1 hour, MFA required, logged  s3:DeleteBucket, account:*
```
Policies written from a permission table produce tighter documents than policies written
from memory. Write the table, then the JSON.

**Step 2: Scope everything**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "ReadOnlyFromAppPrefix",
    "Effect": "Allow",
    "Action": ["s3:GetObject"],
    "Resource": "arn:aws:s3:::my-app-bucket/config/*",
    "Condition": {
      "StringEquals": { "s3:ExistingObjectTag/classification": "public" },
      "Bool": { "aws:SecureTransport": "true" }
    }
  }]
}
```
Two things to notice: the prefix scope stops the policy reading other buckets, and
`aws:SecureTransport` refuses plain HTTP. Conditions are where a scoped policy becomes a
safe one.

**Step 3: Evaluation order — implement it, because it surprises people**
```java
enum Decision { ALLOW, IMPLICIT_DENY, EXPLICIT_DENY }

Decision evaluate(Request req, IdentityPolicy identity, ResourcePolicies resources) {
    for (var resource : resources.matching(req.resourceArn()))   // identity first? no:
        if (explicitDeny(req, resource)) return EXPLICIT_DENY;    // 1. any explicit deny wins

    if (hasIdentityAllow(req, identity)) return ALLOW;            // 2. identity or resource allow

    for (var boundary : boundaries(req))
        if (!boundaryAllows(req)) return IMPLICIT_DENY;           // 3. boundaries cap it

    for (var scp : orgPolicies())
        if (!scpAllows(req)) return IMPLICIT_DENY;                // 4. SCPs

    for (var session : sessionPolicies())
        if (!sessionAllows(req)) return IMPLICIT_DENY;             // 5. session policies

    return IMPLICIT_DENY;
}
```
Order: **explicit deny anywhere → then any allow → then boundaries/SCP/session narrowing**.
The consequence people miss: an explicit `Deny` in a resource policy blocks an identity
allow, and a permission boundary can remove access that an allow granted. Test both.

**Step 4: Break-glass with a real process**
```java
record BreakGlassRequest(String requester, String incidentId, Duration duration, String justification) {}
```
1. A separate role, not a policy attached to an existing identity
2. Requires MFA and a second approver
3. Max 1 hour session duration — hard-coded in the role, not requested at runtime
4. Every use alerted to a security channel and written to an audit log someone reads
5. Test: attempt to use it without MFA, and attempt to extend the session — both must fail

**Step 5: Overprivilege checker**
```java
List<String> findOverprivilege(String policyJson) {
    var doc = JsonNodeFactory.instance.objectNode();
    // flag: Action "*" AND Resource "*" with no Condition
    // flag: Action containing "iam:*", "kms:*", "organizations:*"
    // flag: any Allow on Delete* or Put* without a condition on the resource tag
}
```
Run it across every policy in the account and produce a ranked list. Most organisations find
their own incident leftovers on it.

**Step 6: Test each role against the table**
```java
@Test
void appRoleCannotDeleteAnything() {
    var engine = engineWith(appRole, resourcePolicies);
    assertThat(engine.evaluate(deleteObjectRequest())).isEqualTo(IMPLICIT_DENY);
    assertThat(engine.evaluate(deleteBucketRequest())).isEqualTo(EXPLICIT_DENY);
}
```

### Deliverables
1. Permission table plus four roles with scoped policies
2. `SessionPolicyEngine` implementing evaluation order, with tests for each precedence rule
3. Break-glass role with MFA, approval, hard duration cap, and alerting
4. `OversizedPolicyChecker` results across all account policies

### Extension (CHALLENGE)
Add permission boundaries to the CI/CD role so it can never modify its own IAM permissions,
then show that attempting to grant itself an action fails even with a valid identity policy.

### Estimated Time
3 hours