# EBS Technical Architecture — Mini Project

## Goal
Build a production-shaped custom concurrent program using supported APIs only,
in 90 minutes.

## Requirements
- R1: A table/view layer analysis for one core table, written up in notes.
- R2: A decision table showing when to use `_F`, `_V`, `_S`, or `_ALL`.
- R3: A custom concurrent program registered in the Concurrent Manager.
- R4: The program body calling a public API rather than direct DML.
- R5: A parameter form with at least 3 input parameters.
- R6: A structured error log that survives a mid-run failure.
- R7: A personalization of a standard form, with reversal documented.
- R8: A support-model analysis listing every object the customization touches.

## Steps
1. Analyse the layer views and write the decision table.
2. Locate the public API for your operation and record its signature.
3. Define the staging table and the custom package specification.
4. Register the concurrent program executable and attach the parameters.
5. Implement the package body using the API; capture return status and errors.
6. Run the program through the Concurrent Manager and read the log.
7. Deliberately force a mid-run failure and confirm the error log is useful.
8. Apply a form personalization and document how to remove it.
9. Produce the support-model list with each object's upgrade exposure.

## Acceptance criteria
- The program uses a public API; no direct DML on core tables.
- It runs successfully from the Concurrent Manager, not only from SQL*Plus.
- A mid-run failure leaves an error log sufficient to locate the cause.
- The personalization is fully reversible with documented steps.

## Stretch
- Add a mode parameter for a validate-only run that changes no data.
- Compare query performance against the table versus the `_F` view.