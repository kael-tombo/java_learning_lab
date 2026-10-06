# Lab 09: Security (SOD Remediation) — README

## Overview
Remediate segregation-of-duties violations at a financial services client
undergoing SOX testing: 45 users hold conflicting responsibilities (create
supplier, approve invoice, process payment), 12 dormant accounts have elevated
access, and a profile with `FND_HIDE_DB_PASSWORD='N'` exposes database
credentials — remediated within 30 days without disrupting the business.

## Learning Objectives
By the end of this lab you will be able to:
- Perform SOD risk analysis mapping functions to conflict categories
- Detect conflicting responsibility assignments across a user population
- Build an SOD risk matrix with conflict definitions
- Remediate current violations without disrupting operations
- Implement preventive controls blocking future violations at grant time
- Run a monthly SOD certification process with evidence capture
- Harden the security posture including password visibility and dormant accounts

## Prerequisites
- Oracle EBS security model (responsibilities, function security, MOAC)
- SOX control concepts and segregation of duties
- FND_USER and FND_USER_RESPONSIBILITIES tables
- FND_FUNCTION security

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Full SOD remediation plan |
| `THEORY.md` | SOD theory, preventive vs detective, remediation strategy |
| `CODE_DEEP_DIVE.md` | SOD queries, risk matrix, preventive control, certification |
| `EXERCISES.md` | 8 hands-on SOD exercises |
| `MATH_FOUNDATION.md` | Violation rates, control effectiveness, remediation metrics |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute SOD remediation exercise |
| `REAL_WORLD_PROJECT.md` | SOX SOD remediation engagement |

## Time Estimate
- Core lab: 150 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **SOD fundamentals** — why conflicting duties are a fraud enabler
2. **Risk matrix** — functions mapped to conflict categories
3. **Detection** — finding violations across a user population
4. **Remediation** — revoking access without disrupting business
5. **Preventive control** — blocking violations at grant time
6. **Certification** — periodic attestation with evidence
7. **Exceptions** — documented, approved, time-bound
8. **Hardening** — password visibility, dormant accounts, least privilege