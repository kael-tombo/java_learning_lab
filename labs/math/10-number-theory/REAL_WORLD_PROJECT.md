# REAL_WORLD_PROJECT — Number Theory in Production: Token ID & Checksum Service
> Production use-case: unguessable, collision-checked public IDs.

## 1. Scenario
- Service: API issues public resource IDs with Luhn-style check digits and random prefixes.
- Constraint: IDs must be unguessable (≥128 bits entropy), typo-detecting, URL-safe.
- Choice: 128-bit random core + mod-97 check for human-typed IDs; base32 encoding.
- Data: `Id{prefix, randomBits, check}`.

## 2. Architecture
```
request → RNG (SecureRandom) → mod-97 check → base32 → id → registry
```
- Check digit validated at the edge before any DB lookup.
- Registry maps id→resource with unique index.

## 3. War-Story (plausible, representative)
- Incident: sequential IDs leaked customer counts to competitors.
- Symptom: traffic analytics showed scraping across the whole id space.
- Root cause: `id = auto_increment` exposed — order = enumeration.
- Fix: random 128-bit core; check digit added; scraping now infeasible.
- Lesson: number theory gives you both the entropy and the typo guard — use both.

## 4. Metrics (before → after, one quarter)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| scraped resources | ~40k/day | ~12/day | −99.97% |
| mistyped ID tickets | 210/mo | 18/mo | −91% |
| p99 id validation | 0.4ms | 0.5ms | ~same |
| entropy per id | ~20 bits | 128 bits | much stronger |

## 5. Prevention Checklist
- [ ] No sequential IDs in public URLs.
- [ ] Check digit validated before DB hits.
- [ ] SecureRandom everywhere; never `java.util.Random` for IDs.
- [ ] Length/format defense at the edge.
- [ ] Registry uniqueness enforced by DB constraint.
- [ ] Regression test: Luhn/mod-97 reference vectors.
- [ ] Document the ID format for client libraries.
- [ ] Dashboard: validation failures, ID issuance rate, collision retries (~0).

## 6. What "Good" Looks Like
- IDs unguessable, typos caught at the edge, no enumeration possible.

## 7. Stretch
- Graduate to RSA-based signed tokens (see 01-arithmetic real-world for crypto primitives).

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Modular arithmetic: https://en.wikipedia.org/wiki/Modular_arithmetic
- Luhn algorithm: https://en.wikipedia.org/wiki/Luhn_algorithm
