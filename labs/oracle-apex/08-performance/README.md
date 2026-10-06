# Lab 08: APEX Performance — README

## Overview
Optimise an APEX application systematically: attribute page time to components,
reduce SQL calls, apply caching at the right layer, tune queries and PL/SQL,
instrument with APEX's monitoring tools and the Application Performance
Analyzer, and optimise the Universal Theme.

## Learning Objectives
By the end of this lab you will be able to:
- Attribute page render time to regions, PL/SQL, and session state
- Apply region, page, session state, and result caching appropriately
- Rewrite queries for index use with binds and sargable predicates
- Optimise PL/SQL within APEX for bulk collection access
- Use APEX monitoring tools and the Application Performance Analyzer
- Instrument application code with the APEX plugin interface
- Optimise Universal Theme CSS and JavaScript assets
- Apply database-level tuning the application cannot compensate for

## Prerequisites
- Oracle APEX 23.2 or later
- Lab 02: APEX Page Designer
- Lab 05: APEX Performance (caching and collections)
- Database query optimisation fundamentals

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Systematic optimisation walkthrough |
| `THEORY.md` | Attribution, caching layers, query and PL/SQL tuning |
| `CODE_DEEP_DIVE.md` | Cache config, query rewrites, PL/SQL patterns, monitoring |
| `EXERCISES.md` | 8 hands-on performance exercises |
| `MATH_FOUNDATION.md` | Cost models, cache hit math, wait analysis |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute optimisation exercise |
| `REAL_WORLD_PROJECT.md` | Enterprise application tuning |

## Time Estimate
- Core lab: 180 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Attribution** — measure which component owns the time
2. **Four cache layers** — region, page, session state, result
3. **Sargable predicates** — the column compared to a value, not the reverse
4. **Bind variables** — hard parses and library cache latch contention
5. **PL/SQL tuning** — bulk collection access, not row-by-row
6. **Instrumentation** — APEX_DEBUG, APA, and the activity log
7. **Theme assets** — CSS and JavaScript size as a real cost
8. **Database limits** — what the application cannot fix