# MINI PROJECT — Java Syntax: CLI Expense Tracker

## Goal (2 weeks, ~8–10h)
Build a compilable, well-packaged CLI app using only core syntax: packages, classes, loops, conditionals. No build tool required (javac/java).

## Requirements
### Functional
1. `add <amount> <category> <note>` stores entry; `list` prints table; `total [--category X]` sums; `help`/`exit`.
2. Input loop with `Scanner`; parse args with `String.split` (limit) + validation.
3. Packages: `com.tracker.{model,service,cli}`; one public class per file.
4. Persist to CSV file (`expenses.csv`) with UTF-8; reload on start.
### Non-functional
- Compiles with `javac -d out $(find src -name "*.java")`; runs with `java -cp out`.
- Zero magic strings for commands (constants); Google-Java-Style-ish formatting.
- README with compile/run commands + 3 sample sessions.

## Phases
### Week 1 — Skeleton + Loop (4–5h)
- Day 1–2: packages, `Expense` model, `ExpenseStore` (in-memory list).
- Day 3–4: CLI loop, command parsing, `list`/`total`; JShell-prototype tricky parsing.
- Deliverable: runs in-memory, demo script passes.
### Week 2 — Persistence + Polish (4–5h)
- Day 5–6: CSV save/load, malformed-line handling (skip + warn).
- Day 7–8: constants, help text, README, 5 manual test cases.
- Deliverable: jar via `jar --create`, sample `expenses.csv`.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (9–10) | Pass (6–8) | Fail (<6) |
|-----------|------------------|------------|-----------|
| Packages/compiles CLI-only | Clean layout, one cmd build | Builds with notes | IDE-only |
| Command parsing | Validated, helpful errors | Basic works | Crashes on bad input |
| Persistence | UTF-8 round-trip, tolerant | Saves/loads happy path | Data loss |
| Readability | Named consts, small methods | Mostly clear | Monolith main |
| README/demo | Repro in 3 cmds | Repro with help | Missing |

Pass ≥ 70. Stretch: `monthly-report` command; `export --format tsv`.
