# THEORY — Upgrade & Migration

## 1. Why ADOP changes everything about custom code

12.2 online patching keeps two editions of every object: while users work
in the old edition, patches apply to the new one, then sessions flip.
Custom tables are invisible to this mechanism unless **editioned**: the
pattern is rename-to-`_tb` + `CREATE EDITIONING VIEW` (same name as the
original) + `INSTEAD OF` trigger replaying DML to the base table. Any
custom object without an edition (`edition_name IS NULL` in the readiness
query) breaks online patching — found in dev by the report, never in prod
by the outage.

## 2. Deprecated APIs are the long tail

`FND_FILE.PUT_LINE` → `FND_LOG.STRING(LEVEL_STATEMENT, …)`;
`FND_GLOBAL.APPS_INIT` and old concurrent-manager calls → 12.2
equivalents. 30% of 500 customizations in the scenario: audit by grep +
compile in a 12.2 dev instance, replace mechanically, regression-test the
CEMLI surface. The 14 h ADOP cycle estimate only holds *after* this
cleanup — deprecated calls inside online patches abort the cycle.

## 3. Cutover math: DMS + promotion beats dump-and-load

5 TB over Direct Connect at ~1 Gb/s ≈ 11 h bulk + catch-up replication —
inside a <2 h *cutover* because DMS replicates continuously and the
outage covers only stop-replication → promote-RDS → flip endpoints
(`APPS_WEB_AGENT_HOST` to the ELB). The database-link + `fnd_profile.save`
+ `COMMIT` sequence repoints the apps tier atomically. Storage tiering
(S3 archives) and cross-Region replicas are cost/DR decisions, not
cutover-blockers.

## 4. 11g→19c inside 8 hours with RAC

Direct path exists, but four risks decide the plan: deprecated features
(advanced replication, streams, LONG), custom PL/SQL syntax drift, stale
optimizer stats (plan regressions post-upgrade), and RAC coordination.
Mitigations compose: `preupgrd.sql` + feature-usage audit first;
AutoUpgrade with fallback; standby-first (upgrade standby, switchover —
production outage shrinks to the switchover); LONG→CLOB rewrites;
`GATHER_FIXED_OBJECTS_STATS` + dictionary stats + SQL plan baselines
after. The 8-hour budget holds application patching *and* DB upgrade only
because the rehearsal count is three, not one.
