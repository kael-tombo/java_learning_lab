# ARCHITECTURE DECISIONS: Architecture Decision Record Policy
## Lab 19 | Production Engineering Academy

---

## ADR-01: Adoption of Lightweight Git-Tracked Architecture Decision Records

### Status: ACCEPTED

### Context
Technical architectural rationale was historically scattered across Confluence pages, Slack threads, and unrecorded verbal conversations, leading to repeated debates and loss of architectural memory as staff changed.

### Decisions
1. **Repository Co-Location**:
   - All ADRs must be committed to the Git repository in `/docs/adr/`.
   - Markdown format with Michael Nygard structure.
2. **Review & Approval Gate**:
   - Pull Requests proposing new ADRs require approval from at least 1 Principal/Staff Architect and 2 Tech Leads.
3. **Fitness Function Enforcement**:
   - Wherever feasible, architectural rules established by ADRs must be accompanied by automated **ArchUnit tests** in the CI pipeline to prevent regressions.

### Consequences
- Architectural decisions are version-controlled alongside application code.
- New hires can understand the exact historical rationale for all major design patterns.
