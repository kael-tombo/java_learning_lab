# References - Data Pipelines

Real books only; no invented titles.

- Kleppmann - "Designing Data-Intensive Applications" (O'Reilly, 2017).
  The correctness canon: delivery semantics, idempotence, batch/stream
  tradeoffs, and schema evolution - this lab's THEORY.md follows its
  framing throughout.
- White - "Hadoop: The Definitive Guide" (O'Reilly, 4th ed. 2015). The
  batch-processing counterpart: HDFS/MapReduce mechanics behind the
  large-scale batch jobs pipelines still run.
- Kimball and Ross - "The Data Warehouse Toolkit" (Wiley, 3rd ed.
  2013). Dimensional modeling and the ETL discipline behind modeled
  serving tables.
- Inmon - "Building the Data Warehouse" (Wiley, 4th ed. 2005). The
  warehousing counterpart: enterprise history, auditability, time
  variance - the provenance thinking behind run logs.
- Hyndman and Athanasopoulos - "Forecasting: Principles and Practice"
  (OTexts). For what consumes pipeline output: forecasts inherit every
  upstream defect, so pipeline readers learn what their data owes them.

Start with Kleppmann for semantics, Kimball for modeling the serve
layer, Inmon when auditability requirements get serious.

- Redman - "Data Driven: Profiting from Your Most Important Business
  Asset" (Harvard Business Review Press, 2008). Data quality economics:
  the cost-of-bad-data case behind every quality gate in this lab.
- McGilvray - "Executing Data Quality Projects by Design" (Morgan
  Kaufmann, 2008; 2nd ed. 2021). The practitioner's quality playbook:
  checks, ownership, and remediation that stick.

## Reading order

Kleppmann first (semantics you must not get wrong), Kimball alongside
(modeling the serve layer), Redman for the quality business case,
McGilvray for running the program, Inmon when auditors arrive.
