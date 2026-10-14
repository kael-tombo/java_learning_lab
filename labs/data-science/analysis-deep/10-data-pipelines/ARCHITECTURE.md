# Architecture - Pipeline Mini-Toolkit

JDK-only layout (package com.pipelab):

```
Record    - key + eventTime + fields; validation at construction
Landing   - raw append-only staging per batch (never mutated)
Checks    - row counts, null rates, drift vs reference
Sink      - LinkedHashMap keyed upsert (the idempotent fixed point)
Schema    - required-field set + types; subset-compat verdicts
Dag       - extract/validate/transform/serve nodes with retry counts
```

## Data flow

Source -> Landing (raw) -> Checks (gate) -> transform -> Sink (merge by
key). Schema gates every edge; Dag orders nodes and isolates failures
per node with the node name attached to every page.

## Design choices

- Landing immutable: transforms read staging, write new structures -
  replay reruns the same pure functions over the same bytes.
- Sink.merge is the only write path; direct put is package-private so
  no caller can smuggle a blind overwrite past review.
- Checks return pass/quarantine verdict objects carrying the numbers,
  so pages include evidence, not just alarms.
- Dag is acyclic by construction (topological order at build; cycles
  throw) - no runtime cycle can form.

## Boundaries

No distributed transport here: the lab models semantics (keys, merges,
compat) that any transport needs. Streaming windows appear as pure
functions over lists, transport-agnostic by design.

## Record sketches

```java
record Batch(String id, List<Record> rows) {}
record CheckVerdict(boolean pass, long rows, double nullRate, double drift) {}
```

Batch is immutable on landing; CheckVerdict carries evidence with the
pass/fail bit so pages quote numbers, never bare alarms.

## Failure routing

Failed nodes quarantine output and page with node name and contract
breach. Downstream nodes never read partial writes - they wait on the
contract, which a failed node cannot satisfy by construction.
