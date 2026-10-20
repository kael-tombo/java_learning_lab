# AI Safety & Alignment — Exercises

Run on JDK 21+, `javac --release 21 -encoding UTF-8`. Treat all toy truths as
simulations; write-ups are graded on scoping, not conviction.

## 1. Reproduce both sweeps

Get Snippet 1 (threshold table) and Snippet 2 (proxy-gap rows) to match the documented
observed outputs character-for-character, recompile, and record the exact commands. Any
row that fails, explain which constant you mis-typed.

## 2. Threshold economics

Insert scores `0.55, 0.45` with correctness `1, 1` (seven rows total) and rerun the
sweep. Where does answered-accuracy stop improving as coverage falls? Report the new
table and a one-sentence policy claim: which threshold would you pick for a desk with
human triage, and which for a headless pipeline? Justify each from the printed rows.

## 3. Proxy-gap variants

Edit Snippet 2's constants to three new cases: (a) score ties `(0.5, 0.5, truth 1/0)`,
(b) a candidate pair where the model score and truth AGREE `(0.2, 0.9, truth 0/1)`,
(c) truth ties. Report the two accuracy columns for each scenario and write which of the
three settings most resembles a real preference modelling failure pattern — citing your
table, not intuition.

## 4. Abstention with escalation

Extend Snippet 1 with a band between `0.6 <= t < 0.9` labeled "route to human": print a
three-way table (`auto-answer / escalate / refuse`) per threshold value. The route bucket
must account rows whose scores fall just below the current threshold. Report routing
volume at each setting; state assumptions in comments (score meaning, upstream
classifier).

## 5. Reward report card

Write `SituationCards` printing three rows: the object being optimized in each scenario
(reward model score, answered-set accuracy, human-triage throughput), the 2nd-order
signal you would watch to catch divergence (sycophancy counts, coverage drop, triage
backlog), and one escalation clause per row. Nothing numeric is required beyond snippet
outputs; the point is the discipline of naming watchers before shipping.

## Writing requirements for the folder

Every claim about AI behavior must carry one of three tags in your notes:
`simulated` (from your sandbox), `operational` (about your guard code only), or
`uncertain-literature` (concept-level, no numbers). Untagged claims get cut in review.
