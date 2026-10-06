# Lab 03: Financials — Mini Project

## Goal
Reduce AP invoice holds from 30% to under 8% by fixing matching rules and
tolerances, in 90 minutes.

## Requirements
- R1: A hold taxonomy query from `AP_HOLDS_ALL` ranked by volume and value.
- R2: A query showing held value at risk by supplier category.
- R3: A variance analysis of price and quantity differences on held invoices.
- R4: A proposed matching-rule change (received vs ordered quantity).
- R5: Tolerance values justified from the measured variance distribution.
- R6: A batch hold release program with reason codes and an audit record.
- R7: Workflow notification for newly held invoices.
- R8: A before/after hold-rate measurement with the numbers recorded.

## Steps
1. Load sample PO, receipt, and invoice data with deliberate variances.
2. Run the hold taxonomy query and record the top reasons.
3. Quantify held value and identify the dominant cause.
4. Analyse the variance distribution to choose tolerances from data.
5. Change the matching rule to received quantity and re-test.
6. Apply the justified tolerances and re-run the same data.
7. Build the batch release program with reason codes.
8. Add workflow notification and confirm it fires.
9. Re-measure the hold rate and record before/after.

## Acceptance criteria
- The top hold reason is identified with volume and value, not guessed.
- Tolerances are derived from the observed variance distribution.
- Every released hold has a reason code and an audit record.
- The after-hold rate is below 8% and the measurement is reproducible.

## Stretch
- Show that your tolerance change did not weaken the three-way match.
- Add a dashboard alert that fires if the hold rate regresses above 10%.