# Lab 08: Integrations (SOAP / Business Events) — README

## Overview
Design and implement a bi-directional SOAP integration between EBS 12.2 Order
Management and Salesforce Sales Cloud: Salesforce Opportunities become EBS
quotes, booked orders flow back, with Oracle Workflow business events,
`OE_QUOTE_PUB`/`OE_ORDER_PUB` APIs, OAuth2, transformation, retry logic, and a
dead letter queue — replacing a 2-day manual process with 15% error rates.

## Learning Objectives
By the end of this lab you will be able to:
- Design a bi-directional integration architecture with clear boundaries
- Publish EBS Order Management as a SOAP web service via business events
- Consume Salesforce REST APIs with OAuth2 client credentials
- Transform Salesforce Account/Contact into EBS `HZ_CUST_ACCOUNTS`
- Create quotes with `OE_QUOTE_PUB` and orders with `OE_ORDER_PUB`
- Push order status back to Salesforce via outbound messages
- Implement retry logic, idempotency, and a dead letter queue

## Prerequisites
- Oracle EBS Order Management R12.2 fundamentals
- SOAP and REST concepts
- OAuth2 client credentials flow
- Salesforce platform basics (Accounts, Contacts, Opportunities)

## Lab Structure
| File | Description |
|------|-------------|
| `PROBLEM_WALKTHROUGH.md` | Full integration design and implementation |
| `THEORY.md` | Integration patterns, business events, idempotency, error handling |
| `CODE_DEEP_DIVE.md` | WSDL, business events, transformation, retry, DLQ |
| `EXERCISES.md` | 8 hands-on integration exercises |
| `MATH_FOUNDATION.md` | Latency, throughput, error rates, retry math |
| `QUIZ.md` | 10-question knowledge check |
| `FLASHCARDS.md` | Quick-reference cards |
| `VISION.md` | Learning arc, milestones, anti-goals |
| `MINI_PROJECT.md` | 90-minute integration exercise |
| `REAL_WORLD_PROJECT.md` | Salesforce-EBS order sync programme |

## Time Estimate
- Core lab: 180 minutes
- Exercises: 60 minutes
- Mini-project: 45 minutes

## Key Concepts
1. **Integration architecture** — boundaries, ownership, direction
2. **Business events** — publishing EBS state changes as events
3. **SOAP services** — WSDL, operations, synchronous vs asynchronous
4. **OAuth2** — client credentials, token lifecycle
5. **Transformation** — Salesforce → `HZ_CUST_ACCOUNTS` mapping
6. **Idempotency** — the property that makes retry safe
7. **Retry with backoff** — bounded, observable, recoverable
8. **Dead letter queue** — where failed messages go and how they are replayed