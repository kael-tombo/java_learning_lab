# Lab 02: APEX Page Designer — README

## Overview
Build a responsive sales dashboard in APEX Page Designer: an Interactive Report
top row, two pie charts and a bar chart below, all driven by shared date-range
filters via a Dynamic Action, with drill-through navigation and correct region
queries — replacing a page where every region ran an unfiltered query.

## Learning Objectives
By the end of this lab you will be able to:
- Explain the three execution phases of an APEX page (render, process, after)
- Lay out a page on a 12-column grid with positioned regions
- Bind shared page items into every region query
- Build a Dynamic Action that refreshes multiple regions via AJAX
- Distinguish a page process, a Dynamic Action, and a branch by purpose
- Implement conditional navigation with a branch
- Build drill-through passing context through session state
- Verify a page at 375 px, 768 px, and 1440 px widths

## Prerequisites
- Oracle APEX 23.2 or later
- Lab 01: APEX Getting Started
- Basic SQL and aggregation
- Familiarity with Page Designer navigation

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Dashboard build walkthrough |
| `THEORY.md` | Execution phases, layout, dynamic actions, state |
| `CODE_DEEP_DIVE.md` | Region queries, dynamic action config, process logic |
| `EXERCISES.md` | 8 hands-on Page Designer exercises |
| `MATH_FOUNDATION.md` | Query cost, layout math, refresh cost |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute dashboard build |
| `REAL_WORLD_PROJECT.md` | Client sales dashboard |

## Time Estimate
- Core lab: 150 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Three phases** — rendering, processing, and when each runs
2. **Layout grid** — 12 columns, spans, and responsive behaviour
3. **Regions** — types, positioning, and display conditions
4. **Shared items** — filters bound into every region query
5. **Dynamic Actions** — event, condition, action, no page submit
6. **Processes** — server-side work with conditions
7. **Branches** — conditional navigation
8. **Drill-through** — session state between pages