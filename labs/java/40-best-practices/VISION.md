# VISION — Best Practices (Effective Java, Clean Code)

## Vision Statement
**Write code a stranger can delete safely** — Effective Java rules plus
clean-code habits are one system: correctness, readability, and API
discipline that survives team turnover and JDK upgrades.

---
## Mental Models
### 1. API as Contract
Every public type is a promise. Minimize accessibility, favor
immutability, document preconditions. Bloch Item 15–19 in one line.
### 2. Failure Is a Design Choice
Checked vs unchecked vs Optional vs Result: pick by caller recovery
ability, never by habit. Fail fast with informative exceptions.
### 3. Resources Have Owners
try-with-resources, explicit close, no finalizers/cleaners except as
safety net. Ownership must be visible in the signature.
### 4. Readability Compounds
Naming, 15-line methods, no magic numbers, static factories with names.
The reader's working memory is the real constraint.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Builder vs constructor? | >3 params or optional → builder |
| Optional return? | Return Optional, never take it as param |
| Inheritance? | Composition first; design-and-document or prohibit |
| Utility class? | Final + private ctor + static methods only |
| Equals/hashCode? | Value type → override both + toString |

---
## Career Trajectory
- **L1:** Naming, formatting, try-with-resources, equals/hashCode.
- **L2:** Immutables, builders, defensive copies, exception taxonomy.
- **L3:** API design reviews, generics bounds, concurrency-safe publishing.
- **L4:** Org-wide baselines: ArchUnit rules, Error Prone, review culture.

---
## 4-Week Path
```
W1: Items 1–20 kata — builders, immutables, try-with-resources.
W2: Generics + lambdas/streams discipline + Optional policy.
W3: API-design review of a real module; ArchUnit + Error Prone gates.
W4: Legacy cleanup sprint — measure warnings, complexity, test delta.
```
## Success Metrics
- [ ] Zero Error Prone ERRORs; ArchUnit API rules green
- [ ] try-with-resources on every Closeable path
- [ ] New APIs ship with immutability + documented preconditions
- [ ] Review checklist adopted by one teammate

## What This Is Not
Style trivia. It is defect prevention with numbers attached.

> Mantra: **Make illegal states unrepresentable and correct use easy.**
