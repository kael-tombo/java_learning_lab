# Step-by-Step Guide: Probability Axioms

## Worked example: Bayes' rule on a medical test

Given: prevalence P(D) = 0.01, sensitivity P(+|D) = 0.99, specificity P(¬+|¬D) = 0.95.

### Step 1 — Enumerate the partition of Ω
{D ∩ +, D ∩ ¬+, ¬D ∩ +, ¬D ∩ ¬+} are disjoint and cover Ω, so their probabilities sum to 1.

### Step 2 — Fill the joint cells (product rule)
- P(D ∩ +)  = 0.01 × 0.99  = 0.0099
- P(D ∩ ¬+) = 0.01 × 0.01  = 0.0001
- P(¬D ∩ +)  = 0.99 × 0.05 = 0.0495
- P(¬D ∩ ¬+) = 0.99 × 0.95 = 0.9405

Check: 0.0099 + 0.0001 + 0.0495 + 0.9405 = 1.0000 ✓

### Step 3 — Marginalize for P(+)
P(+) = 0.0099 + 0.0495 = 0.0594 (about 1 in 17 tested people)

### Step 4 — Condition
P(D | +) = 0.0099 / 0.0594 = 0.16666… ≈ **16.7%**

### Step 5 — Verify by odds
Prior odds = 0.01/0.99 = 0.010101…; likelihood ratio = 0.99/0.05 = 19.8.
Posterior odds = 0.010101… × 19.8 = 0.2 → posterior = 0.2/1.2 = 1/6 ✓ Same answer.

## Worked example: inclusion-exclusion on two dice

Let A = "sum ≥ 9" (10 of 36 ordered pairs → P(A) = 10/36), B = "doubles" (6 of 36 → P(B) = 6/36).
A ∩ B = doubles whose sum is ≥ 9: (4,4) has sum 8 (excluded), so A ∩ B = {(5,5), (6,6)} → 2/36.

P(A ∪ B) = 10/36 + 6/36 − 2/36 = 14/36 = 7/18 ≈ 0.3889.

Count directly to confirm: pairs with sum ≥ 9 or doubles = 10 + 6 − 2 = 14 of 36 ✓

## Verification checklist
- [ ] The events used as a partition are disjoint *and* exhaustive
- [ ] Joint cells sum to exactly 1 (within floating-point tolerance)
- [ ] Conditional probability divides by the marginal of the conditioning event
- [ ] Result cross-checked by odds/likelihood ratio or direct counting
