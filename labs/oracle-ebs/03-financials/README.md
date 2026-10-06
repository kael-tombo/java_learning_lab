# Lab 03: Financials — README

## Overview
Reduce AP invoice holds from 30% to under 8% by correcting receipt matching
rules and deriving price/quantity tolerances from measured variance data —
without weakening SOX three-way match controls.

## Learning Objectives
By the end of this lab you will be able to:
- Build a hold taxonomy from `AP_HOLDS_ALL` ranked by volume and value
- Explain why ordered-vs-received quantity matching creates false holds
- Derive price and quantity tolerances from observed variance distributions
- Configure matching rules through purchasing setup rather than direct DML
- Build a batch hold release program with mandatory reason codes and audit trail
- Add workflow notification routing held invoices to correct approvers
- Prove a tolerance change preserved three-way match control strength

## Prerequisites
- Oracle EBS Financials R12.2 basics
- Payables invoice lifecycle (validate → hold → approve → pay)
- Purchasing three-way matching concepts
- Basic PL/SQL for concurrent program structure

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Full diagnostic and remediation walkthrough |
| `THEORY.md` | Holds, matching rules, tolerances, control preservation |
| `CODE_DEEP_DIVE.md` | Taxonomy queries, variance analysis, batch release PL/SQL |
| `EXERCISES.md` | 8 hands-on Payables exercises |
| `MATH_FOUNDATION.md` | Variance statistics, tolerance derivation, control math |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute hold-rate reduction exercise |
| `REAL_WORLD_PROJECT.md` | UAT scenario with SOX constraints |

## Time Estimate
- Core lab: 120 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Hold taxonomy** — measure before changing anything
2. **Ordered vs received matching** — the root cause of false quantity holds
3. **Tolerance derivation** — from data distributions, not convention
4. **Three-way match** — PO, receipt, invoice
5. **Control preservation** — lower holds without weakening SOX
6. **Reason-coded release** — every release justified and auditable
7. **Workflow routing** — holds reach the right person quickly
8. **Regression monitoring** — hold rate is a tracked metric