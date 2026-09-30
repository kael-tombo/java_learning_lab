# CHECKLIST: Architectural Decision & Governance Readiness
## Lab 19 | Production Engineering Academy

---

## 1. ADR Authoring Standards
- [ ] Michael Nygard format followed (Context, Drivers, Considered Options, Outcome, Consequences).
- [ ] Decision Type explicitly categorized (Type 1 Irreversible vs Type 2 Reversible).
- [ ] Negative consequences and accepted trade-offs explicitly documented (no "pure win" fairy tales).
- [ ] Alternatives objectively evaluated with pros and cons.

## 2. Review & Consensus Gates
- [ ] Shared in RFC Slack channel for at least 72 hours.
- [ ] Feedback collected from engineers who will implement and maintain the system.
- [ ] Approval obtained from designated Architecture Review Board (ARB) members.

## 3. Automated Fitness Enforcement
- [ ] ArchUnit tests implemented in CI to enforce architectural boundaries and package dependencies.
- [ ] ADR committed to Git repository under `/docs/adr/`.
- [ ] Superseded ADRs linked and marked deprecated.
