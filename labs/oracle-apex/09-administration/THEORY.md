# THEORY — APEX Administration

## 1. The three tiers you administer

APEX administration splits into **instance** (the whole APEX engine:
security posture, resources, patching), **workspace** (a tenant: schemas,
developers, storage), and **application** (lab 03/05 territory). Confusing
the tiers is the root of most admin mistakes — e.g. fixing a workspace
quota problem with an instance parameter, or enforcing security per-app
that belongs instance-wide.

## 2. Provisioning = identity + schema + quota

A workspace binds a name to parsing schemas (the tables apps touch) and
people in roles (workspace-admin manages users, developer builds,
end-user runs). Least privilege applies upward too: developers never get
workspace-admin, workspace-admins never get instance-admin. Schema quotas
bound the blast radius of a runaway loader long before monitoring notices.

## 3. Posture beats patching

Password policy, 15-minute session timeout (same rule as lab 03, now
enforced platform-wide), mandatory HTTPS, outbound network allow-listing
(ORDS/DB ACLs so apps can only reach approved hosts), and workspace file/
workarea caps. Each is one misconfiguration from an incident: open
outbound = SSRF springboard; unlimited uploads = disk exhaustion; weak
sessions = hijack window. Set them at instance level so no single app can
opt out.

## 4. Monitoring is triage, not dashboards

`apex_workspace_activity_log` answers the only three questions that
matter: what's slow (elapsed-time ranking), what's broken (error spikes
by page/process), what's hot (page-view concentration). `APEX_DEBUG`
session tracing reproduces single-user pain; ORDS pool saturation
(queued requests, growing response times with idle DB) says scale the
middle tier, not the database. Review weekly; alert on deltas, not
absolutes.

## 5. Backup order and patch fallback

Restore order is fixed: workspace definition → schema objects/data →
application import → ORDS/security config re-application. Any other order
imports an app whose tables don't exist yet. Patching mirrors it: full
backup (DB + exports) → stage → test matrix (auth, REST, reports) → prod
window → flashback/RMAN fallback armed *before* the first change, with
written go/no-go gates — the same rehearsal discipline as the EBS upgrade
lab (`labs/oracle-ebs/10-upgrade-migration/`).
