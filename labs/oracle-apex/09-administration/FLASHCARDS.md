# FLASHCARDS — APEX Administration

| # | Front | Back |
|---|-------|------|
| 1 | Three admin tiers? | Instance (posture) / workspace (tenant) / application (auth+pages). |
| 2 | Workspace binds? | Name + parsing schemas + people-in-roles. |
| 3 | Developer ≠ ? | Workspace-admin, instance-admin, schema-owner, DBA. |
| 4 | Quota purpose? | Blast-radius bound on runaway loaders. |
| 5 | Posture five-pack? | Passwords, session timeout, HTTPS, outbound allow-list, size caps. |
| 6 | Outbound gates (2)? | ORDS host rules AND DB network ACLs — both must permit. |
| 7 | Triage triple? | Slowest, most-erroring, hottest — from activity log. |
| 8 | Slow page next step? | APEX_DEBUG session trace → region-level culprit. |
| 9 | Pool vs DB pressure? | Queue+latency up at flat DB load = ORDS pool. |
| 10 | Backup trio? | App export + workspace export + DB backup. |
| 11 | Restore order? | Workspace → schema/data → app → ORDS config. |
| 12 | Patch snapshot? | Apps + instance params before/after — behavior as diff. |
| 13 | Fallback timing? | Armed before change: flashback + verified RMAN. |
| 14 | Session floor? | Instance 15-min timeout; apps can only tighten. |
| 15 | Audit cadence? | Weekly log review; alert on deltas. |
