# ARCHITECTURE DECISIONS: Enterprise Incident Response Standards
## Lab 14 | Production Engineering Academy

---

## ADR-01: Incident Command System & Post-Mortem Policy

### Status: ACCEPTED

### Context
Uncoordinated incident response led to extended MTTR ($> 90\text{ minutes}$) during critical customer checkout outages.

### Decisions
1. **Mandatory Incident Command for P1/P2**:
   - Any incident affecting $> 1\%$ of users or payment transactions requires an Incident Commander (IC).
   - The IC has absolute authority to direct mitigation, including emergency rollbacks and traffic shedding.
2. **Blameless Post-Mortem Requirement**:
   - Every Sev-1 and Sev-2 incident requires a published blameless post-mortem within 72 hours.
   - Root cause analysis must employ the "5 Whys" methodology.
3. **Action Item Tracking**:
   - Corrective actions must be logged as P1 Jira tickets and scheduled in the immediately following engineering sprint.

### Consequences
- Decreased MTTR by 45% through coordinated command.
- Encourages open reporting of near-misses and operational weaknesses.
