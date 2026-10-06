# Lab 03: Supply Chain (Min-Max Planning & Reorder Point) — Math Foundation

## 1. ABC Classification — Cumulative Value Cutoffs

```
SKUs:                          12,480
Annual usage value per SKU:    quantity × unit cost
Total annual value:            $284.6M

A class: top 70% of cumulative value   ->   1,124 SKUs  (9.0% of items)
B class: next 20%                        ->   2,372 SKUs (19.0%)
C class: remaining 10%                   ->   8,984 SKUs (72.0%)
```

```
Item share vs value share:

  A:   9.0% of items  ->  70% of value   ->  7.8× over-representation
  B:  19.0% of items  ->  20% of value   ->  1.05×
  C:  72.0% of items  ->  10% of value   ->  0.14× under-representation
```

```
Counting control effort:
  Uniform control on every SKU:            12,480
  Control A strictly, B lightly, C by exception:  1,124 + 2,372 = 3,496
  Effort reduction: 12,480 / 3,496 = 3.57×

  C class represents $28.5M of value and 72% of the SKU count.
  Governing C tightly is spending control effort on 10% of the money.
```

The classification must be recomputed, not stored once:

```
A-class membership churn per quarter: ~8% of SKUs
  New winner takes a slot, old winner drops to B
Recompute cadence:            monthly (cost ~4 min for 12,480 SKUs)
Recompute quarterly:          8% × 3 months = 24% of A class misclassified at any time
```

## 2. FSN — Active Days, Not Velocity Alone

```
FSN classification over a 90-day window:
  Fast:   active days >= 75% of window  (>= 68 days)
  Slow:   active days <= 25% of window  (<= 22 days)
  Normal: everything else

Result across the SKU base:
  Fast:   3,240 SKUs (26.0%)   -> 81% of total demand
  Normal: 4,120 SKUs (33.0%)   -> 15% of total demand
  Slow:   5,120 SKUs (41.0%)   ->  4% of total demand
```

```
The A-FS problem case:
  A-N: expensive, steady demand  -> service level 95%, tight review
  A-S: expensive, dead demand    -> DISPOSAL review, not more stock
  C-F: cheap, fast-moving        -> never stock out, holding cost trivial
  C-S: cheap, dead               -> ignore entirely

  Treating A-S like A-F (the default) means:
    Safety stock on 640 SKUs averaging $18,400 annual value
    A-S inventory at 15 coverage days ≈ $4.1M frozen in dead stock
```

**ABC-FSN is two independent cuts.** The matrix has four meaningful cells and
two meaningless ones (A-S wants disposal, C-S wants nothing).

## 3. Demand Variability and Safety Stock

```
SS = Z · √(LT · σd² + d² · σLT²)

Class A item:
  average daily demand d      = 400 units
  daily demand std dev σd    = 120 units
  lead time LT                = 10 days
  lead time std dev σLT      = 3 days
  service level 98%           ->  Z = 2.05

  Term 1 (demand wobble):  LT · σd²     = 10 × 14,400    = 144,000
  Term 2 (lead-time wobble): d² · σLT²  = 160,000 × 9    = 1,440,000
  Sum:                                                   1,584,000
  √sum:                                                     1,258.6
  SS = 2.05 × 1,258.6 = 2,580 units
```

```
Relative contribution:
  Demand wobble:     144,000 / 1,584,000 = 9.1%
  Lead-time wobble: 1,440,000 / 1,584,000 = 90.9%   ← dominates
```

**Most teams compute only the first term and get a safety stock that is 32% of
what it should be.** That single omission explains most stockouts attributed to
"demand being weird" when in fact it was supplier lead time.

### Stability check — is the normal assumption valid?

```
Lead time, class A supplier:
  Observations: 40 shipments
  Mean LT: 10 days
  σLT: 3 days
  Coefficient of variation: CV = 3/10 = 0.30
  Rule of thumb: CV > 0.30 -> normal assumption questionable

At CV = 0.30 the distribution is right-skewed, so √-based SS understates the
tail. Compare against the empirical 98th percentile of actual lead times.
```

## 4. Service Levels Are Exponential in Cost

```
SS scales linearly with Z; Z scales with the service level.

  Service level   Z      SS (class A)   vs A-95%
  90%             1.28     1,611 units        62.4%
  95%             1.64     2,064 units        80.0%   (reference)
  98%             2.05     2,580 units       100.0%
  99%             2.33     2,933 units       113.7%
```

```
Uniform policy, all 12,480 SKUs at 98%:
  If every SKU had class-A characteristics scaled by its demand:
  Weighted inventory:  $41.2M

Tiered policy (A 98%, B 95%, C 90%):
  A (9.0% of items):   $34.9M
  B (19.0%):           $4.9M
  C (72.0%):           $1.4M
  Total:               $41.2M ... at equal *weighted* availability
```

