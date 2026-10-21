# Data Governance Interview Questions

## Beginner
**Q**: What is data governance?
**A**: Data governance is the practice of managing data assets through policies, processes, and technologies to ensure data is accurate, available, secure, and compliant.

## Intermediate
**Q**: Explain data lineage and why it matters.
**A**: Data lineage tracks where data comes from, how it's transformed, and where it goes. It's critical for debugging, impact analysis, regulatory compliance, and building trust in data.

## Advanced
**Q**: How would you implement data governance in a data mesh architecture?
**A**: Each domain owns its data and governance. Provide shared tools (catalog, lineage, policy engine) as a platform. Domains implement domain-specific policies within their boundaries. Central team provides standards, tooling, and cross-domain governance.

## Senior
**Q**: Design a governance strategy for a company with 1000+ data assets across 20 domains.
**A**: Phase 1: Automated catalog discovery, PII detection, basic lineage. Phase 2: Domain ownership, quality metrics, policy engine. Phase 3: Automated compliance reporting, anomaly detection on governance metrics, self-service data access with policy enforcement.
