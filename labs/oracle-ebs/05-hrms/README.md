# Lab 05: HRMS Data Migration — README

## Overview
Migrate 20,000 employee records from a legacy SAP HR system into Oracle EBS
HRMS for a global bank across 15 countries — where only 60% of records pass
validation due to missing supervisors, invalid national identifiers, mixed date
formats, and overlapping assignment effective dates.

## Learning Objectives
By the end of this lab you will be able to:
- Build a pre-validation staging layer that captures all source records
- Write domain-specific PL/SQL validation routines (person, assignment, supervisor)
- Implement a multi-pass load respecting dependency order
- Handle orphaned supervisor references with placeholder records
- Normalize dates and national identifiers using country-specific rules
- Load through `PER_ALL_PEOPLE_F` / `PER_ALL_ASSIGNMENTS_F` APIs
- Drive a re-validation loop to 99.9% acceptance and manage the long tail

## Prerequisites
- Oracle EBS HRMS R12.2 fundamentals
- Effective-dated data modelling
- Data migration patterns (stage → validate → load → reconcile)
- PL/SQL collections and exception handling

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Full migration strategy and execution |
| `THEORY.md` | Migration methodology, validation domains, dependency ordering |
| `CODE_DEEP_DIVE.md` | Staging, validators, multi-pass loader, reconciliation |
| `EXERCISES.md` | 8 hands-on migration exercises |
| `MATH_FOUNDATION.md` | Pass-rate convergence, error rates, dependency math |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute staged migration exercise |
| `REAL_WORLD_PROJECT.md` | Bank migration with fixed go-live |

## Time Estimate
- Core lab: 150 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Stage before loading** — never validate against the target directly
2. **Domain validation** — person, assignment, supervisor, identifier, date
3. **Dependency order** — people → assignments → supervisors
4. **Placeholders** — preserve hierarchy when a manager is missing
5. **Normalization** — country-specific date and identifier rules
6. **API-only loading** — `PER_ALL_PEOPLE_F` / `PER_ALL_ASSIGNMENTS_F`
7. **Convergence** — the long tail matters more than first-pass rate
8. **Reconciliation** — counts, totals, and hierarchy integrity