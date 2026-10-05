# REAL-WORLD PROJECT — Serialization: Rolling Upgrade Poisons Event Stream

## Incident Scenario
Order service v3 deploys alongside v2; v2 consumers crash-loop on new event
fields, v3 drops v2's unknown `giftWrap` flag silently, and a pentest pops
RCE via unfiltered Java deserialization on the admin import endpoint.

## Symptoms
- `UnrecognizedPropertyException: coupon` spikes on v2 pods during rollout.
- `InvalidClassException` / wrong `total` on mixed-version reads (renamed field).
- Admin `/import` accepts raw Java-serialized blob; CPU 100% on one payload.
- Protobuf consumers get JSON-mapped protos with dropped unknown fields.
- No golden files; `ObjectMapper` built per call with default settings.

## Investigation Tasks
1. Protect prod: `jcmd <pid> Thread.print` on pegged import pod; capture
   `jcmd <pid> JFR.start duration=60s filename=ser.jfr` (CPU + alloc).
2. Heap: `jcmd <pid> GC.heap_dump` — dominators for `ObjectMapper`,
   `byte[]` event backlog, deserialized gadget graph on import pod.
3. JFR alloc: `jdk.ObjectAllocationInNewTLAB` showing per-call mapper +
   `char[]` churn; `jdk.JavaExceptionThrow` for ser exceptions by type.
4. Log diff: `grep -E "UnrecognizedProperty|InvalidClass|MismatchedInput" app.log
   | sort | uniq -c`; correlate with deploy timeline.
5. Wire capture: save 100 raw events (v2+v3); replay old→new, new→old in
   staging — record exact drop/crash per field.
6. Import audit: `grep -rn "ObjectInputStream\|readObject\|enableDefaultTyping" src/`;
   craft inert gadget proof (sleep/DNS, never RCE) for the filter test.
7. Config audit: list every `new ObjectMapper` and date/unknown-field setting.

## Root Cause
Unversioned breaking changes (renamed field, required new field) + strict
parsers with no compat policy + Java-native deserialization unfiltered +
per-call mapper waste — evolution and security both unowned.

## Resolution
- Immediate: pause rollout; tolerant v2 hotfix (ignore-unknown + log),
  disable Java-ser import (reject blobs), pin event version header.
- Short-term: additive-only schema, `eventVersion` + downgrade path,
  shared mapper (strict core / tolerant edge), `ObjectInputFilter` allowlist,
  golden files both directions in CI.
- Long-term: Protobuf/Avro + registry `BACKWARD` gate, schema council,
  deserialization allowlist lint, payload/CPU budget.

## Runbook
```
1. Thread.print + JFR + heap_dump on import pod; block ser endpoint.
2. Hotfix tolerant-read; verify mixed-version errors -> 0.
3. Land golden compat + additive-schema gate; re-roll gradually.
4. Re-enable import on JSON/allowlist only; pentest re-run.
5. Postmortem: evolution rules + filter policy.
```

## Metrics
- Mixed-version error rate = 0; golden compat 100% both directions.
- Java-ser endpoint removed/filtered; gadget payload 100% blocked.
- Mapper singletons; event alloc/CPU within budget (bench in README).

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- Serializable API: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/Serializable.html
- Serialization spec: https://docs.oracle.com/en/java/javase/21/docs/specs/serialization/index.html
