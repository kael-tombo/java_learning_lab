# Mini Project: Messaging Fundamentals

## Moving parts

- Queues versus topics distinction supporting the clinic notification fan-out.
- At-least-once delivery handling supporting the clinic notification fan-out.
- Idempotent consumer design.
- Poison-message isolation.
- Ordering guarantees per channel.

## Build brief

This messaging fundamentals mini build produces a working app you can run locally.
Scope stays deliberately small so every messaging fundamentals behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating messaging fundamentals judgment, not just compiling code.
Keep a lab journal noting each messaging fundamentals surprise encountered.
Acceptance checks define the edge, and no additions go past them.

## Sequence

1. Publish appointment reminders to both queue and topic channels for the service.
2. Make the reminder consumer safe under duplicate delivery.
3. Isolate one malformed reminder without halting the flow.
4. Preserve per-patient ordering across 20 reminders.
5. Measure redelivery behavior after a consumer restart.

## Done when

- [ ] 100 reminders reach every subscribed channel in the solution.
- [ ] Duplicate delivery of 20 messages changes nothing in the platform.
- [ ] Malformed message quarantined within 3 attempts.
- [ ] Per-patient order holds across all 20 sequences.
- [ ] Restart loses zero reminders.

## If time remains

The project gains exactly one realistic complication, chosen by you.
Write the two-paragraph retro: which messaging fundamentals decision proved hardest.
Walk a peer through the system while they read only the acceptance checks.
