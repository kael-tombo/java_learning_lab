# EBS Setup and Configuration — Real World Project

## Scenario
A healthcare provider is implementing EBS R12.2 and must go live in 16 weeks.
The instance was created with the wrong installation type, multi-org was never
configured for the 6 operating units, the chart of accounts has 4 unplanned
flexfield segments, and no document sequences exist so users are inventing
invoice numbers by hand. You own the setup workstream and must not create a
structure that has to be migrated later.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/cloud/saas/erp/25d/faipp/ (EBS setup and config)
- https://docs.oracle.com/database/121/EBSSR/ (EBS System Administrator's Guide)
- https://docs.oracle.com/en/database/oracle/oracle-database/19/admin/

## Architecture
```
Requirements ─► Installation type ─► Rapid Install / pre-install checks
                                            │
                                            ▼
                                   Database + apps schema
                                            │
        ┌───────────────────────────────────┼──────────────────────────┐
        ▼                                   ▼                          ▼
  Multi-org (MOAC)              Profile options (4 levels)     Flexfields
  6 operating units            system/app/resp/user            descriptive/key
        │                                   │                          │
        └───────────────────────────────────┼──────────────────────────┘
                                            ▼
                             Document sequences + auditing
                                            │
                                            ▼
                              Setup validation & sign-off
```

## Implementation sketch
```sql
-- MOAC scoping: which operating units does this responsibility see?
SELECT responsibility_name, org_id, mo_enabled
  FROM fnd_responsibilities
 WHERE application_id = 140
 ORDER BY responsibility_name;

-- Profile precedence: effective value at the most specific level set
SELECT p.profile_option_name,
       (SELECT profile_option_value FROM fnd_profile_options o
         WHERE o.profile_option_id = p.profile_option_id
           AND o.level = 10000)                                  sys_level,
       (SELECT profile_option_value FROM fnd_profile_options o
         WHERE o.profile_option_id = p.profile_option_id
           AND o.level = 40000)                                  app_level,
       (SELECT profile_option_value FROM fnd_profile_options o
         WHERE o.profile_option_id = p.profile_option_id
           AND o.level = 50000)                                  resp_level,
       (SELECT profile_option_value FROM fnd_profile_options o
         WHERE o.profile_option_id = p.profile_option_id
           AND o.level = 60000)                                  user_level
  FROM fnd_profile_options p;
```

## Requirements
- F1: Installation type decision record tied to stated business requirements.
- F2: Complete pre-install checklist with all checks passing before install.
- F3: MOAC configured for 6 operating units with an access test per unit.
- F4: Profile option standards preventing system-level changes by default.
- F5: Chart of accounts design with descriptive and key flexfield structure.
- F6: Key flexfield combination rules preventing invalid accounting combos.
- F7: Document sequences for all business documents, replacing manual numbers.
- F8: Auditing enabled on setup and financial tables with retention policy.
- F9: Setup validation suite run as a gate before go-live.
- F10: Setup data dictionary handed to the business with owners assigned.
- NF1: Go-live date met with no structure requiring post-go-live migration.
- NF2: Zero invalid key flexfield combinations in production.
- NF3: Every business document numbered from a defined sequence.
- NF4: Security baseline — setup changes restricted to the admin responsibility.
- NF5: Audit trail enabled for all setup configuration changes.
- NF6: RPO/RTO with a documented restore drill for the configured instance.

## Milestones
- Week 1: Requirements capture and installation type decision signed off.
- Week 2: Pre-install checks passed; install executed in non-production.
- Week 3: MOAC configured for all 6 operating units; access tested.
- Week 4: Chart of accounts, flexfields, and combination rules designed.
- Week 5: Sequences, auditing, and profile standards applied.
- Week 6: Setup validation suite green; data dictionary handed over.

## Verification
- Setup validation suite must pass with zero errors before go-live.
- Access matrix test proving each operating unit sees only its own data.
- Restore drill on the configured instance verifying setup data survives.
- Business sign-off on the setup data dictionary.

## Rollback
Profile option changes capture prior values; flexfield structure is versioned
by deployment script; MOAC changes are reversible by responsibility. Document
rollback steps for every configuration change.