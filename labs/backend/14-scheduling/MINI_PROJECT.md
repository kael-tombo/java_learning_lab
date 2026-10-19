# Mini Project: Scheduling

## What to build

This scheduling mini build produces a working bakery nightly-job rack you can run locally.
Scope stays deliberately small so every scheduling behavior remains observable.
Budget roughly one focused evening for the bakery nightly-job rack implementation.
Success means demonstrating scheduling judgment, not just compiling code.
Keep a lab journal noting each scheduling surprise encountered.
Stick to the acceptance checks and refuse scope that runs beyond them.

## Steps

1. Schedule nightly dough-report and weekly supplier-order jobs for the service.
2. Pick fixed-rate or fixed-delay deliberately per job.
3. Make the supplier order safe to rerun after a crash.
4. Prevent overlapping report runs with a lock.
5. Recover gracefully from one simulated missed run.

## Architecture in miniature

- Cron expression scheduling.
- Fixed-rate versus fixed-delay.
- Job idempotency on rerun.
- Overlap prevention with locks.
- Missed-run recovery.

## How it is judged

- [ ] Both jobs fire on schedule across a 48-hour observation in the solution.
- [ ] Rate-versus-delay choice documented per job in the platform.
- [ ] Rerun after crash creates zero duplicate orders.
- [ ] Overlapping trigger attempt logged as skipped, not doubled.
- [ ] Missed run recovered with a written audit entry.

## Extension

Grow the project by adding one realistic complication you select.
Write the two-paragraph retro: which scheduling decision proved hardest.
Demo time: the peer sees the system with just the acceptance checks as the guide.
