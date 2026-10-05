# MINI PROJECT — Abstraction & Interfaces: Notifier SPI

## Goal (2 weeks, ~8–10h)
Design a `Notifier` abstraction with Email/SMS/Push providers + a sealed ticket-event domain — small stable API, swappable impls.

## Requirements
### Functional
1. `interface Notifier { send(Notification): Receipt }` (≤5 methods); `record Notification(Target,TemplateId,Vars)`; `abstract BaseNotifier` for retry/backoff skeleton.
2. Providers: `Email/Sms/Push` with fake transports; `default` method `sendAll(batch)`; static factory `Notifiers.of("email")`.
3. Sealed `sealed interface TicketEvent permits Created,Assigned,Resolved` + exhaustive switch dispatcher.
4. Evolution drill: add `schedule(...)` as `default` without breaking existing providers (compat test).
### Non-functional
- Interface stability doc (what is/isn't public); no constants-interface anti-pattern.
- 16+ tests: each provider, batch default, exhaustive dispatch, compat.
- README: abstract-vs-interface choice log.

## Phases
### Week 1 — Abstraction (4–5h)
- Interface/record/base + Email impl + dispatcher.
- Deliverable: 1-provider E2E + dispatch tests.
### Week 2 — Providers + Evolution (4–5h)
- SMS/Push, batch default, schedule-default compat proof.
- Deliverable: compat test + provider matrix.

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| API minimality | ≤5 methods, role-named | Small | Bloated/leaky |
| Template/base | Hook-based, DRY | Works | Duplicated retry |
| Sealed/exhaustive | Compiler-checked | Complete | Default-abuse |
| Evolution | Default w/ compat test | Default only | Breaks impls |
| Doc/tests | Choice log + 16 | Present/10+ | Thin |

Pass ≥ 70. Stretch: ServiceLoader wiring; rate-limit decorator.
