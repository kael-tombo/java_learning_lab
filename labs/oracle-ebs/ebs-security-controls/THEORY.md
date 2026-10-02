# Theory: EBS Security Controls

## 1. Core Concepts

### 1.1 Overview

In Oracle E-Business Suite R12.2, EBS Security Controls represents a critical functional area. The technology stack includes Oracle Database 19c, Oracle Fusion Middleware, and the EBS application tier. Each component interacts through well-defined APIs and database views.

### 1.2 Key Principles

1. Separation of Concerns - The EBS architecture divides presentation, business logic, and data layers.
2. Multi-Org Access Control (MOAC) - Enables a single EBS instance to serve multiple operating units.
3. Edition-Based Redefinition - R12.2 uses EBR to support online patching, minimizing downtime.

### 1.3 Database Objects

- APPS schema - The runtime schema containing all EBS code
- FND tables - Foundation tables used by all products
- Product-specific tables (GL_, AP_, AR_, PO_, INV_)

### 1.4 Concurrent Processing

EBS uses concurrent managers to run background requests. Each request has a phase (Pending, Running, Completed) and a status (Normal, Warning, Error).

## 2. Key Technologies

| Technology | Purpose |
|------------|---------|
| Oracle Forms | Desktop UI |
| OA Framework | Web-based UI |
| Oracle Workflow | Business process automation |
| Oracle Reports | Reporting engine |
| ADOP | Online patching |

## 3. Summary

This lab builds a solid theoretical foundation for understanding EBS Security Controls within the broader EBS ecosystem. All subsequent labs will reference these concepts.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- Oracle E-Business Suite Security Guide, R12.2 (Oracle Docs, E22952) — https://docs.oracle.com/cd/E26401_01/doc.122/e22952/toc.htm — Takeaway tied to lab §1.2/§2: Function Security + Data Security + RBAC is the official model behind the lab's separation-of-concerns and MOAC notes; design responsibilities first, then menus/functions.
- Access Control with Oracle User Management: roles, permission sets, delegated administration (same Oracle EBS Security Guide, R12.2) — https://docs.oracle.com/cd/E26401_01/doc.122/e22952/toc.htm — Takeaway tied to lab §1.3 FND/APPS discussion: grants on objects and instance sets are how APPS-schema code enforces row-level access without forking code.
- Secure Configuration + Auditing and Logging checklists: Sign-On Audit, Audit Trail shadow tables, Secure Configuration Console (same Oracle EBS Security Guide, R12.2) — https://docs.oracle.com/cd/E26401_01/doc.122/e22952/toc.htm — Takeaway tied to lab §1.4 concurrent processing: pair request phase/status tracking with sign-on audit and audit-trail purging/reporting so security reviews are queries, not archaeology.
