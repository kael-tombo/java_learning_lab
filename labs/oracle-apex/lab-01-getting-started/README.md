# Lab 01: APEX Getting Started — README

## Overview
Build your first Oracle APEX application end to end: a department expense
tracker with an Interactive Report, a form page for create/edit/delete, two
summary regions, server-side validation, and department row security that
survives the summary totals.

## Learning Objectives
- Explain the workspace → schema → application → page → region hierarchy
- Build an Interactive Report with server-side pagination and bound filters
- Build a form page with one save process handling insert and update
- Pass a record ID in session state rather than in the URL
- Write server-side validation with a message that names the bad value
- Implement department scoping that fails closed when context is missing
- Demonstrate the summary-region disclosure, then fix it
- Export the application as YAML and use it as the rollback path

## Prerequisites
- Oracle APEX 24.2 (or 23.2) and Oracle Database 19c+
- A workspace with an assigned schema
- Basic SQL: SELECT, INSERT, UPDATE, DELETE, joins, indexes

## Lab Structure
| File | Description |
|------|-------------|
| `THEORY.md` | The eight principles behind a first APEX application |
| `CODE_DEEP_DIVE.md` | Annotated schema, queries, processes, row security |
| `EXERCISES.md` | 10 exercises from schema to security test |
| `MATH_FOUNDATION.md` | Pagination, selectivity, sargability, coverage math |
| `QUIZ.md` | 15 questions with answers |
| `FLASHCARDS.md` | 60 quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute expense tracker build |
| `REAL_WORLD_PROJECT.md` | Client-delivered expense application |

## Time Estimate
- Theory and build: 150 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes
- Quiz and flashcards: 25 minutes

## Key Concepts
1. Every region is a query that runs on every render
2. Pagination reduces returned bytes, never rows examined
3. Sargable predicates are the cheapest performance win in APEX
4. Session state for context, URL only for shareable links
5. DML belongs in page processes with a condition, never in a region query
6. Validation is server-side; the constraint is the backstop
7. Row security must cover summary regions and must fail closed
8. The YAML export is the rollback path
