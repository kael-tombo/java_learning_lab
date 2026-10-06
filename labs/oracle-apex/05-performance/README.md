# Lab 05: APEX Performance (Caching, Collections, Bulk) — README

## Overview
Optimise a 30-second executive dashboard in a 10,000-user APEX application:
10 interactive reports over 5M-row tables, 6 chart regions with complex
aggregations, cascading filters, and CSV export — targeting under 3 seconds p95,
under 1 second for filter changes, and 100K-row export in under 30 seconds.

## Learning Objectives
By the end of this lab you will be able to:
- Attribute page time to components rather than guessing
- Share one query across regions using collections
- Apply region and page caching with correct invalidation triggers
- Convert row-by-row processing into bulk set-based operations
- Rewrite export from the APEX default to a bounded, fast path
- Cache reference data without serving stale content
- Measure each optimisation independently

## Prerequisites
- Oracle APEX 23.2 or later
- Lab 02: Page Designer
- Lab 08: APEX Performance (query optimisation)
- Understanding of database result caching

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Dashboard optimisation walkthrough |
| `THEORY.md` | Attribution, collections, caching, bulk operations |
| `CODE_DEEP_DIVE.md` | Collection, cache, bulk, export implementations |
| `EXERCISES.md` | 8 hands-on performance exercises |
| `MATH_FOUNDATION.md` | Cost models, cache hit rates, bulk throughput |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute optimisation exercise |
| `REAL_WORLD_PROJECT.md` | Enterprise dashboard optimisation |

## Time Estimate
- Core lab: 180 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Attribution** — measure before optimising; one Debug run finds the problem
2. **Collections** — one query, many regions
3. **Caching** — region and page cache with invalidation triggers
4. **Bulk operations** — set-based, not row-by-row
5. **Export** — bounded fetch, not the default full-dump path
6. **Reference data** — cache aggressively; it rarely changes
7. **Measurement** — each fix measured alone, not bundled