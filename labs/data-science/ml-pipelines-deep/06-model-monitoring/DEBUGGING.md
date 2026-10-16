# Model Monitoring - Debugging

## Alerts fire constantly
- Cause: thresholds fit to a quiet window; normal variance now pages.
- Check: alert precision over the last month; distribution of paged values.
- Fix: retune to high-precision rules; move the rest to dashboards.

## Real incident missed
- Cause: aggregate metric stable while one slice broke.
- Check: slice breakdowns for the incident window.
- Fix: add per-slice monitors for the segments that matter.

## Drift score jumps overnight
- Cause: pipeline change (new encoder, unit change) rather than world change.
- Check: deploy and schema-change log against the jump time.
- Fix: pin the reference correctly; add pipeline-health checks first.

## Quality metrics look wrong
- Cause: computed on immature labels with low maturity fraction.
- Check: label-maturity curve for the window.
- Fix: restrict official metrics to mature windows; mark fresh ones provisional.

## Silent monitor
- Cause: telemetry stopped; aggregator shows stale flat lines.
- Check: event volume and last-received timestamps.
- Fix: alert on missing data, not only on bad values.

## Slice regression with clean aggregate
- Cause: one segment broke while others compensated in the average.
- Check: per-slice positive rate and error over the incident window.
- Fix: per-slice monitors plus a segment owner for each tracked slice.

## Reference older than the pipeline
- Cause: encoder or unit change shipped without a reference refresh review.
- Check: deploy log against drift-score jump time; confirm pipeline diff first.
- Fix: refresh the reference deliberately and annotate the pipeline reason.

## Maturity illusion
- Cause: dashboards mix provisional and mature windows in one line.
- Check: maturity age behind each plotted point.
- Fix: split lines by maturity state; official numbers from mature only.

## Feedback-amplified drift
- Cause: retraining on model-influenced labels reinforced its own bias.
- Check: label-source audit for the last two retraining rounds.
- Fix: quarantine looped labels; validate sources before the next round.
