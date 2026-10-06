# EBS Financials — Mini Project

## Goal
Run a complete procure-to-pay and order-to-cash cycle on a small dataset in
90 minutes, and reconcile everything back to the trial balance.

## Requirements
- R1: A chart of accounts with at least 3 segments and 15 accounts.
- R2: SLA accounting templates for AP and AR.
- R3: A purchase order, receipt, and supplier invoice through to payment.
- R4: An AP hold placed on a mismatched invoice, diagnosed, and released.
- R5: A customer order, shipment, invoice, receipt, and application.
- R6: AR aging report before and after the receipt.
- R7: Bank reconciliation producing an explained reconciling item.
- R8: A reconciliation query proving GL equals subledger totals.

## Steps
1. Build the chart of accounts and load opening balances.
2. Define the SLA templates for AP and AR.
3. Create a PO, receive it, enter the invoice, and pay it.
4. Run the hold diagnostic; explain why the hold fired and release it.
5. Create a sales order, ship it, invoice it, and apply a receipt.
6. Produce AR aging before and after the application.
7. Reconcile the bank account and explain the reconciling difference.
8. Run the GL↔subledger reconciliation and confirm zero variance.

## Acceptance criteria
- Every transaction posts to GL through the SLA, not directly.
- The AP hold is diagnosed from `AP_HOLDS_ALL`, not guessed.
- The GL↔subledger reconciliation returns zero unexplained variance.
- The aging report visibly changes after the receipt is applied.

## Stretch
- Add a fixed asset with a depreciation run and check the net book value.
- Introduce a partial payment and show its effect on the trial balance.