# EBS Supply Chain — Vision

## Where this lab takes you
From inventory basics through purchasing, order management, and advanced
pricing — the modules that decide whether an order was a good idea.

## The Arc
1. **Inventory** — items, subinventories, transactions, on-hand.
2. **Purchasing** — requisitions, POs, receipts, and three-way match.
3. **Order management** — customer orders, lines, fulfilment.
4. **Pricing** — pricing rules, adjustments, and their precedence.
5. **ATP** — available to promise, and the rules that define it.
6. **Shipping** — pick, pack, ship, and freight calculation.
7. **Special orders** — drop ship and back-to-back flow.
8. **Configure to order** — products assembled from their bill of material.

## Milestones (checkable)
- [ ] M1: Explain the item/subinventory structure and on-hand semantics.
- [ ] M2: Execute a receipt and a shipment, tracing the inventory effects.
- [ ] M3: Run a three-way match and explain a price variance hold.
- [ ] M4: Enter a customer order and take it through fulfilment.
- [ ] M5: Apply two pricing rules and show which one won, and why.
- [ ] M6: Query ATP and explain the difference between on-hand and available.
- [ ] M7: Process a drop-ship order without the goods ever entering inventory.
- [ ] M8: Configure a product with a BOM and assemble it to order.

## Anti-Goals
- Treating on-hand as available without checking reservations and supply.
- Debugging a pricing result without reading the pricing hierarchy.
- Using drop-ship as a shortcut for a fulfilment problem.
- Configuring a product without confirming the BOM routing is real.

## The one-sentence thesis
Order management is a promise about capacity — ATP, pricing precedence, and
fulfilment path all have to agree or the promise breaks downstream.