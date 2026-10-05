# MINI PROJECT — String Handling: High-Throughput Template + CSV Service

## Goal (2 weeks, ~8–10h)
Build a `template-service` that renders personalized messages from templates
plus a hardened CSV ingester — correct Unicode, zero charset bugs, and no
allocation blowups at 1M rows.

## Requirements
### Functional
1. Template engine: `Template(name, body)` with `{{placeholders}}`, defaults
   (`{{name|Guest}}`), conditionals (`{{#if premium}}`), loaded from files.
2. CSV ingester: parse `users.csv` (name,email,locale,plan) handling quoted
   commas, embedded newlines, BOM, mixed encodings (UTF-8/UTF-16 detect).
3. i18n: `ResourceBundle` messages per locale; `Normalizer` + trim on names;
   email validation with ONE precompiled `Pattern` (length-capped).
4. Render pipeline: `StringBuilder` pooling/recycling, `String.join` for lists,
   text blocks for fixtures; never `+` inside hot loops.
5. CLI: `render --template welcome --csv users.csv --out out/` producing one
   file per user + a summary report (`rendered, skipped, errors`).

### Non-functional
- Explicit `StandardCharsets` on every byte<->String edge; `Objects.equals`
  for nullable compares; no `new String(bytes)` without charset.
- 20+ tests: quoted CSV, BOM, emoji/code-point names, null placeholders,
  regex-reuse (verify single `Pattern.compile`), golden-file renders.
- Benchmark: render 100k messages; report throughput + allocations.
- README: encoding policy + builder-vs-plus decision + regex note.

## Phases
### Week 1 — Engine + Ingester (4–5h)
- Steps: model `Template/Placeholder`; placeholder resolver; CSV reader
  with quote/newline/BOM handling; email pattern; ResourceBundle setup.
- Deliverable: CLI renders 1k users correctly, golden files green.

### Week 2 — Scale + Harden (4–5h)
- Steps: capacity-hinted builders; 100k-run timing; malformed-row
  quarantine (`errors.csv`); fuzz with emoji/long fields; fix hotspots.
- Deliverable: benchmark table + quarantine sample + final report.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–15) | Fail (<12) |
|-----------|----------------|--------------|------------|
| Correctness | Golden files, BOM/quotes/emoji pass | Basics pass | Charset/quote bugs |
| Builder discipline | No hot-loop `+`, capacity hints | Mostly clean | O(n^2) concat |
| Encoding/i18n | Explicit charset everywhere + bundles | Mostly explicit | Bare `getBytes()` |
| Validation | Precompiled capped regex + fuzz | Regex present | Recompiled/DoS-prone |
| Tests + bench | 20+ tests + timed 100k run | 12+ tests | Happy-path only |

Pass >= 70. Stretch: `STR.` string templates (JDK 21+); streaming render
with `Files.lines(charset)`; JFR allocation-diff memo.
