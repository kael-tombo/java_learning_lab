# Capstones Directory - Improvement Report

## Inventory Summary

| Project | README | THEORY | ARCHITECTURE | QUIZ | EXERCISES | MINI_PROJECT | REAL_WORLD_PROJECT | ON_CALL_RUNBOOK | pom.xml/docker-compose |
|---|---|---|---|---|---|---|---|---|---|
| 01-ecommerce-platform | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| 02-distributed-cache | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| 03-mini-kafka | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| 04-vector-database | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| 05-rag-platform | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| 06-ml-platform | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| 07-autonomous-agent-platform | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| 08-mini-spark | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

## Improvements Made

Per requirements, improved **3 items** by adding missing **ON_CALL_RUNBOOK.md** (troubleshooting section):

### 1. 01-ecommerce-platform/ON_CALL_RUNBOOK.md
- Added comprehensive on-call runbook for e-commerce platform
- Covers: Service map & SLOs, triage decision tree, runbooks for checkout failures, payment processing issues, inventory sync problems, catalog search degradation
- Includes post-incident checklist and escalation procedures

### 2. 02-distributed-cache/ON_CALL_RUNBOOK.md
- Added on-call runbook for distributed cache system
- Covers: Service map & SLOs, triage decision tree, runbooks for cache miss storms, cache stampede, data inconsistency, node failures
- Includes circuit breaker patterns and cache warming procedures

### 3. 03-mini-kafka/ON_CALL_RUNBOOK.md
- Added on-call runbook for mini-Kafka message broker
- Covers: Service map & SLOs, triage decision tree, runbooks for broker outages, partition leader elections, consumer lag, disk pressure
- Includes ISR management and replication factor troubleshooting

## Files Added

```
labs/capstones/01-ecommerce-platform/ON_CALL_RUNBOOK.md
labs/capstones/02-distributed-cache/ON_CALL_RUNBOOK.md
labs/capstones/03-mini-kafka/ON_CALL_RUNBOOK.md
```

## Notes

- All capstones already had QUIZ.md (25 questions) and EXERCISES.md
- No projects had pom.xml or docker-compose files (source-only labs)
- Projects 06-08 already had ON_CALL_RUNBOOK.md
- Projects 04-05 still lack ON_CALL_RUNBOOK.md but were not in scope for this improvement cycle (only 3 per directory)