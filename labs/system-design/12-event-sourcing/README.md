# Lab 12: Event Sourcing

## Overview
Event-sourced systems: immutable event logs as the source of truth, state
rebuilt by projection, auditability as a first-class property, and the
operational discipline that keeps a growing log manageable.

## Prerequisites
- Java 21+, strong understanding of state modelling
- Relational database and indexing
- CAP theorem and idempotency
- Basic message broker concepts

## What You Will Learn
- Why storing events rather than state changes the shape of a system
- Event schemas, versioning, and the upcasting problem
- Optimistic concurrency control via expected version
- Projections, read models, and rebuild from scratch
- Snapshots, compaction, and long-term log growth
- Temporal queries ("balance as of T")
- Exactly-once illusions via idempotent projection

## Lab Structure
| File | Description |
|------|-------------|
| VISION.md | What this lab is for and how to use it |
| THEORY.md | Event sourcing, projections, versioning, operations |
| MATH_FOUNDATION.md | Storage growth, snapshot sizing, latency, read amplification |
| CODE_DEEP_DIVE.md | Aggregate, event store, projector, snapshot, upcaster |
| EXERCISES.md | 12 graded exercises with solutions |
| QUIZ.md | 15 questions with answers and explanations |
| FLASHCARDS.md | 60 review cards |
| MINI_PROJECT.md | An event-sourced ledger with rebuildable projections |
| REAL_WORLD_PROJECT.md | Production event sourcing for a banking platform |

## Quick Start
```bash
cd 12-event-sourcing
# 1. Read VISION.md, then THEORY.md
# 2. Work through MATH_FOUNDATION.md for storage and snapshot sizing
# 3. Implement CODE_DEEP_DIVE.md
# 4. Complete EXERCISES.md, then test yourself with QUIZ.md
# 5. Build MINI_PROJECT.md, then design REAL_WORLD_PROJECT.md
```

## Learning Path
1. `VISION.md` for the mental model.
2. `THEORY.md` for the architecture and the hard parts.
3. `MATH_FOUNDATION.md` for storage, snapshot, and latency arithmetic.
4. `CODE_DEEP_DIVE.md` for the implementation.
5. `EXERCISES.md` to apply it; `QUIZ.md` to check yourself.
6. `MINI_PROJECT.md` for hands-on; `REAL_WORLD_PROJECT.md` for production.

## Key Topics
- Events as the source of truth vs. events as notifications
- Optimistic concurrency via expected version
- Event schema evolution, upcasting, and tolerant readers
- Projections: synchronous, async, rebuildable
- Snapshotting, compaction, and checkpointing
- Temporal queries and full audit reconstruction
- Poison messages, replay, and blue-green projection deploys
- GDPR erasure vs. the immutability requirement

## Estimated Time: 7 hours