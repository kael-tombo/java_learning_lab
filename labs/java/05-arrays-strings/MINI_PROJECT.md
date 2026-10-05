# MINI PROJECT — Arrays & Strings: CSV Analyzer

## Goal (2 weeks, ~8–10h)
Build a UTF-8 CSV parser + column-stats tool proving array/String mastery: no regex-injection, no O(n²) concat, correct quoting.

## Requirements
### Functional
1. Parse RFC-4180 subset: quoted fields, escaped `""`, embedded commas/newlines; `split` with limit only where safe.
2. Stats: per-column distinct count, max length, numeric avg (arrays + `Arrays.sort` for median).
3. Report builder with `StringBuilder`/`StringJoiner`; text-block email template output.
4. CLI: `analyze file.csv --col 2` prints table; exit codes 0/2 (usage)/3 (bad data).
### Non-functional
- Handles 50k-line file < 3s; memory via streaming (no full `String` concat in loop).
- 15+ tests: quotes, empty fields, UTF-8 (emoji/accents), CRLF, trailing comma.
- `.equals` everywhere; zero `==` on Strings (review check).

## Phases
### Week 1 — Parser (4–5h)
- Char-array state machine (IN_QUOTE/ESCAPE), row → `String[]`.
- Deliverable: adversarial CSV suite passing.
### Week 2 — Stats + Report (4–5h)
- Column stats, Builder report, CLI, perf timing doc.
- Deliverable: sample report + benchmark note (concat vs Builder).

## Evaluation Rubric (100 pts)
| Criterion | Excellent | Pass | Fail |
|-----------|-----------|------|------|
| Quoting correctness | Full subset + tests | Basic quotes | Breaks on comma-in-quote |
| Encoding | UTF-8 explicit everywhere | Works by luck | Mojibake |
| Perf | Streaming, timed proof | Acceptable | O(n²) concat |
| Tests | 15+ incl. UTF-8/edge | 10+ | Happy only |
| CLI/report | Clean table + codes | Works | Unclear output |

Pass ≥ 70. Stretch: `--json` output; malformed-row recovery report.
