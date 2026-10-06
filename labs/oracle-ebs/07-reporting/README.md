# Lab 07: Reporting (BI Publisher) — README

## Overview
Build and deploy a BI Publisher AP Aging report for a manufacturing client —
aging buckets by supplier category, drill-down from category to supplier to
invoice detail, multi-currency conversion to USD, aging based on due date, and
delivery by email bursting — registered as an EBS concurrent program.

## Learning Objectives
By the end of this lab you will be able to:
- Design a BI Publisher data model with bind variables
- Implement aging buckets (0-30, 31-60, 61-90, 90+) based on due date
- Group by supplier category with drill-down to invoice detail
- Convert multi-currency to USD using `GL_DAILY_RATES`
- Build an RTF template with conditional formatting
- Implement drill-down hyperlinks with request parameters
- Register the report as an EBS concurrent program with bursting

## Prerequisites
- Oracle EBS Financials R12.2 basics
- SQL and PL/SQL
- BI Publisher concepts (data model, template, layout)
- Currency conversion and aging calculation

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Full report design and deployment |
| `THEORY.md` | Report design, aging semantics, currency, drill-down |
| `CODE_DEEP_DIVE.md` | Data model SQL, RTF template, drill-down, bursting |
| `EXERCISES.md` | 8 hands-on reporting exercises |
| `MATH_FOUNDATION.md` | Aging math, currency conversion, aggregate cost |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute report build exercise |
| `REAL_WORLD_PROJECT.md` | CFO AP aging reporting programme |

## Time Estimate
- Core lab: 150 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Data model** — SQL with bind variables, performance-tested
2. **Aging semantics** — due date, not invoice date
3. **Buckets** — 0-30, 31-60, 61-90, 90+ and why boundaries matter
4. **Currency** — spot rate conversion via `GL_DAILY_RATES`
5. **Drill-down** — hyperlinks carrying request parameters
6. **Template** — RTF layout with conditional formatting
7. **Bursting** — email delivery to category managers
8. **Registration** — concurrent program with parameters