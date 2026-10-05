# Real-World Project — Deep Serialization (serialization-deep)

Production-style build around Java native, Jackson, Avro, Protobuf, versioning: design, scale, operate.

## Problem statement
Design a service/demo where Serializable & serialVersionUID, Externalizable, Jackson databind are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `Serializable & serialVersionUID` → component + owner + SLO.
- `Externalizable` → component + owner + SLO.
- `Jackson databind` → component + owner + SLO.
- `Avro schemas` → component + owner + SLO.
- `Protobuf` → component + owner + SLO.

## Milestones (4)
1. Slice: happy path + test.
2. Harden: timeouts, retries, validation.
3. Observe: logs/metrics/JFR + dashboard.
4. Scale: benchmark + tune one bottleneck.

## Ops checklist
- [ ] Dockerfile + health check
- [ ] Load test (k6/JMeter) with p99
- [ ] Runbook: top-3 failures + mitigations

## Interview story
Prepare STAR: problem → approach → metric → lesson.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/io/Serializable.html
- https://docs.oracle.com/en/java/javase/17/docs/specs/serialization/
- https://openjdk.org/jeps/198 (JSON API discussion)

## Deliverables
- Repo + tests + benchmark + 1-page ops note.
Extension 0: scale Serializable & serialVersionUID under load.
Extension 1: scale Externalizable under load.
Extension 2: scale Jackson databind under load.
Extension 3: scale Avro schemas under load.
Extension 4: scale Protobuf under load.
Extension 5: scale versioning & compatibility under load.
Extension 6: scale security of deserialization under load.
Extension 7: scale performance tradeoffs under load.
Extension 8: scale Serializable & serialVersionUID under load.
Extension 9: scale Externalizable under load.
Extension 10: scale Jackson databind under load.
Extension 11: scale Avro schemas under load.
Extension 12: scale Protobuf under load.
Extension 13: scale versioning & compatibility under load.
Extension 14: scale security of deserialization under load.
Extension 15: scale performance tradeoffs under load.
Extension 16: scale Serializable & serialVersionUID under load.
Extension 17: scale Externalizable under load.
Extension 18: scale Jackson databind under load.
Extension 19: scale Avro schemas under load.
Extension 20: scale Protobuf under load.
Extension 21: scale versioning & compatibility under load.
Extension 22: scale security of deserialization under load.
Extension 23: scale performance tradeoffs under load.
Extension 24: scale Serializable & serialVersionUID under load.
Extension 25: scale Externalizable under load.
Extension 26: scale Jackson databind under load.
Extension 27: scale Avro schemas under load.
Extension 28: scale Protobuf under load.
Extension 29: scale versioning & compatibility under load.
Extension 30: scale security of deserialization under load.
Extension 31: scale performance tradeoffs under load.
Extension 32: scale Serializable & serialVersionUID under load.
Extension 33: scale Externalizable under load.
Extension 34: scale Jackson databind under load.
Extension 35: scale Avro schemas under load.
Extension 36: scale Protobuf under load.
Extension 37: scale versioning & compatibility under load.
Extension 38: scale security of deserialization under load.
Extension 39: scale performance tradeoffs under load.
Extension 40: scale Serializable & serialVersionUID under load.
Extension 41: scale Externalizable under load.
Extension 42: scale Jackson databind under load.
Extension 43: scale Avro schemas under load.
Extension 44: scale Protobuf under load.
Extension 45: scale versioning & compatibility under load.
Extension 46: scale security of deserialization under load.
Extension 47: scale performance tradeoffs under load.
Extension 48: scale Serializable & serialVersionUID under load.
Extension 49: scale Externalizable under load.
Extension 50: scale Jackson databind under load.
Extension 51: scale Avro schemas under load.
Extension 52: scale Protobuf under load.
Extension 53: scale versioning & compatibility under load.
Extension 54: scale security of deserialization under load.
Extension 55: scale performance tradeoffs under load.
Extension 56: scale Serializable & serialVersionUID under load.
Extension 57: scale Externalizable under load.
Extension 58: scale Jackson databind under load.
Extension 59: scale Avro schemas under load.
Extension 60: scale Protobuf under load.
Extension 61: scale versioning & compatibility under load.
Extension 62: scale security of deserialization under load.
Extension 63: scale performance tradeoffs under load.
Extension 64: scale Serializable & serialVersionUID under load.
Extension 65: scale Externalizable under load.
Extension 66: scale Jackson databind under load.
Extension 67: scale Avro schemas under load.
Extension 68: scale Protobuf under load.
Extension 69: scale versioning & compatibility under load.
Extension 70: scale security of deserialization under load.
Extension 71: scale performance tradeoffs under load.
Extension 72: scale Serializable & serialVersionUID under load.
Extension 73: scale Externalizable under load.
Extension 74: scale Jackson databind under load.
