# Lab 03: Interactive Reports — Dynamic Filtering, Master-Detail, Download & Email

## Overview
Master Oracle APEX Interactive Reports (IR) with dynamic filters, master-detail navigation, CSV email delivery, and performance optimization for large datasets.

## Learning Objectives
By the end of this lab, you will be able to:
- Build IR with dynamic date-range and search filters using bind variables
- Implement master-detail IR navigation (page-to-page and modal dialog)
- Add multi-row selection with CSV download and email via APEX_DATA_EXPORT
- Optimize IR performance for 500K+ rows using pagination, indexes, and materialized views

## Prerequisites
- APEX 23.2+ workspace
- Oracle Database 19c+
- Completed Lab 01 (Getting Started), Lab 02 (Workshop Builder)

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | 4 complete problem scenarios with solutions |
| `THEORY.md` | IR architecture, filtering, pagination, export internals |
| `CODE_DEEP_DIVE.md` | APEX_DATA_EXPORT, APEX_MAIL, IR JavaScript API |
| `EXERCISES.md` | 8 hands-on exercises |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference flashcards |
| `WORKED_EXAMPLE.sql` | Complete worked SQL/PLSQL |
| `MINI_PROJECT/` | Build a sales dashboard with saved reports |
| `REAL_WORLD_PROJECT/` | Executive reporting portal with subscriptions |

## Time Estimate
- Core lab: 90 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts Covered
1. **Dynamic WHERE Clauses** — Bind variables for date ranges and search
2. **Master-Detail IR** — Link columns with page item passing
3. **Row Selection & Export** — APEX_APPLICATION.G_F01, APEX_DATA_EXPORT
4. **Email Integration** — APEX_MAIL with CSV attachments
5. **Performance Tuning** — Indexes, materialized views, pagination settings