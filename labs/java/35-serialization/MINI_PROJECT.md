# MINI PROJECT — Serialization: Versioned Order Events

## Goal (2 weeks, ~8–10h)
Build an `order-events` library publishing v1→v3 order events over JSON and
Protobuf with golden-file compat tests and a hardened deserialization path.

## Requirements
### Functional
1. Model: `OrderEvent` records (v1: id/items/total; v2: +coupon optional;
   v3: +split-payments) with explicit `eventVersion` field.
2. Jackson: shared `ObjectMapper` (singleton, `JavaTimeModule`, ISO dates);
   `FAIL_ON_UNKNOWN_PROPERTIES=false` at edge + `true` in strict core;
   `@JsonCreator` factories, enum `@JsonValue` codes.
3. Protobuf: `order_event.proto` with `optional` additions only; codegen;
   JSON↔Proto bridge preserving unknown fields on passthrough.
4. Compat: `src/test/resources/golden/v1/*.json` readable by v3 parser and
   v3→v1 downgrade tested (unknown fields dropped + logged, no crash).
5. Java-ser hardening: if any `Serializable` remains, `serialVersionUID` +
   `ObjectInputFilter` allowlist demo + gadget-payload rejection test.
6. Registry check: script asserting only additive `.proto` diffs (no renames).

### Non-functional
- 20+ tests: golden both-directions, tamper/unknown-field matrix, date
  shapes, filter-blocked payload, size/CPU bench JSON vs Proto.
- Benchmark: 100k serialize/deserialize each format; README table.
- README: evolution rules (add-optional-only) + downgrade policy.

## Phases
### Week 1 — JSON + Versioning (4–5h)
- Steps: mapper config, v1–v3 models, golden files, strict/edge policies.
- Deliverable: golden compat green.

### Week 2 — Binary + Hardening (4–5h)
- Steps: proto codegen, bridge, filter demo, bench, registry script.
- Deliverable: compat report + bench table.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Versioning | Additive-only + both-direction proof | One direction | Breaks old |
| Jackson | Singleton + policy matrix tested | Works | New mapper/call |
| Protobuf | Schema + bridge correct | Present | Hand JSON as "proto" |
| Security | Filter + tamper tests | Mentioned | Unfiltered ser |
| Bench+docs | 100k numbers + rules doc | Timed | Missing |

Pass >= 70. Stretch: Avro + Schema Registry compat (`BACKWARD` check);
JFR allocation diff JSON vs Proto; fuzz corpus on parsers.
