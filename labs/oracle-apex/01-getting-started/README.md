# Lab 01: APEX Getting Started (CRUD) — README

## Overview
Build a complete department expense tracking application in Oracle APEX: an
Interactive Report with sorting, filtering, and searching; a form page for create,
edit, and delete with confirmation; and category/month summaries — all with
row-level security so managers see only their own department.

## Learning Objectives
By the end of this lab you will be able to:
- Explain the workspace/schema model and where application data lives
- Build an Interactive Report with sorting, filtering, search, and pagination
- Build a form page supporting insert, update, and delete
- Link pages using session state rather than page submission
- Add validation with actionable error messages
- Implement department-scoped row security and verify cross-department denial
- Build summary regions that are scoped identically to detail regions

## Prerequisites
- Oracle APEX 23.2 or later
- Oracle Database 19c or later
- Basic SQL
- A workspace with an assigned schema

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Complete application build |
| `THEORY.md` | APEX architecture, regions, state, row security |
| `CODE_DEEP_DIVE.md` | Schema, queries, processes, row security |
| `EXERCISES.md` | 8 hands-on APEX exercises |
| `MATH_FOUNDATION.md` | Data volume, filter cost, pagination, query math |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute CRUD application exercise |
| `REAL_WORLD_PROJECT.md` | Client expense tracking application |

## Time Estimate
- Core lab: 150 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Workspace and schema** — where APEX runs and where your data lives
2. **Pages and regions** — APEX is a page-and-region model
3. **Interactive Reports** — display, filter, search, aggregate
4. **Forms** — DML through page processes, not SQL on submit
5. **Session state** — the correct way to pass context between pages
6. **Validation** — server-side rules with useful messages
7. **Row security** — scoping every region, including summaries
8. **Export** — declarative, and reversible