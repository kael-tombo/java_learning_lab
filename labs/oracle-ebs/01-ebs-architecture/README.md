# Lab 01: EBS Architecture — README

## Overview
Diagnose and remediate month-end Concurrent Manager contention on a 2,000-user
EBS 12.2 instance, where app tier CPU is at 100% while the database sits at 60%.

## Learning Objectives
By the end of this lab you will be able to:
- Diagnose a tier-level constraint by comparing utilisation across tiers
- Explain `JTF_QUEUE_LOCK` contention and why high CPU coexists with poor throughput
- Design an application-tier node cloning plan with per-node service assignment
- Create specialised Concurrent Managers using `FND_CONCURRENT_QUEUE_PUB`
- Enable JTF clustering so multiple nodes coordinate rather than collide
- Configure work shifts to shape capacity across regional peaks
- Validate the fix with a measured before/after load test

## Prerequisites
- Oracle EBS R12.2 fundamentals
- Concurrent Manager concepts and concurrent request lifecycle
- Basic Oracle Database querying (`FND_CONCURRENT_REQUESTS`)
- Linux process/CPU troubleshooting

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Complete diagnostic and remediation walkthrough |
| `THEORY.md` | Tier diagnosis, contention, specialisation, JTF clustering |
| `CODE_DEEP_DIVE.md` | SQL queries, PL/SQL API calls, cluster configuration |
| `EXERCISES.md` | 8 hands-on diagnostic and configuration exercises |
| `MATH_FOUNDATION.md` | Queueing, utilisation, Little's Law, capacity math |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute diagnosis and remediation exercise |
| `REAL_WORLD_PROJECT.md` | Client engagement scenario with full delivery plan |

## Time Estimate
- Core lab: 120 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Per-tier utilisation** — 100% app vs 60% DB is a tier finding
2. **Contention fingerprint** — high CPU with poor throughput means lock contention
3. **`JTF_QUEUE_LOCK`** — workers spinning on rows, not doing work
4. **Specialisation** — separate queues isolate workload blast radius
5. **Horizontal scale** — more nodes, not more processes on a saturated node
6. **JTF clustering** — coordinates reservation across nodes
7. **Work shifts** — shape capacity to demand over time
8. **Measured validation** — before/after with real numbers