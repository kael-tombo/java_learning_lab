# EBS Customization and Extension — Real World Project

## Scenario
A healthcare provider's EBS R12.2 instance carries 640 customizations, of which
187 modify standard objects. The last upgrade consumed 11 months and required 3
remedial patches that had to be re-authored. Meanwhile the AP team needs a new
"invoice image visible inline during approval" feature this quarter. You are
appointed to govern customization so this stops compounding — while still
delivering the feature.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- (link removed) (EBS customization)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/index.html (Application Development Guide)
- https://docs.oracle.com/en/database/oracle/oracle-database/21/lnpls/

## Architecture
```
Requirement ─► Decision record (smallest CEMLI option that works)
                    │
   ┌────────────────┼────────────────┬───────────────┐
   ▼                ▼                ▼               ▼
Configure      Personalize        Extend        Modify (last resort)
profile opts   form / OAF         APIs, AME,    standard objects,
                                workflow,       regression-tested
                                business events  on every upgrade
                                   │
                   ┌───────────────┴───────────────┐
                   ▼                               ▼
            XML Gateway / web service      Localization track
            (integration, decoupled)       (legislative, separate)
```

## Implementation sketch
```sql
-- Customization registry: every custom object needs an owner and a strategy
CREATE TABLE xx_cust_registry (
  object_name   VARCHAR2(100),
  object_type   VARCHAR2(30),   -- PACKAGE / TRIGGER / FORM / REPORT
  cemli_strategy VARCHAR2(1),   -- C/E/M/L/I
  owner         VARCHAR2(64),
  upgrade_tested CHAR(1),
  decision_ref  VARCHAR2(30),
  CONSTRAINT xx_cust_ck CHECK (cemli_strategy IN ('C','E','M','L','I'))
);
-- Modification exposure: standard objects carrying custom code
SELECT owner, name, type FROM all_source
 WHERE owner IN ('AP','AR','GL','FA','PO') AND ROWNUM <= 20;
```

## Requirements
- F1: Customization inventory classifying all 640 items by CEMLI strategy.
- F2: Risk ranking of the 187 modifications by upgrade blast radius.
- F3: Decision-record standard, enforced for every new customization request.
- F4: Delivered AP invoice-image feature built as the smallest viable option.
- F5: Extension-point catalogue documenting approved integration points.
- F6: Automated regression suite executed on every upgrade.
- F7: XML Gateway or web service interface replacing custom interface tables.
- F8: Localization track separation so legislative changes don't collide with
      functional ones.
- F9: Deprecation plan for the highest-risk modifications.
- F10: Upgrade-readiness report produced monthly, automatically.
- NF1: Next upgrade customization effort under 4 person-months (from 11).
- NF2: 100% of new customizations carry a decision record and an owner.
- NF3: Regression suite runs in under 4 hours with no manual steps.
- NF4: Security baseline — custom objects reviewed for injection risk.
- NF5: Audit trail of every registration and deprecation decision.
- NF6: RPO/RTO and a documented restore drill before each upgrade.

## Milestones
- Week 1: Inventory and CEMLI classification of all 640 customizations.
- Week 2: Risk ranking and deprecation shortlist agreed with the business.
- Week 3: Decision-record standard live; feature delivered as a pilot.
- Week 4: Extension catalogue and integration interface built.
- Week 5: Regression suite automated and green on current code.
- Week 6: Upgrade-readiness reporting live; first monthly report issued.

## Verification
- Replay the AP approval flow with the new feature and confirm audit trail.
- Regression suite run on an upgraded non-production instance.
- Restore drill verifying custom objects and registry survive recovery.
- Security review of all new custom objects before release.

## Rollback
Personalizations are removable by definition; registry rows are versioned;
extension code is deployed behind a flag; deprecated objects are archived, not
deleted. Document rollback steps for every change.