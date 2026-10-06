# Lab 07: APEX Advanced Components — README

## Overview
Master APEX's most powerful components — Interactive Grid editing with per-cell
validation, master-detail grids, Oracle JET charts, and plugin-based extension —
building an Excel-like order entry grid and a multi-level data browser.

## Learning Objectives
By the end of this lab you will be able to:
- Choose between Interactive Report and Interactive Grid from use case
- Configure an IG with editing, aggregations, and control breaks
- Implement cell-level and row-level validation distinctly
- Build master-detail grids linked by a foreign key
- Save per-user IG state and layout preferences
- Configure Oracle JET charts and know their limits
- Extend APEX with a plugin rather than forking framework code

## Prerequisites
- Oracle APEX 23.2 or later
- Lab 01: APEX Getting Started
- Lab 04: APEX Interactive Grid concepts
- JavaScript and jQuery basics

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Advanced component builds |
| `THEORY.md` | IG vs IR, editing model, validation, JET, plugins |
| `CODE_DEEP_DIVE.md` | IG configuration, validation, JET, plugin code |
| `EXERCISES.md` | 8 hands-on advanced component exercises |
| `MATH_FOUNDATION.md` | Save payload math, validation cost, state sizing |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute advanced component exercise |
| `REAL_WORLD_PROJECT.md` | Order entry grid and analytics browser |

## Time Estimate
- Core lab: 180 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **IG vs IR** — read-only display versus spreadsheet editing
2. **Edit model** — allowed operations, primary key, and the Save contract
3. **Cell vs row validation** — different problems, different mechanisms
4. **Computed columns** — recalculated versus saved
5. **Aggregation and control breaks** — rollups without extra regions
6. **Master-detail IG** — two grids joined by a foreign key
7. **Per-user state** — layout preferences and saved filters
8. **Plugins** — extend APEX without forking framework code