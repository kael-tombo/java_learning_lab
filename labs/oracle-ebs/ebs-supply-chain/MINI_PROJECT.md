# EBS Supply Chain — Mini Project

## Goal
Run a full procure-to-order cycle for a small catalogue in 90 minutes,
including pricing and a drop-ship line.

## Requirements
- R1: Item master with at least 2 subinventories and an initial on-hand load.
- R2: A requisition, purchase order, and receipt for one item.
- R3: A three-way match producing and then resolving a price variance.
- R4: A customer order with 2 lines and a fulfilment plan.
- R5: Two pricing rules with a demonstrated precedence outcome.
- R6: An ATP query contrasting on-hand, reserved, and available.
- R7: A drop-ship order line that never touches inventory.
- R8: A configured product assembled from a BOM to satisfy an order line.

## Steps
1. Create items, subinventories, and load opening on-hand.
2. Raise a requisition, convert it to a PO, and receive the goods.
3. Enter the supplier invoice and run the three-way match; capture the hold.
4. Explain the price variance, correct it, and release the hold.
5. Enter a customer order and generate a fulfilment plan.
6. Define two pricing rules and show which one applies to a given context.
7. Query ATP for a constrained item and explain the availability figure.
8. Process the drop-ship line and confirm inventory was never touched.
9. Assemble the configured product and confirm component consumption.

## Acceptance criteria
- Inventory balances reconcile after receipt, shipment, and assembly.
- The three-way match hold is diagnosed from the hold table, not guessed.
- The pricing outcome is explained using the rule hierarchy.
- ATP correctly excludes reserved and supply-pending quantities.

## Stretch
- Add a freight calculation and show its effect on the order total.
- Break ATP deliberately and explain why the order promised what it could not.