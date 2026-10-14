# Data Wrangling - Why It Exists

## Real data arrives dirty

Sensors drop packets, respondents skip questions, operators type "3x" into
numeric fields, and batch jobs load the same file twice. Analysis tools
assume rectangular, typed, duplicate-free tables; raw feeds violate every
part of that contract. Wrangling exists to close the gap explicitly instead
of letting each analyst silently patch it a different way.

## Silent corruption is the default

Without a coercion grammar, `"N/A"` becomes zero or crashes a parser three
stages later. Without dedup keys, a double-loaded file doubles revenue.
Without a missingness model, dropping incomplete rows quietly selects a
subpopulation (any MNAR column) and biases every downstream estimate.
Each failure mode is silent: the program runs and the number is wrong.

## Reproducibility demands records

Two analysts given the same raw file must produce the same clean table, or
their results cannot be compared. That requires named rules (which fill,
which key, which fences) plus counts, not ad-hoc spreadsheet edits. The
wrangling stage is where reproducibility is won or lost.

## Cleaning is analysis, not janitor work

Choosing mean vs median fill, or deciding the 60.0 is an error versus a
discovery, changes conclusions. Those are statistical judgments, and they
belong in versioned, reviewed code with before/after summaries - which is
exactly what this lab practices on small checkable examples.

## The alternative is folklore

Without named rules, each team member cleans differently: one drops NaN,
one fills zero, one deletes the 60.0, and three irreconcilable dashboards
result. Wrangling as a written, versioned stage replaces folklore with a
single auditable recipe the whole team - and any reviewer - can rerun.

## The cost of skipping it

Every production incident cited above - doubled revenue, fabricated zeros,
deleted outages - traces to a cleaning judgment made implicitly. This lab
makes each judgment explicit on data small enough to check by hand.
