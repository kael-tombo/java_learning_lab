# Model Training Pipelines — Why It Exists

Training pipelines exist because manual retraining does not survive
contact with production. A notebook that worked once depends on the
analyst's memory of which data, which code, and which seed — none of
which is recorded. When metrics shift, nobody can say whether the data,
the code, or chance moved them. When bad data arrives, nothing stops
it from becoming a bad model. When the test set quietly changes between
runs, every comparison becomes meaningless while looking rigorous.

The staged pipeline replaces memory with mechanism: versioned inputs,
gated validation, recorded seeds, and registered outputs. Each piece
answers one audit question — what data, what checks, what code, what
result — so retraining becomes an operation the team can run, monitor,
and defend, instead of a ritual one person performs. The alternative is
not "simpler ML"; it is untraceable ML, where every incident ends in
argument rather than evidence.

A pipeline is also a contract with future teammates: the DAG in this
lab's demo declares that register depends on both train and evaluate,
so no artifact can ship without passing through measurement — a rule
the structure enforces even when schedule pressure tempts shortcuts.

Without it, the failure mode is always the same shape: a metric moves,
three candidate causes (data, code, chance) are all unlogged, and the
postmortem concludes "we need better monitoring" without ever producing
the records that monitoring would have read. Pipelines are that record
by construction, not by afterthought. That is the whole of it: evidence
instead of argument, every retrain, as a side effect of running the work.
Start there: version the inputs before optimizing anything else.
