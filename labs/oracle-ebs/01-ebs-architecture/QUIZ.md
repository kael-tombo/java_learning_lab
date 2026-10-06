# Lab 01: EBS Architecture — Quiz

**1.** An EBS instance shows app tier CPU at 100% and database utilisation at
60% during month-end. What does this most strongly indicate?

A. The database needs more indexes
B. The application tier is the constrained tier
C. Users are submitting invalid requests
D. The load balancer is misconfigured

<details><summary>Answer</summary><b>B</b> — One tier saturated while another has headroom is a tier-level capacity finding. The database has slack; the app tier does not.</details>

---

**2.** What does `JTF_QUEUE_LOCK` contention indicate?

A. A missing index
B. Workers spinning on row locks while competing for work
C. A deadlock detected by the database
D. An exhausted tablespace

<details><summary>Answer</summary><b>B</b> — Workers contend to reserve and claim concurrent work. High CPU with poor throughput is the contention fingerprint.</details>

---

**3.** Why is raising the Concurrent Manager process count on a saturated node
the wrong fix?

A. It is illegal in R12.2
B. The node has no CPU headroom and workers still share one lock
C. It requires a database restart
D. It disables JTF clustering

<details><summary>Answer</summary><b>B</b> — Adding processes to a saturated node adds contention, not throughput. Effective capacity requires horizontal scale and queue separation.</details>

---

**4.** With 20 workers contending on a single lock, roughly what fraction of CPU
is wasted?

A. 5%
B. 20%
C. 50%
D. 95%

<details><summary>Answer</summary><b>D</b> — Useful work ≈ 1/20 = 5%, so ≈95% is wasted spinning.</details>

---

**5.** What is the purpose of Concurrent Manager specialisation?

A. To reduce licensing cost
B. To isolate workload classes so one cannot block another
C. To eliminate the Standard Manager
D. To increase database CPU

<details><summary>Answer</summary><b>B</b> — Separate queues mean a report storm cannot delay a latency-sensitive interface.</details>

---

**6.** Little's Law states `L = λ × W`. If arrival rate is unchanged and average
wait falls from 15 to 2.5 minutes, what happens to the queue length?

A. It is unchanged
B. It falls proportionally (6× reduction)
C. It doubles
D. It cannot be determined

<details><summary>Answer</summary><b>B</b> — L falls from 12×15=180 to 12×2.5=30, a 6× reduction, because throughput rose.</details>

---

**7.** Work shifts must be defined in which time zone?

A. Each region's local time
B. UTC
C. The database (server) time zone
D. The user's browser time

<details><summary>Answer</summary><b>C</b> — Defining them in local time misplaces capacity, typically failing overnight.</details>

---

**8.** After cloning application-tier nodes, what must be enabled to prevent two
nodes scheduling the same job?

A. RAC services
B. JTF clustering
C. Data Guard
D. Forms compression

<details><summary>Answer</summary><b>B</b> — JTF clustering coordinates reservation across nodes so calendar conflict resolution works globally.</details>

---

**9.** Why did database utilisation rise from 60% to 65% after remediation?

A. The database was underperforming
B. New SQL was introduced
C. Work previously stuck in a queue is now actually executing
D. RAC load balancing is misconfigured

<details><summary>Answer</summary><b>C</b> — Higher DB utilisation after fixing the app tier is the expected and healthy signal.</details>

---

**10.** Which F5 health check is correct for a Forms pool?

A. TCP port check
B. ICMP ping
B. HTTP 200 on the application login path

<details><summary>Answer</summary><b>C</b> — TCP-only checks pass while a JVM is hung. Health checks must be application-level.</details>

---

## Scoring
- **9–10**: Ready for a client diagnosis.
- **7–8**: Solid; revisit utilisation multiplier and JTF clustering.
- **5–6**: Re-read THEORY sections on contention and specialisation.
- **<5**: Work through EXERCISES 2, 3, and 8 again.