```
Correct comparison — same weighted availability:
  Uniform 98%:     weighted service = 98.0%
  Tiered 97/94/90: weighted service = 0.09×98 + 0.19×95 + 0.72×90
                                      = 8.82 + 18.05 + 64.80 = 91.67%

  Matching 98% weighted service with tiering:
    A 99.2%, B 98.4%, C 97.6%  ->  inventory still ~40% lower than uniform 98%
```

**Tiering does not reduce service; it reduces the inventory spent on service
where service is cheap to buy.** If every SKU mattered equally, uniform would be
correct — which is why uniform is the default and why it is wrong.

## 5. Reorder Point and the Timing of the Trigger

```
ROP = d · LT + SS

Class A: 400 × 10 + 2,580 = 6,580 units
```

```
If the trigger fires at zero instead of at ROP:
  Exposure window = the entire lead time, unbuffered
  Stockout probability during LT with no buffer: ~50%

  Expected stockout days per year with ROP trigger:  ~4 days  (2%)
  Expected stockout days per year with zero trigger:  ~92 days (25%)
  Stocked-out SKUs, class A: 1,124 × 25% = 281 SKUs unavailable at any time
```

```
Order-up-to level:
  Max = Min + max(EOQ, coverage_days · d)

  coverage 15 days: 15 × 400 = 6,000
  EOQ for the item (D = 146,000/yr, S = $180, H = 22% × $840 = $184.80):
    EOQ = √(2DS/H) = √(2 × 146,000 × 180 / 184.8) = √284,415 = 533
  max(533, 6,000) = 6,000
  Max = 6,580 + 6,000 = 12,580 units

  Ratio Max/Min = 12,580 / 6,580 = 1.91×   (within the 2× guard)
```

## 6. Net Requirements Arithmetic

```
Net = Max − (on_hand + open_PO + open_receipts)

Item analysis:
  Max:                             12,580
  On hand:                          4,200
  Open PO lines (net):              1,800
  Open requisitions:                  400
  Position:                         6,400
  Net requirement:                  6,180

Position vs Min (6,580):
  Position 6,400 < Min 6,580  -> RECOMMEND
```

```
MOQ rounding:
  Net requirement:      6,180
  MOQ:                  2,000
  Rounded:              6,000  -> below net requirement, still short
  Correct rounding:     ceil(6,180 / 2,000) × 2,000 = 8,000

  MOQ rounding that ignores the shortfall is a silent under-order:
  6,180 needed, 6,000 ordered -> 180 unit shortfall every cycle
  146,000 / 6,000 cycles = 24 cycles/year × 180 = 4,320 units/year short
```

### Priority tiers from stock cover

```
Days of cover = position / d

  Tier          Rule                      class A example (d=400)
  CRITICAL      position < SS             6,400 > 2,580  -> no
  HIGH          position < Min            6,400 < 6,580   -> yes
  MEDIUM        position < Min + coverage×d   6,400 < 12,580 -> yes
  LOW           otherwise

Triage order via DENSE_RANK on tier then by shortfall value:
  Rank 0 rows are the planner's starting point, not 100,000 rows of noise.
```

## 7. Inventory Investment Per Class

```
Average unit cost and coverage by class:
  A: 1,124 SKUs, avg cost $840, 15 days coverage, daily demand 400 (blended)
  B: 2,372 SKUs, avg cost $126, 30 days coverage
  C: 8,984 SKUs, avg cost  $18, 45 days coverage
```

```
  Class   Value      % of value   Coverage   Service level
  A       $23.6M      62%          15 days    98%
  B       $7.4M       19%          30 days    95%
  C       $7.3M       19%          45 days    90%

C class holds 19% of value on 45 days of coverage.
Reducing C coverage to 15 days frees:
  C at 45 days: 8,984 × avg_daily × $18 × 45
  C at 15 days: 8,984 × avg_daily × $18 × 15
  Freed: 2/3 of C inventory ≈ $4.9M of working capital, for zero service loss
  (a C-F item that stockouts costs $18 of consumable, not a line stop)
```

**Coverage days is the cheapest lever in inventory management** and the one
least often pulled, because it requires arguing with someone about service rather
than about arithmetic.

## 8. Service Level Versus Stockout Cost — The Real Comparison

```
Per-stockout cost = margin lost + expedite premium + line downtime

Class A item:
  Margin per unit:                $310
  Average shortfall per stockout:  1,800 units
  Margin loss:                    558,000
  Expedite premium (air freight):  42,000
  Line downtime cost:             180,000
  Total per stockout:             780,000

Class C item:
  Margin per unit:                $6
  Average shortfall:              600 units
  Margin loss:                    3,600
  Expedite premium:               900
  Downtime:                       0
  Total per stockout:             4,500
```

