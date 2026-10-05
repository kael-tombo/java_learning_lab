# VISION — String Handling

## Vision Statement
**Strings are immutable values, not buckets of chars** — master immutability,
encoding, and builder discipline so text code is correct at scale and fast
under load, from CSV parsing to template rendering.

---

## Mental Models
### 1. Immutability + Sharing
`String` is final, `char[]/byte[]` never exposed. Concatenation creates new
objects; `==` compares identity, `equals` compares value. `intern()` trades
heap for PermGen/Metaspace-era pool pressure — use rarely.
### 2. Encoding Is the Contract
`UTF-16` internally (compact strings use Latin-1/UTF-16); bytes on the wire
need an explicit `Charset` (`UTF_8`). `getBytes()` without charset is a bug
factory across OS locales. Length in chars != length in code points.
### 3. Builder vs Plus vs Template
Loop `+` is O(n^2); `StringBuilder` (single-thread) / `StringBuffer`
(synchronized, legacy) amortize appends. `String.join`, `String.format`,
`MessageFormat`, and text blocks (`"""`) each fit one job — pick deliberately.
### 4. Regex + Parsing Cost
`Pattern` compile once, reuse; `String.split` recompiles each call. Regex
backtracking can DoS untrusted input — prefer precompiled patterns, limits,
or a real parser (`Scanner`, CSV lib) for structured data.

---

## Decision Framework
| Question | Rule |
|----------|------|
| Concatenate in loop? | `StringBuilder` with capacity hint |
| Compare strings? | `equals`, never `==`; `Objects.equals` for nulls |
| Bytes <-> String? | Always pass `StandardCharsets.UTF_8` |
| Format a message? | Text blocks + `formatted`/`StringTemplate` over `+` chains |
| Validate input? | Precompiled `Pattern`, length caps, normalize first |

---

## Career Trajectory
- **L1:** `equals/split/join`, `StringBuilder`, text blocks, charset basics.
- **L2:** Regex tuning, Unicode (code points, normalization), CSV/i18n handling.
- **L3:** Allocation profiling (JFR), pooling/interning policy, parser design.
- **L4:** Text-pipeline architecture (templating, localization at scale).

---

## 4-Week Path
```
W1: Immutability, equals/hashCode, builder, join/format, text blocks.
W2: Charsets, UTF-8 I/O, code points, Normalizer, ResourceBundle i18n.
W3: Regex compile-reuse, split/join pitfalls, CSV parser kata.
W4: Allocation benchmark (JMH/JFR) + template-service capstone.
```
## Success Metrics
- [ ] Zero `==` string compares; explicit charset on every conversion
- [ ] Regex compiled once; 1M-row parse without O(n^2) blowup
- [ ] JFR shows string-alloc reduction with builder/join fix
