# Lab 06: APEX Migration (Forms → APEX) — README

## Overview
Migrate a legacy Oracle Forms Inventory Management system — 20+ canvases,
50+ data blocks, PL/SQL triggers, LOVs, and alerts — into a modern Oracle APEX
application, mapping Forms constructs to APEX components and relocating business
logic out of the client tier.

## Learning Objectives
By the end of this lab you will be able to:
- Inventory a Forms application systematically (canvases, blocks, triggers)
- Map Forms constructs to APEX components with named correspondences
- Convert Forms PL/SQL triggers to APEX processes, computations, and Dynamic Actions
- Relocate client-side business logic to the database tier
- Handle Forms-specific behaviours: LOVs, alerts, savepoints, LOVs on multi-row
- Plan validation migration from Forms levels to APEX validations and constraints
- Sequence a migration so each stage is independently deliverable

## Prerequisites
- Oracle Forms 6i/10g/12c concepts (canvases, data blocks, triggers)
- Oracle APEX 23.2 or later
- PL/SQL
- Lab 01: APEX Getting Started

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Full migration approach |
| `THEORY.md` | Forms-to-APEX mapping, tier relocation, validation |
| `CODE_DEEP_DIVE.md` | Trigger conversion, LOV handling, validation migration |
| `EXERCISES.md` | 8 hands-on migration exercises |
| `MATH_FOUNDATION.md` | Migration effort, coverage, risk math |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute Forms-to-APEX conversion |
| `REAL_WORLD_PROJECT.md` | Forms inventory application migration |

## Time Estimate
- Core lab: 180 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Systematic inventory** — documents, blocks, triggers, LOVs
2. **Component mapping** — canvas to page, block to region, trigger to process
3. **Tier relocation** — Forms PL/SQL moved server-side
4. **Validation migration** — Forms levels to APEX validations and constraints
5. **Navigation** — Forms menu stack to APEX breadcrumbs and tabs
6. **Savepoints** — Forms commit semantics to APEX processes
7. **LOV conversion** — Forms LOVs to APEX LOVs and popup LOVs
8. **Sequencing** — staged delivery, not big-bang cutover