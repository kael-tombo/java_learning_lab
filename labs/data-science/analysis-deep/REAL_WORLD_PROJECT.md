# Analysis Deep — Real-World Project: Reproducible Analysis Service

Build a refreshable analysis pipeline over a periodically updated open
dataset (e.g., transit ridership, weather observations, public budgets):
scheduled ingest with schema checks (lab 10 discipline), a wrangling
stage with logged rejects, EDA notebooks or scripts that rerun cleanly,
and a standing one-page brief regenerated on each refresh.

Acceptance: a reviewer can delete all outputs, rerun one command, and
get byte-identical tables and charts; a schema change in the source
fails loudly at the validation gate instead of silently shifting
numbers; the brief carries counts, caveats, and a changelog entry per
refresh. Operate it for a month: the refresh log (what changed, what
broke, what was decided) is the actual deliverable — the charts are
proof it ran.
