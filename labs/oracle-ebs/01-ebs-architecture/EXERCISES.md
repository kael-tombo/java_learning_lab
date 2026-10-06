# Lab 01: EBS Architecture — Exercises

## Exercise 1: Read the Two-Tier Evidence
**Time**: 15 minutes | **Difficulty**: Beginner

### Objective
Explain why "app tier 100% CPU, database 60%" is a tier finding rather than a
SQL performance finding.

### Steps
1. Write the utilisation of each tier and its headroom.
2. Identify which tier has zero absorption capacity.
3. Explain what happens to response time as utilisation approaches 1.0.
4. State what you would check next to confirm the tier is the constraint.

### Verification
- [ ] Headroom calculated for both tiers (0.00 and 0.40)
- [ ] Response-time multiplier discussed at U > 0.8
- [ ] Next-step check named (queue depth, not query tuning)

---

## Exercise 2: Prove the Single-Queue Condition
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Confirm from the data that every concurrent request shares one queue.

### Steps
1. Run the query counting enabled, non-specialised queues.
2. Run the queue depth query grouped by queue name.
3. Confirm requests are distributed across exactly one queue.
4. Predict the effect of a 200-report user storm on an interface job.

### Verification
- [ ] Query returns a single Standard Manager row
- [ ] Predicted effect stated: interface delayed behind reports
- [ ] Explanation given in terms of shared queue, not shared CPU

---

## Exercise 3: Explain `JTF_QUEUE_LOCK`
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Explain why 20 CM workers produce high CPU and poor throughput.

### Steps
1. Find the SQL touching `JTF_QUEUE_LOCK`.
2. Identify sessions blocked or spinning in active session history.
3. Compute the wasted CPU fraction for 20 workers.
4. Predict the effect of adding 10 more workers to the same queue.

### Verification
- [ ] Wasted fraction calculated (≈95%)
- [ ] Prediction: CPU rises, throughput does not
- [ ] Link made to the contention fingerprint

---

## Exercise 4: Design the Node Layout
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Produce a 3-node service assignment for 5,000 users.

### Steps
1. Split users: US 2,500 / EMEA 1,500 / APAC 1,000.
2. Compute Forms processes per node at 1:50.
3. Compute OAF threads per node at 1:100, plus JVM overhead.
4. Assign which CM runs on which node and justify each choice.

### Verification
- [ ] Formulas applied, totals correct
- [ ] Admin server designated active on exactly one node
- [ ] Every node has an explicit, non-"same as node 1" assignment

---

## Exercise 5: Create Specialised Managers
**Time**: 30 minutes | **Difficulty**: Advanced

### Objective
Create three specialised queues with correct target nodes.

### Steps
1. Call `FND_CONCURRENT_QUEUE_PUB.CREATE_QUEUE` for Report, Interface, Batch.
2. Set `specialization_on => 'Y'` on each.
3. Pin each to its intended node via `target_node`.
4. Document the rollback (`STOP` rather than delete).

### Verification
- [ ] Three queues created with correct max/min servers
- [ ] Specialisation enabled on all three
- [ ] Target nodes match the layout from Exercise 4
- [ ] Rollback documented as disable, not delete

---

## Exercise 6: Configure Work Shifts
**Time**: 20 minutes | **Difficulty**: Intermediate

### Objective
Define regional peaks correctly in database time zone.

### Steps
1. Create `US_PEAK` 08:00–18:00 EST.
2. Convert EMEA 08:00–18:00 CET to 02:00–12:00 EST.
3. Convert APAC 08:00–18:00 SGT to 19:00–05:00 EST.
4. Assign capacities 40 / 25 / 20 and justify the ratios.

### Verification
- [ ] All three shifts in EST, not local time
- [ ] APAC shift correctly wraps midnight
- [ ] Capacity ratios follow the user distribution

---

## Exercise 7: JTF Clustering
**Time**: 20 minutes | **Difficulty**: Advanced

### Objective
Explain what breaks without clustering after node cloning.

### Steps
1. Describe the duplicate-execution risk across nodes.
2. Find the `jtf_cluster` parameter and set it.
3. Query which queues have specialised target nodes.
4. Explain the role of the Concurrent Manager Node Monitor.

### Verification
- [ ] Duplicate-execution risk described correctly
- [ ] Parameter set and verified
- [ ] Explanation covers calendar-based conflict resolution

---

## Exercise 8: Build the Before/After Report
**Time**: 25 minutes | **Difficulty**: Intermediate

### Objective
Produce a measured comparison table with ratios.

### Steps
1. Record baseline: queue depth, avg wait, peak CPU, completion time.
2. Run the load test after remediation.
3. Compute improvement ratios rather than absolute deltas.
4. Note the database utilisation change and explain why it rose.

### Verification
- [ ] Ratios used, not raw differences
- [ ] DB utilisation increase explained as work no longer stuck
- [ ] All four metrics present in the table