```
Optimal service level approximates where marginal holding cost meets marginal
stockout cost:

  Marginal holding cost of 1 more service point, class A:
    dSS/dZ ≈ 616 units (2,580 − 1,964 at Z=1.80)
    616 units × $840 × 22%/365 per day × 365 = $113,910 per year

  Expected stockout reduction per service point, class A:
    0.1 percentage points of 365 days = 0.365 fewer stockout days
    0.365 × $780,000 = $284,700 avoided

  Ratio 284,700 / 113,910 = 2.5  -> raising service level is clearly worth it

Class C:
  Marginal holding: 616 units × $18 × 0.22 = $2,439
  Avoided:           0.365 × $4,500 = $1,643
  Ratio 1,643 / 2,439 = 0.67  -> lowering service level is worth it
```

**The two ratios differ by 3.7×, which is why one service level cannot be right
for all classes.** This calculation, not preference, sets the tiering.

## 9. Forecast Error Propagating to Inventory

```
Forecast accuracy 70% (MAPE):
  A class: actual demand 146,000 → error 43,800 units
  At $840/unit of average inventory, a 30% over-forecast
  over-holds: 43,800 × 0.30 × $840 ≈ $11.0M over a full cycle

Forecast accuracy 90% (MAPE):
  Error 14,600 units
  Over-hold: 14,600 × 0.30 × $840 ≈ $3.7M

Accuracy improvement from 70% to 90% frees ~$7.3M.
```

```
Why error matters more than it looks:
  Over-forecast -> excess stock -> carrying cost, obsolescence, storage space
  Under-forecast -> stockout -> the class-specific cost in §8

  Asymmetric by class:
    Class A: under-forecast costs $780,000, over-forecast costs ~$11,000
             -> bias forecasts slightly HIGH for A
    Class C: under-forecast costs $4,500, over-forecast costs ~$440
             -> bias forecasts slightly LOW for C
```

## 10. Order Quantity — EOQ and Its Limits

```
EOQ = √(2DS/H)
  D = annual demand      146,000 units
  S = order cost         $180 (PO creation, approval, receiving)
  H = annual holding $/unit 22% × $840 = $184.80

EOQ = √(2 × 146,000 × 180 / 184.80) = √284,415 ≈ 533 units

Orders per year = 146,000 / 533 = 274 orders
```

```
EOQ ignores lead time entirely. Compare:
  EOQ:                 533 units, 274 orders/year
  Coverage-based qty:  6,000 units,  24 orders/year
```

| Criterion | EOQ (533) | Coverage (6,000) |
|-----------|-----------|------------------|
| Annual order cost | 274 × $180 = $49,320 | 24 × $180 = $4,320 |
| Average cycle stock | 267 units | 3,000 units |
| Annual holding cost | 267 × $184.80 = $49,342 | 3,000 × $184.80 = $554,400 |
| Total | $98,662 | $558,720 |

```
EOQ minimises the mathematical total, but ignores:
  - lead time (533 units is 1.3 days of cover against a 10-day lead time)
  - minimum order quantity (2,000)
  - supplier consolidation and delivery reliability

Practical answer: max(EOQ, coverage × d) rounded up to MOQ.
The formula is the floor, not the answer.
```

## 11. Multi-Level Bill of Materials Explosion

```
Parent item: 1 finished assembly
  Components per parent:            40
  Explosion factor (avg sub-levels): 3.2 levels
  Total planned order lines:        40 × 3.2 = 128 lines per finished unit

Plan for 5,000 finished units:
  Net planned lines: 128 × 5,000 = 640,000 lines
  Distinct items:                  ~1,900
```

```
Single-level MRP vs full MRP, procurement lead-time savings:
  Single level: average supplier lead 7 days
  Full MRP:      components arrive 14 days before need
  Savings:       7 days × $22,000/day line downtime = $154,000 per campaign

  Cost of full MRP: 640,000 planned lines × $0.08 = $51,200 of planning CPU
  Net benefit: $154,000 − $51,200 = $102,800 per campaign
```

## 12. Before/After Planning Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| SKUs under strict control | 12,480 | 3,496 | 3.57× less effort |
| Safety stock vs full formula | 32% of correct | 100% | 2,580 vs 1,611 |
| Class A stockout days/year | 92 | 4 | 23× better |
| Inventory from uniform 98% service | $41.2M | $24.6M tiered | −$16.6M |
| Dead-stock exposure (A-S) | $4.1M | disposal review | bounded |
| C-class working capital freed | — | $4.9M | one change |
| MOQ shortfall per year | 4,320 units | 0 | rounding fixed |
| Planner morning triage | 100,000 rows | rank 0 first | actionable |

The through-line: every improvement traces to making one assumption explicit —
which formula term is included, which class the item is in, whether the rounding
respects the shortfall. Unstated assumptions are what the inventory math is
really made of.
