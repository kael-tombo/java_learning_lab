# VISION — On-Call Excellence for High CPU

## 1. Future State
High-CPU pages arrive with the culprit frame already attached. Flame graphs are one click from the alert, hot-thread mapping is automated, and bad regexes / spin loops never reach prod because profiling gates block them.

## 2. What Good Looks Like
- Continuous profiling (async-profiler / Pyroscope) always on with <1% overhead.
- Alert includes top-3 frames + pod + deploy correlation, not just "CPU >90%".
- CPU limits right-sized from flame data; throttle alerts separate from hot-thread alerts.

## 3. Behaviors
Profile-before-guess discipline, compare CPU vs wall flames to avoid chasing blocked threads, blameless focus on code path not "noisy neighbor".

## 4. Anti-Vision
Restart-and-pray, blindly raising CPU limits, killing -9 without a 60s profile, blaming the platform for an app loop.

## 5. Commitment
This week: run one 60s async-profiler capture on your hottest service and share the flame. Next: add continuous profiling + hot-frame alert annotation.

> Excellence = every CPU page names the method, not just the machine.
