# QUIZ — APEX Administration

## 1. Instance vs workspace vs application admin: one-line split?
<details><summary>Answer</summary>Instance: engine-wide posture/resources/patching. Workspace: tenant schemas/people/quota. Application: auth/pages/REST (labs 03/05).</details>

## 2. `ADD_WORKSPACE` binds what three things?
<details><summary>Answer</summary>Workspace name, primary parsing schema, additional schemas — tenant + data access in one call.</details>

## 3. Developer account gets schema-owner/DBA. Verdict?
<details><summary>Answer</summary>Never — workspace roles grant building rights; table access flows via parsing schema. DBA to a developer is blast-radius malpractice.</details>

## 4. Instance password policy vs app-level checks: relationship?
<details><summary>Answer</summary>Instance values are the floor (internal/local accounts); lab-03 app logic adds per-app rules on top. Neither replaces the other.</details>

## 5. Outbound call fails from APEX but curl works. First suspects?
<details><summary>Answer</summary>ORDS host allow-list, then DB network ACL — two independent gates, both must permit. Check in that order.</details>

## 6. Activity log's three triage questions?
<details><summary>Answer</summary>What's slow (elapsed ranking), what's broken (error spikes), what's hot (view concentration).</details>

## 7. ORDS queue grows, DB idle. Diagnosis?
<details><summary>Answer</summary>Middle-tier pool exhaustion — scale ORDS, not the database. Flat DB load is the tell.</details>

## 8. Restore order, and why that order?
<details><summary>Answer</summary>Workspace → schema objects/data → app import → ORDS config. Anything else imports an app onto missing tables.</details>

## 9. App export alone: sufficient backup?
<details><summary>Answer</summary>No — metadata only. Without the DB backup underneath there is nothing to import into.</details>

## 10. Patch fallback armed when?
<details><summary>Answer</summary>Before the first change: flashback window + verified RMAN piece + written go/no-go gates — the EBS-lab rehearsal rule applies here too.</details>
