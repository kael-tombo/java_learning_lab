# VISION — Serialization (Java, JSON, Binary)

## Vision Statement
**Serialization is a versioned contract across time and teams** — schema-first
formats, explicit versioning, and allowlisted deserialization keep rolling
upgrades safe and attackers out of your `readObject`.

---

## Mental Models
### 1. Bytes Are a Promise
Every serialized form must be readable by N and N+1. Add optional fields,
never rename/repurpose; test old→new and new→old golden files.
### 2. Java Native Ser Is Dangerous
`Serializable` + `readObject` executes object graphs — gadget chains exploit
it. Prefer JSON/Protobuf/Avro; if native, use filters
(`ObjectInputFilter`) + `serialVersionUID` + `readResolve` guards.
### 3. Jackson Is Configuration
`ObjectMapper` singleton, `FAIL_ON_UNKNOWN_PROPERTIES` policy, `@JsonCreator`
+ `@JsonValue` for enums, `JavaTimeModule` for dates, allowlist polymorphic
types (`activateDefaultTyping` is a loaded gun).
### 4. Binary Wins at Scale
Protobuf/Avro give compact bytes + schema registry + codegen; JSON wins for
humans/debug. Measure payload + CPU, not fashion.

---

## Decision Framework
| Question | Rule |
|----------|------|
| New API/event? | Schema-first (Protobuf/Avro or JSON Schema) |
| Java-native ser? | Avoid; filter + allowlist if forced |
| Unknown JSON fields? | Fail in strict services, ignore at edge with log |
| Dates? | ISO-8601 strings, never epoch guesswork |
| Version bump? | Golden-file compat test both directions |

---

## Career Trajectory
- **L1:** Jackson basics, `serialVersionUID`, ISO dates, unknown-field policy.
- **L2:** Versioning strategy, polymorphic allowlists, custom ser/deser.
- **L3:** Schema registry, Protobuf/Avro migration, compat gates in CI.
- **L4:** Event-schema governance (org-wide compat policy).

---

## 4-Week Path
```
W1: Jackson config, records + JavaTime, unknown-field matrix.
W2: Java ser risks, filters, readObject guards (exploit demo safe).
W3: Protobuf/Avro lab, schema evolution (add/remove field).
W4: Order-event compat capstone (golden files + registry check).
```
## Success Metrics
- [ ] Golden compat tests pass both directions
- [ ] Deserialization filter blocks gadget payload
- [ ] Unknown-field + date policy documented and tested
