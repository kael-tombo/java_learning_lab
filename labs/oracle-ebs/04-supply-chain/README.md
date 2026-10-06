# Lab 04: Supply Chain (Cycle Counting) — README

## Overview
Replace a once-yearly plant-shutdown physical inventory — which revealed a $2M
discrepancy — with a continuous cycle counting programme across 50,000 SKUs and
3 warehouses, using ABC classification, count schedules, approval workflows,
handheld scanner integration, and root-cause coding.

## Learning Objectives
By the end of this lab you will be able to:
- Run an ABC classification on annual dollar usage and defend the cutoffs
- Design cycle count frequency by ABC class (A monthly, B quarterly, C annually)
- Create count schedules by subinventory with rotating assignments
- Configure approval workflows with per-ABC-class tolerance limits
- Integrate handheld barcode scanners via `INV_MATERIAL_STATUS_API`
- Build a discrepancy analysis report with root-cause coding
- Prove the cycle count programme prevents the discrepancy recurring

## Prerequisites
- Oracle EBS Inventory R12.2 fundamentals (items, subinventories, on-hand)
- Inventory costing and transaction types
- ABC analysis concepts
- Basic concurrent program and approval workflow knowledge

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Full cycle counting programme design |
| `THEORY.md` | ABC classification, counting theory, accuracy vs effort |
| `CODE_DEEP_DIVE.md` | ABC query, count schedules, tolerance config, scanner API |
| `EXERCISES.md` | 8 hands-on inventory counting exercises |
| `MATH_FOUNDATION.md` | ABC math, count coverage, discrepancy cost, accuracy math |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute cycle count design exercise |
| `REAL_WORLD_PROJECT.md` | Chemical manufacturer programme |

## Time Estimate
- Core lab: 120 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **ABC analysis** — 20% of SKUs carry 80% of dollar usage
2. **Pareto principle** — concentrate counting effort where value is
3. **Cycle counting** — continuous, not annual
4. **Count frequency** — driven by value and movement, not convenience
5. **Tolerance limits** — approval thresholds by ABC class
6. **Count schedules** — by subinventory with rotating responsibility
7. **Scanner integration** — `INV_MATERIAL_STATUS_API`
8. **Root-cause coding** — the step that actually prevents recurrence