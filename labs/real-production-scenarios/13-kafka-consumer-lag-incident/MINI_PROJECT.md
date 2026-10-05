# Lab 13 — Mini Project: Reproduce + Detect + Fix Lag

## Objective
Run Kafka locally (Docker), create lag with a slow consumer + poison pill, then fix — ~60 minutes.

## Part 1 — Reproduce (20 min)
1. `docker compose up -d kafka` (KRaft or ZooKeeper image); create topic: `kafka-topics.sh --create --topic orders --partitions 3 --replication-factor 1`.
2. Produce 10k msgs fast (`kafka-producer-perf-test.sh`).
3. Start a slow consumer (sleep 50ms/msg) in one terminal; watch `--describe` lag climb.
4. Inject poison pill (malformed JSON at offset N); show infinite-retry + lag stall.

## Part 2 — Detect (20 min)
1. Script `lag_watch.sh` polling `--describe` every 10s, logging sum + per-partition.
2. Compute growth rate (Δlag/Δt) and ETA to 100k backlog.
3. Build a simple chart (CSV → plot) of lag vs consume rate.
4. Add a fake alert: echo PAGE when sum > 5k for 3 consecutive polls.

## Part 3 — Fix (20 min)
1. Implement bounded retry (3×) + DLQ topic `orders.DLT` in consumer code.
2. Scale consumers 1→3 (== partitions); measure drain rate improvement.
3. Try 6 consumers; prove 3 idle (no gain) from assignment output.
4. Document runbook: describe → hot-vs-uniform → scale-or-DLQ — each with copy-paste command.

## Deliverables
- `lag_watch.sh`, lag CSV + chart, consumer code with DLQ, runbook, drain-rate numbers.
- Success: lag reproduced, detected via script, drained after fix with proof.

## Grading
- Reproduce (30%), Detect/script + analysis (35%), Fix + runbook (35%).
