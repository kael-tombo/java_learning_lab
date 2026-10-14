# Why Data Pipelines Exist

Raw data is born hostile: scattered across sources, keyed
inconsistently, revised without notice, arriving late and duplicated.
Decisions need the opposite: one keyed, validated, fresh-enough table
where every number traces to a logged run. Pipelines exist to convert
the former into the latter, repeatedly, without heroics.

Each concept patches one observed failure. Idempotent sinks because
retries are certain and appends duplicate. Delivery semantics because
transport promises are weaker than newcomers assume. Schema contracts
because two teams evolving one format without rules break each other
quarterly. Quality gates because silent corruption compounds into every
downstream model and dashboard. DAGs because cron chains hide failure
locality until 3 a.m.

Without pipelines, analytics is archaeology: spreadsheets emailed,
counts irreproducible, "final_v7" the version system. With them, the
same questions get fresher answers every day, each defensible from its
run log.

## A concrete scene

A retailer emails "final" revenue every Monday, each week restating the
last - finance plans on shifting sand while three teams keep three
spreadsheets that disagree by 4%. No keys shared, no run logged, no
contract signed: archaeology with better fonts.

## What method changes

Keyed orders land raw; checks gate nulls and drift; merges sink
idempotently; the DAG reruns nightly from logs. Monday's number traces
to a run id anyone can replay - disputes end at the diff, not in
meetings about whose spreadsheet is holier.

## The alternative, priced

Manual re-pulls cost analyst-weeks per quarter and still disagree;
one silent schema rename once broke every downstream model for a month
before anyone noticed. Quarantine gates and compat checks price in
pennies against either failure.
