# VISION — Arrays & Strings

## Vision Statement
**Handle sequences without fear** — know when data is fixed (`array`), textual (`String`), or mutable (`StringBuilder`), and never pay O(n²) for concatenation again.

---
## Mental Models
### 1. Array = Fixed Contiguous Block
Length fixed at birth; `ArrayIndexOutOfBounds` = contract violation. Prefer `List` unless perf/interop demands arrays.
### 2. String Immutability Dividend
Immutable → thread-safe, hashable, poolable. Concatenation in loop creates garbage; use `StringBuilder`.
### 3. Pool vs Heap
Literals interned; `new String()` bypasses pool. Compare with `.equals()`, never `==`.
### 4. Text Blocks + Encoding
`"""` blocks preserve layout; files are bytes — always specify `StandardCharsets.UTF_8`.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Building string in loop? | `StringBuilder` (single thread) |
| Fixed-size primitives? | Array; else `ArrayList` |
| Splitting/parsing? | `split` with limit; validate length |
| User text? | Normalize + validate encoding early |

---
## Career Trajectory
- **L1:** index safely, loop, `.equals` correctly.
- **L2:** Builder/joiner, text blocks, `Arrays` utilities.
- **L3:** encoding bugs, regex perf, large-text streaming.
- **L4:** i18n standards, input-validation policy.

---
## 4-Week Path
```
W1: Arrays, 2D arrays, Arrays.sort/binarySearch.
W2: String API, equals, immutability demos.
W3: Builder, joiner, format, text blocks, regex basics.
W4: CSV-parser kata with UTF-8 + edge-case tests.
```
## Success Metrics
- [ ] Prove O(n²) concat vs Builder with JMH/microbench
- [ ] Handle UTF-8 round-trip without mojibake
- [ ] Zero index-out-of-bounds in fuzz test
