# MLOps Orchestration - Mental Models

## Recipe with checkpoints
- The DAG is a recipe; gates are taste tests.
- A failed taste stops the dish before guests are served, never after.
- The recipe card records batch, page, and knob settings: that is lineage.

## Idempotence as a stamp
- Stamping a form twice leaves one mark.
- Tasks should stamp outputs keyed by run id, not append signatures.
- The promotion flag is the wax seal: applied once, by hand, after inspection.

## Backoff as polite knocking
- Knock, wait longer, knock again, stop shouting after the cap.
- Jitter keeps the whole street from knocking together after a blackout.
- Some doors say do not knock: validation failures fail fast.

## Lineage as lab notebook
- Every experiment page cites data batch, code page, and knob settings.
- Without the notebook the result is rumor, however pretty the chart.
- Fingerprints turn the notebook into an index: same pointer, same run.

## Promotion as graduation
- Overall grades plus no failed subjects.
- One failed subject holds back graduation regardless of the average.
- The diploma names the exact lineage that earned it.

## Triggers as alarm clocks and doorbells
- Cron is the alarm clock: it rings on time whether anyone is at the door.
- Events are the doorbell: silent until data arrives, then immediate.
- A house with both wakes on schedule and answers visitors between ticks.

## Backfill as transcript correction
- Published minutes with an error get a corrected reprint, not white-out.
- Replays write corrected pages beside the originals with new version stamps.
- Readers switch editions explicitly; nobody edits the archive in place.

## Queues as checkout lanes
- Scheduled runs are weekly shoppers; backfills are inventory restock carts.
- One shared lane lets restocking block every shopper behind it.
- Separate lanes with capped carts keep both moving at their own pace.

## Fingerprints as library cards
- Each run files its card: data edition, code printing, knob settings.
- Identical cards retrieve identical books; a changed card means a new edition.
- The catalog number 1047179432 is meaningless alone and exact together.
