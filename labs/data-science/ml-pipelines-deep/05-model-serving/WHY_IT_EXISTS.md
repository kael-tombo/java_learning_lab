# Model Serving - Why It Exists

Training produces weights on disk; products need answers at request time. Serving bridges that gap with interfaces, latency budgets, and versioned rollouts.

Without it, every team hand-rolls prediction plumbing: mismatched preprocessing, unversioned models, deploys without rollback. The failure mode is silent quality loss, not loud crashes.

Serving patterns exist because no single shape fits: scheduled scoring, interactive requests, and event streams need different latency and throughput contracts.

Versioned rollouts exist because models regress in ways unit tests miss; shadow and canary phases catch them on real traffic before full exposure.

Schemas exist because producers and consumers evolve independently. A versioned contract absorbs that drift; an unversioned one turns every change into coordinated downtime.

Warmup exists because fresh processes are slow: page faults, JIT, cache fills. Paying that cost before traffic arrives keeps p99 honest from the first request.

Prediction logs exist because incidents are otherwise unreplayable. Version plus inputs plus outputs reconstruct exactly what the user saw.

Resource sizing exists because weights and preprocessing compete for memory and CPU. Explicit sizing replaces hope with headroom at peak load.

## Why each guard exists

Batching caps exist because throughput greed is unbounded: without a cap the batch
grows until interactivity dies, and the formula shows exactly where that point is.
The cap converts a hardware temptation into a latency promise.

Canary discipline exists because small samples lie fluently: a z near 1 looks like
signal and is noise, and only predeclared share and duration keep teams from acting
on it. Peeking early manufactures false alarms out of arithmetic.

Readiness gating exists because liveness lies: a running process with cold weights
answers slowly and poisons the tail for exactly the users who arrived first. Only
warmed instances with passing sample scores earn traffic.

Versioned prediction logs exist because memory lies too: postmortems without
version-tagged inputs and outputs reconstruct a plausible incident, not the actual
one. Replayable logs turn archaeology into accounting.

## What serving refuses to do

Serving refuses to guess on invalid input: preprocessing failures return validation
errors rather than fabricated scores, because a guessed score corrupts silently
while an error routes loudly. Refusal is a feature with a log line.

Serving refuses shared anonymous timeouts: one budget across four legs hides which
leg slipped, so each leg owns its slice and its alert. Attribution precedes repair.

Serving refuses unversioned caches: a prediction stored without its model and schema
versions is a stale answer waiting for a confident delivery. Keys carry versions
or the cache does not exist.

Serving refuses silent schema evolution: renamed fields and changed units arrive as
new versions with explicit policy, never as quiet reinterpretations of old bytes.
Dual-serve windows absorb the migration; coordinated downtime is the failure mode
being retired.
