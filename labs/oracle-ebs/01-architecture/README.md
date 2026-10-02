# Lab 01: EBS Multi-Tier Architecture — HA, Load Balancing, Failover

## Overview
Design a high-availability Oracle EBS R12.2 multi-tier architecture supporting 5,000 concurrent users across three geographic regions with 99.95% uptime SLA, sub-second response times, and zero data loss during failover.

## Learning Objectives
By the end of this lab, you will be able to:
- Design a 3-node application tier cluster with F5 BIG-IP load balancing
- Configure Oracle RAC database with Data Guard for disaster recovery
- Implement specialized Concurrent Managers per node for workload isolation
- Plan zero-downtime patching with FS_CLONE (adop) rolling cutover
- Build monitoring queries for architecture health validation

## Prerequisites
- Oracle EBS R12.2.11 knowledge
- Oracle Database 19c RAC fundamentals
- Linux administration basics
- Load balancer (F5 BIG-IP) concepts

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Complete architecture design with all steps |
| `THEORY.md` | HA architecture principles, RAC, Data Guard, load balancing |
| `CODE_DEEP_DIVE.md` | Service configuration, F5 pools, adop, monitoring SQL |
| `EXERCISES.md` | 7 hands-on architecture exercises |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference flashcards |
| `WORKED_EXAMPLE.sql` | Complete SQL/PLSQL for configuration |
| `MINI_PROJECT/` | Design HA architecture for 10K users |
| `REAL_WORLD_PROJECT/` | Global instance consolidation blueprint |

## Time Estimate
- Core lab: 120 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts Covered
1. **Application Tier Clustering** — 3-node active-active behind F5
2. **Load Balancer Configuration** — Forms, OAF, CM pools with persistence
3. **Database Tier** — 2-node RAC + 1 Standby with Data Guard
4. **Concurrent Manager Specialization** — Per-node specialized queues
5. **Work Shifts** — Regional peak hour optimization
6. **FS_CLONE Patching** — Rolling adop cutover across regions
7. **Failover Architecture** — App tier health checks, DB Fast-Start Failover
8. **Monitoring & Validation** — Forms sessions, CM queues, RAC load, DG lag