# CODE_DEEP_DIVE — Upgrade walkthrough code

All references are to `PROBLEM_WALKTHROUGH.md` in this lab.

## 1. ADOP readiness + editioning (Problem 1, lines 21–63)

- **Readiness query**: `dba_objects WHERE owner LIKE 'XX%' AND
  edition_name IS NULL AND type IN (TABLE,VIEW,PACKAGE,…)` — every row is
  a patch-cycle breaker. Run in dev first; zero rows is the gate.
- **Rename → view → trigger**: `ALTER TABLE … RENAME TO …_tb` preserves
  data; `CREATE EDITIONING VIEW` restores the original name (apps code
  unchanged); the `INSTEAD OF INSERT/UPDATE/DELETE FOR EACH ROW` trigger
  replays DML to `_tb` with `:NEW.*` (note the walkthrough's UPDATE/DELETE
  bodies are abbreviated `SET …`/`WHERE …` — fill in PK predicates per
  table; blind `UPDATE …_tb SET …` without a WHERE would be catastrophic).
- **`FND_FILE.PUT_LINE` → `FND_LOG.STRING(LEVEL_STATEMENT, module,
  message)`**: same call sites, leveled logging the concurrent manager
  routes correctly under ADOP.

## 2. Cloud repointing (Problem 2, lines 92–127)

- **DB link** to RDS built with `EXECUTE IMMEDIATE` string concat —
  credentials inline in the example are redacted (`****`); in practice use
  a wallet/secret, never cleartext in a script.
- **Endpoint flip**: `SELECT` the four agent-host profiles to confirm
  current values, then `fnd_profile.save('APPS_WEB_AGENT_HOST', ELB…,
  'SITE')` (+ frames host) and `COMMIT`. ELB DNS — not instance IPs —
  is what makes future ASG churn invisible to EBS.

## 3. DB upgrade checks (Problem 3, lines 156–198)

- **Feature audit**: `dba_feature_usage_statistics WHERE currently_used =
  'TRUE'` for replication/streams/text/transportable — each hit needs a
  removal/migration plan before AutoUpgrade.
- **LONG→CLOB rewrite**: `SELECT notes INTO l_long_data` becomes
  `SELECT TO_CLOB(notes) INTO l_clob_data` — 19c removed LONG from
  PL/SQL; every `LONG` declaration is a compile error post-upgrade, so
  grep the custom schema for `%LONG%` early.
- **Post-upgrade stats**: `GATHER_FIXED_OBJECTS_STATS` then
  `GATHER_DATABASE_STATS(gather_sys=>TRUE, 'GATHER STALE')` — without
  these, the new optimizer flies blind and plan regressions masquerade
  as "the upgrade broke performance".
