# EXERCISES: Incident Response, SRE War Rooms & Post-Mortem Operations
## Lab 14 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: Simulated High-Stakes Tier-0 War Room Roleplay (ICS Protocol)

### 1. Objective
Experience and execute the Incident Command System (ICS) under high-stress conditions, strictly enforcing role separation, single-variable hypothesis testing, and the 5-minute rollback rule.

### 2. Scenario Setup & Roles
Assign 4 engineers to specific roles:
- **Engineer A**: Incident Commander (IC)
- **Engineer B**: Technical Operations Lead
- **Engineer C**: Communications Lead
- **Engineer D**: Scribe
- **Trainer/Facilitator**: Injects chaos anomalies (e.g. database latency spikes, client timeouts, executive interruptions).

### 3. Simulation Tasks
1. The Trainer injects a simulated outage: HTTP 504 errors climb to $28\%$ following a deployment of `order-service:v2.4.0`.
2. **First 2 Minutes**:
   - Engineer A declares Incident Command, establishes the war room, and verifies roles.
   - Engineer A enforces the rule: *No typing commands without IC approval.*
3. **Pacing and Mitigation Execution**:
   - The Trainer acts as an aggressive executive demanding an ETA. Engineer C immediately intervenes and redirects the executive to the comms channel.
   - Engineer B proposes an immediate rollback to `v2.3.9` under the 5-Minute Rollback Rule.
   - Engineer A explicitly authorizes the rollback.
   - Engineer D logs the exact timestamp and command: `kubectl rollout undo deployment/order-service`.
4. **Debrief**:
   - Verify that Engineer A never touched a terminal.
   - Verify that single-variable isolation was strictly maintained.

---

## Exercise 2: Implementing and Testing an Emergency Load Shedding Kill-Switch

### 1. Objective
Implement a dynamic Spring Boot Actuator kill-switch endpoint, simulate a severe database saturation incident under load, and verify that tripping the kill-switch sheds non-critical load and restores core payment availability in $< 10\text{ seconds}$.

### 2. Implementation Tasks
1. Build a Spring Boot REST service with two endpoints:
   - `/api/checkout`: Executes a critical transaction query against PostgreSQL.
   - `/api/recommendations`: Executes a heavy, slow analytics query against PostgreSQL (`SELECT ... JOIN ... GROUP BY`).
2. Integrate `EmergencyLoadSheddingEndpoint` exposing `/actuator/emergency-circuit`.
3. Launch a load generator with 50 concurrent threads firing at both endpoints:
   ```bash
   hey -z 60s -c 50 http://localhost:8080/api/recommendations &
   hey -z 60s -c 20 http://localhost:8080/api/checkout &
   ```
4. Observe PostgreSQL connection pool saturation:
   - Verify checkout latency jumps from 15ms to $> 3,000\text{ms}$.
5. Execute the emergency load shedding command:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"circuitName": "RECOMMENDATIONS", "shedded": true}' \
     http://localhost:8080/actuator/emergency-circuit
   ```
6. Verify the outcome:
   - `/api/recommendations` returns HTTP 200 with empty fallback data in $0.2\text{ms}$.
   - `/api/checkout` latency immediately recovers back to $< 20\text{ms}$ while the load test is still running!

---

## Exercise 3: Automating Forensic Snapshot Capture Prior to Container Termination

### 1. Objective
Build an automated bash forensic capture script and integrate it into a Kubernetes pod lifecycle or emergency triage runbook to guarantee zero diagnostic state is lost during pod restarts.

### 2. Implementation Tasks
1. Write `capture_forensics.sh` implementing Pattern 1 from CODE DEEP DIVE:
   - Captures `top`, `vmstat`, `ss -s`, `cpu.stat`, `Thread.print`, and `GC.class_histogram`.
   - Compresses into `/tmp/incident-bundle.tar.gz` in $< 30\text{ seconds}$.
2. Run a CPU and memory-intensive Java load test in Docker.
3. Trigger the forensic script while the container is actively processing load:
   ```bash
   ./capture_forensics.sh "sim-outage-01"
   ```
4. Inspect the generated tarball:
   - Verify `thread_dump.txt` contains valid, parsable Java stack traces showing active worker threads.
   - Verify `class_histogram_top50.txt` accurately identifies the top memory-allocating domain classes.
   - Verify total tarball size is $< 5\text{MB}$.

---

## Exercise 4: Facilitating a 5-Whys Blameless Post-Mortem and Hierarchy Review

### 1. Objective
Conduct a complete 50-minute simulated blameless post-mortem review on a real-world outage case study, applying Dekker's Just Culture and the Engineering Hierarchy of Controls.

### 2. Case Study Scenario
> *"At 14:00 UTC, Software Engineer Kevin pushed a change modifying the database connection pool timeout from 30s to 1s in a staging branch, which accidentally got merged into main and deployed to production. 10 minutes later, during a normal query spike, connection requests timed out after 1 second, causing 12,000 user transactions to fail."*

### 3. Execution Tasks
1. **Preamble**: State the blameless Just Culture ground rules. Reject any conclusion that blames Kevin.
2. **Execute 5-Whys Analysis**:
   - Why did requests time out? (Timeout set to 1s).
   - Why was timeout set to 1s? (Staging testing value accidentally merged).
   - Why was staging config merged to main? (No branch protection or config separation).
   - Why did production lack config validation? (No schema linter rejecting timeouts $< 10\text{s}$).
   - Why did canary not catch it? (Canary deployment stage disabled to expedite release).
3. **Formulate Action Items**:
   - Draft 2 Level 1/2 **Engineering Controls** (e.g. CI config linter rejecting dangerous timeouts, automated canary gate enforcement).
   - Assign owners and define 14-day P0 SLAs.
