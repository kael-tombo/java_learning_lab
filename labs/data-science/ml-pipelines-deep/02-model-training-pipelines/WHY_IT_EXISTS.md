# Model Training Pipelines — Why It Exists

Training pipelines exist because manual retraining does not survive
contact with production. A notebook that worked once depends on the
analyst's memory of which data, which code, and which seed — none of
which is recorded. When metrics shift, nobody can say whether the data,
the code, or chance moved them. When bad data arrives, nothing stops
it from becoming a bad model.

The staged pipeline replaces memory with mechanism: versioned inputs,
gated validation, recorded seeds, and registered outputs. Each piece
answers one audit question — what data, what checks, what code, what
result — so retraining becomes an operation the team can run, monitor,
and defend, instead of a ritual one person performs.
