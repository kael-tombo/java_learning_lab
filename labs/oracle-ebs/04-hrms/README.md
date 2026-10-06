# Lab 04: Employee Lifecycle Management (HRMS) — README

## Overview
Design a unified, automated employee lifecycle in Oracle EBS HRMS for 25,000
employees across 18 countries — from hire through onboarding, payroll setup,
benefits, development, termination, and offboarding — with automated triggers,
ADP payroll integration, legislative compliance, and a 7-year audit trail.

## Learning Objectives
By the end of this lab you will be able to:
- Model the full hire-to-alumni lifecycle as automated, event-driven transitions
- Design automated triggers cascading hire → onboarding → payroll → benefits
- Enforce per-country labour law (notice periods, final pay) via legislative data groups
- Build a 7-year-retention lifecycle audit trail
- Integrate bidirectionally with ADP Global View for payroll
- Build manager self-service for promotion, transfer, and termination
- Automate offboarding with an exit checklist and evidence capture

## Prerequisites
- Oracle EBS HRMS R12.2 fundamentals (people, assignments, positions)
- Public HRMS APIs (`PER_ALL_PEOPLE_F`, `PER_ALL_ASSIGNMENTS_F`)
- Effective-dated data modelling
- Basic workflow and concurrent program concepts

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Full lifecycle design and implementation |
| `THEORY.md` | Lifecycle modelling, effective dating, legislative compliance |
| `CODE_DEEP_DIVE.md` | HRMS API calls, trigger engine, audit trail, ADP payloads |
| `EXERCISES.md` | 8 hands-on lifecycle exercises |
| `MATH_FOUNDATION.md` | Turnover, TSF, lifecycle timing, capacity math |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute lifecycle automation exercise |
| `REAL_WORLD_PROJECT.md` | Global HR lifecycle programme |

## Time Estimate
- Core lab: 150 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Lifecycle state machine** — hire → active → terminated → alumni
2. **Effective dating** — `_F` history vs `_V` current state
3. **Event triggers** — cascade downstream work automatically
4. **Legislative compliance** — per-country rules in HRMS, not in code
5. **Payroll integration** — outbound + reconciliation inbound
6. **Self-service** — manager workflow with approval routing
7. **Offboarding** — checklist automation and evidence
8. **Audit trail** — immutable, 7-year retention