# Visualization - Real-World Project: Transit ridership visual story
## Scenario
monthly boardings by line with a service-gap quarter and a fare-change marker. Success means a reviewer can rerun the 02-visualization flow from raw files to final tables without asking for missing steps.
## Design (histograms, small multiples, slope comparisons, captioned line/bar discipline)
Core chain runs y-axes start at zero for bar comparisons; line charts mark the service gap explicitly.
Method set in play: histograms, small multiples, slope comparisons, captioned line/bar discipline.
## Execution steps
1. Draft the message of each chart in one sentence before drawing it.
2. Show boarding distributions with histograms using documented bin widths.
3. Build small-multiple line panels per transit line sharing one y-scale.
4. Annotate the service-gap quarter and fare-change date on every time chart.
5. Add data-source plus row-count captions beneath each figure.
6. Write alt-text describing trend direction and magnitude for each chart.
7. Cut one decorative chart that repeats a message already shown.
## Pass criteria
- each chart carries a one-sentence message title for the 02-visualization dossier.
- shared y-scale declared across small multiples checked against 02-visualization logs.
- gap and fare annotations present on time axes reproduced on rerun of 02-visualization steps.
- captions give source plus counts for every figure stored with the 02-visualization artifact set.
- alt-text exists for all published charts signed off inside the 02-visualization review note.
## Limits of Transit ridership visual story
Textbook methods only; streaming, serving, and cost tuning belong outside this 02-visualization brief.
## Evidence pack carried with 02-visualization
- Raw monthly boardings by line with a service-gap quarter and a fare-change marker snapshot pointer plus exact row counts.
- Dated run log linking each 02-visualization build decision to its output table.
- Before/after comparison table kept beside the Transit ridership visual story tables.
- Rejected-rows file with rule codes for the 02-visualization audit trail.
- One-page Visualization glossary defining every column the Transit ridership visual story emits.
## Reviewer walkthrough for Transit ridership visual story
- Reviewer opens 02-visualization inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to monthly boardings by line with a service-gap quarter and a fare-change marker.
- Reviewer confirms each chart carries a one-sentence message title without extra explanation.
- Reviewer closes the Visualization session with two written follow-ups.
