# Cloud Cost Optimization - Mini Project

## Project: A Cost Engine That Ranks Opportunities by Size

### Objective
Build a FinOps engine over a synthetic but realistic cost model that ranks optimisation
opportunities by expected saving, and model commitment discounts against real utilisation.

### Requirements
1. `CostModel` — hourly cost per resource type, region, and pricing tier
2. `CostAttributor` — allocate spend to services and teams from tags
3. `RightsizingEngine` — find underutilised resources from utilisation percentiles
4. `CommitmentModel` — compute savings plans / reservations from a utilisation distribution
5. `ScheduleEngine` — find resources that should be off outside business hours

### Steps

**Step 1: Model cost honestly**
```java
record ResourceCost(String id, String type, String region, double hourlyRate,
                    double utilisationP50, double utilisationP99, boolean stateful) {}
double monthlyCost(ResourceCost r, int hoursPerMonth) { return r.hourlyRate() * hoursPerMonth; }
```
Get the rates right for your region and instance family — this is the input everything else
depends on. A model with wrong rates produces confidently wrong rankings.

**Step 2: Attribute before optimising**
```java
record Allocation(String costCentre, String service, double amount) {}
Map<String, Allocation> attribute(List<ResourceCost> resources, TagLookup tags) {
    // untagged resources are an attribution failure AND a cost risk -- report them separately
}
```
Produce two reports: attributed spend by cost centre, and untagged spend. If untagged spend is
above a few percent, fixing attribution is the highest-value action available — it usually
beats every optimisation on this page.

**Step 3: Rightsizing from percentiles, not averages**
```java
record RightSizing(String id, double currentSize, double recommendedSize,
                   double monthlySaving, double risk) {}

RightSizing analyse(ResourceCost r) {
    // p99 CPU, not mean CPU: instances that spike matter, and the mean hides them
    if (r.stateful()) return RightSizing.NO_CHANGE;          // no downsizing without a test
    if (r.utilisationP99() > 60) return RightSizing.NO_CHANGE;
    var step = stepDownFrom(r.currentSize());                // one step, not straight to the floor
    return new RightSizing(r.id(), r.currentSize(), step,
                           r.hourlyRate() * 730 - priceOf(step) * 730, Risk.LOW);
}
```
Two rules that keep this from causing incidents: **one size down, not to the floor**, and
**never rightsize stateful resources without a load test**.

**Step 4: Model commitments properly**
```java
record CommitmentDecision(double monthlySaving, double upfrontCost,
                          double breakEvenMonths, String recommendation) {}

CommitmentDecision analysePlan(List<ResourceCost> steady, List<ResourceCost> spiky) {
    // Only the baseline of a steady-state family should be committed.
    // Committing spiky capacity means paying for idle capacity at a discount -- still idle.
    var steadyBaseline = baselineOf(steady);          // the p5 floor, not the average
    var oneYearSaving = discountValue(steadyBaseline);
    var threeYearSaving = discountValue(steadyBaseline) * 1.25;   // deeper discount
    return recommendByHorizon(oneYearSaving, threeYearSaving);
}
```
The mistake to demonstrate: committing based on average utilisation. Compute the
**p5 baseline** and commit only that. Then show what happens if you commit the average: half
the commitment sits idle.

**Step 5: Schedulable and ephemeral**
```java
record ScheduleOpportunity(String id, double monthlySaving, String justification) {}
```
1. Non-production environments: 8 hours on weekdays, on for release windows
2. Development instances that are stateful and always-on: hard to justify, move to
   on-demand and stop them deliberately
3. Spot for batch and CI workloads with checkpointing — this is where spot belongs, and the
   checkpointing requirement is the actual work

**Step 6: Rank by size**
```
opportunity            monthly saving    effort    risk
stop 14 dev envs       £1,840            1 day     none
downsize 60 instances  £2,300            1 week    low
non-prod schedule      £2,950            2 weeks   low
savings plans          £4,100            2 weeks   medium (commitment)
data transfer fix      £3,600            3 weeks   medium
```
Ranking by *saving × confidence ÷ effort* is the deliverable. The instinct to start with the
easiest change is how teams spend a quarter and save 4% of the addressable total.

### Deliverables
1. `CostModel` with verified regional rates and an attribution report including untagged spend
2. `RightsizingEngine` using p99 with the stateful exclusion
3. `CommitmentModel` comparing average versus p5 baseline, with break-even arithmetic
4. A ranked opportunity list with saving, effort, and risk for each item

### Extension (CHALLENGE)
Model data transfer costs for a cross-region architecture and show which traffic pattern
(egress, inter-zone, cross-region) dominates — often the least expected one.

### Estimated Time
3-4 hours