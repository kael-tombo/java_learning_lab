# Feature Stores — Step by Step

## Step 1. Define one feature with a version
Name it `login_7d_count:v1`. Record owner, SQL/logic pointer, TTL,
imputation default. Nothing enters the store without these fields.

## Step 2. Append history rows
Write (entity, ts, value) rows in event-time order. Example history:
(u1,10,1.0), (u1,20,2.0), (u1,30,3.0). Never overwrite; corrections
are new rows with newer ts.

## Step 3. Build one training row by hand
Label (u1,25). Scan rows for u1 with ts <= 25; pick max ts = 20, value
2.0. Confirm the row at ts=30 is excluded. That exclusion is the whole
point-in-time rule.

## Step 4. Run the verified as-of program
Compile and run PointInTimeJoin (see CODE_DEEP_DIVE.md). Expected:
`u1@25 -> 2.0`, `u1@30 -> 3.0`, `u2@12 -> NO_FEATURE`.

## Step 5. Simulate a skew
Apply transform 0.5*x+1.0 on the training path and 0.5*x+0.0 on a stale
serving path. Max absolute difference is 1.0. Fix serving to the same
code and confirm 0.0.

## Step 6. Enforce a TTL
With label time 100 and TTL 30, keep ages <= 30, drop the rest.
Expected kept=2, dropped=2, coverage=0.5.

## Step 7. Version a change
Copy the transform to v2, backfill history, validate null rates, then
point new training at v2 while the old model stays on v1.

## Step 8. Audit one dataset end to end
Pick the u1@25 training row and assemble its evidence: feature history
rows consulted, the ts <= 25 predicate, the chosen value 2.0, the
transform version, and the TTL that would apply at serving. File it as
a one-paragraph lineage note — that paragraph is the unit of trust the
store exists to produce.
