# Mini Project: Kafka Integration

## What to build

This Kafka integration mini build produces a working museum clickstream pipeline you can run locally.
Scope stays deliberately small so every Kafka integration behavior remains observable.
Budget roughly one focused evening for the museum clickstream pipeline implementation.
Success means demonstrating Kafka integration judgment, not just compiling code.
Keep a lab journal noting each Kafka integration surprise encountered.
Resist adding features beyond the museum clickstream pipeline acceptance checks.

## Steps

1. Stream gallery click events into a partitioned topic for the service.
2. Scale intake with a consumer group of three members.
3. Commit offsets only after successful handling.
4. Keep each visitor session ordered by key.
5. Replay one hour of events into a fresh counter.

## Architecture in miniature

- Topics and partitions layout.
- Consumer groups for parallel intake.
- Offset commit discipline.
- Key-based ordering.
- Retention and replay.

## How it is judged

- [ ] 5000 click events land partitioned by gallery in the solution.
- [ ] Three-member group shares load with no idle member in the platform.
- [ ] Killing one member redelivers its events without loss.
- [ ] Session order intact across 50 sampled sessions.
- [ ] Replay rebuilds identical gallery counters.

## Extension

Choose one realistic complication and bolt it onto the project.
Write the two-paragraph retro: which Kafka integration decision proved hardest.
Walk a peer through the system while they read only the acceptance checks.
