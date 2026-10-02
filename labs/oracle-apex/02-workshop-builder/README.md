# Lab 02: Workshop Builder — Master-Detail Pages with Dynamic Actions

## Overview
Learn to build a master-detail page in Oracle APEX where selecting a row in an Interactive Report instantly refreshes a detail Interactive Grid via AJAX — no page submission required.

## Learning Objectives
By the end of this lab, you will be able to:
- Configure master-detail regions using page items as shared state
- Create Dynamic Actions for AJAX-based region refresh
- Implement inline editing with Interactive Grid
- Build real-time calculated fields using virtual columns
- Handle validation and error scenarios in master-detail flows

## Prerequisites
- APEX 23.2+ workspace
- Oracle Database 19c+ with sample schema access
- Basic SQL and PL/SQL knowledge
- Completed Lab 01 (Getting Started)

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Complete step-by-step solution |
| `THEORY.md` | Conceptual background on master-detail patterns |
| `CODE_DEEP_DIVE.md` | Technical deep-dive on Dynamic Actions and IG internals |
| `EXERCISES.md` | Hands-on practice exercises |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference flashcards |
| `WORKED_EXAMPLE.sql` | Complete worked SQL/PLSQL example |
| `MINI_PROJECT/` | Extended challenge: Multi-level master-detail |
| `REAL_WORLD_PROJECT/` | Production-ready order management app |

## Time Estimate
- Core lab: 90 minutes
- Exercises: 45 minutes
- Mini-project: 60 minutes

## Key Concepts Covered
1. **Master-Detail Synchronization** — Using page items as the bridge
2. **Dynamic Actions** — Client-side events triggering server actions
3. **Interactive Grid** — Inline editing with declarative save processing
4. **Virtual Columns** — Database-generated computed fields
5. **AJAX Refresh** — Partial page updates without submission