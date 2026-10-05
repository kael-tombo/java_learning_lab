# AWS Security - Real World Project

## Project: Account-Wide Security Baseline with Continuous Verification

### Objective
Establish a security baseline across all accounts — IAM governance, encryption, perimeter
controls, detection coverage — and turn it into a continuously verified state rather than a
one-time project deliverable.

### Why This Is a Real Problem
Security baselines rot. They pass at audit time, and six months later a new account, a new
region, or an emergency change has quietly undone them. This project's real output is the
detection loop, not the document.

### Architecture Overview
```
  AWS Organizations (SCP guardrails at the root)
        │
        ├── member accounts (prod / staging / dev / sandbox)
        │      ├── IAM: roles only, no long-lived keys, boundaries on deploy roles
        │      ├── KMS: customer-managed keys, per-environment, key policy denies admin
        │      └── Config rules: continuous compliance evaluation
        │
        └── Security Hub / GuardDuty / central CloudTrail (org-wide)
                     └── event bus ──▶ detection rules ──▶ response runbooks
```

### Phase 1: Assess the Current State (Week 1)
1. Run the policy overprivilege checker on every account; produce a ranked report
2. Inventory long-lived IAM users and access keys — the highest-risk finding in most estates
3. Check unencrypted resources: EBS volumes, S3 buckets, RDS instances, snapshots, queues
4. Check public exposure: S3 bucket policies, security groups with `0.0.0.0/0`, open ports
5. Check logging coverage: CloudTrail in every region, VPC Flow Logs, S3 access logs

### Phase 2: Set Organization Guardrails (Week 2)
1. Service Control Policies at the root: deny by default the things you never want
   - No `iam:*` without a condition on the organization or account ID
   - No resource policies granting public access
   - No disabling of CloudTrail, Config, or GuardDuty
2. Explicit Deny beats prevention: a guardrail that blocks is better than one that audits
3. Apply to all accounts, then use `aws:RequestTag` conditions to let only designated roles
   create the approved resource shapes
4. Test each SCP by attempting the forbidden action — an untested guardrail is a guess

### Phase 3: Eliminate Long-Lived Credentials (Week 3)
1. Inventory every access key and every `aws_access_key_id` in code, config, and CI
2. Replace with IAM roles: instance profiles, task roles, CI OIDC federation
3. Where keys are unavoidable, rotate on a schedule and store them in Secrets Manager
4. **Target: zero static keys in application code.** That is the measurable goal
5. Alert on any new long-lived key creation — the number must only go down

### Phase 4: Encryption Everywhere (Week 4)
1. Customer-managed KMS keys per environment; key policy explicitly denies account admins
   from `kms:Decrypt` without a ticket-based condition
2. Envelope encryption by default for EBS, S3, RDS, SQS, SNS
3. CloudTrail log validation enabled, with logs written to a separate, tightly-scoped
   account — an attacker who can edit the audit log has no audit log
4. Verify decrypt works for the legitimate path, and that the key policy genuinely blocks
   the illegitimate one

### Phase 5: Make It Continuous (Week 5+)
1. Config rules per baseline control: encrypted volumes, buckets not public, no open SGs,
   CloudTrail on everywhere
2. Non-compliance events routed to a central bus, then to a ticket — not a page, unless the
   control is critical
3. Detections: guard-duty findings, CloudTrail anomalies, IAM changes, key-policy changes,
   public-bucket creation
4. Monthly access review generated from CloudTrail (who did what to which resource)
5. Quarterly: re-run the phase 1 assessment and diff against the baseline — the drift report
   is the deliverable that proves the programme works

### Deliverables
1. Baseline assessment report with ranked findings
2. SCP guardrails at the organization root, each one tested
3. Zero-static-keys migration plan with progress reporting
4. Continuous compliance rules, detection set, access reviews, and the drift report

### Success Criteria
- Long-lived access keys reduced to zero in production
- Every account and region has CloudTrail, Config, and GuardDuty enabled and verified
- Every SCP tested by a successful blocked attempt
- No unencrypted resource older than one month, measured by Config

### Sourced field notes (fetched Oct 2026 — verify before citing)
- AWS IAM best practices —
  https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
  Use for: the maintained guidance on using roles instead of long-lived credentials, scoping
  policies, and reviewing access. Cite the current recommendations rather than paraphrasing
  them from memory.
- AWS KMS encryption concepts —
  https://docs.aws.amazon.com/kms/latest/developerguide/encryption-concepts.html
  Use for: envelope encryption and the key-policy mechanics used to separate key administration
  from key usage. Verify the current guidance on key rotation and grant behaviour.

### Estimated Time
8-10 weeks part-time