# Lab 05: Technical Foundations (Custom Concurrent Program) — README

## Overview
Build a production-grade custom PL/SQL concurrent program for Oracle EBS R12.2
that reads supplier EDI price lists from a staging table, validates against
EBS supplier master, processes through standard PO/AP/INV APIs, and produces
detailed execution reports — reducing a 3-day manual price list update to under
one hour for 10,000+ lines per run.

## Learning Objectives
By the end of this lab you will be able to:
- Register a custom concurrent program executable with the Concurrent Manager
- Implement multi-mode execution (VALIDATE_ONLY, PROCESS, ROLLBACK) via parameters
- Process 10,000+ lines with batching, commit control, and resumability
- Use standard EBS APIs (PO, AP, INV) instead of direct DML on base tables
- Honour Multi-Org Access Control (MOAC) in a custom program
- Produce XML concurrent program output with summary and detail sections
- Build comprehensive error handling and a full audit trail

## Prerequisites
- Oracle EBS R12.2 technical fundamentals
- PL/SQL packages, collections, dynamic SQL, exception handling
- Concurrent Manager concepts and program registration
- MOAC and public API concepts

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Full program design and implementation |
| `THEORY.md` | Concurrent program mechanics, API discipline, MOAC, audit |
| `CODE_DEEP_DIVE.md` | Full package implementation, registration, XML output |
| `EXERCISES.md` | 8 hands-on concurrent program exercises |
| `MATH_FOUNDATION.md` | Throughput, batching, error rates, MOAC math |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute concurrent program exercise |
| `REAL_WORLD_PROJECT.md` | EDI price list processing programme |

## Time Estimate
- Core lab: 150 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Concurrent program wrapper** — request lifecycle and registration
2. **Multi-mode execution** — one program, parameter-driven behaviour
3. **API discipline** — never direct DML on base tables
4. **Batching and commit control** — resumability at scale
5. **MOAC** — honouring the caller's operating units
6. **Structured error logging** — survives mid-run failure
7. **XML output** — summary and detail sections
8. **Audit trail** — who, when, what, for every DML