# THEORY: Incident Response, On-Call & Post-Mortem Engineering
## Lab 14 | Production Engineering Academy

---

## 1. Incident Command System (ICS) for Technology Outages

When a major production outage strikes, standard organizational hierarchy breaks down. Emergency operations require clear role separation based on the Incident Command System (adapted from FEMA emergency response):

1. **Incident Commander (IC)**:
   - Holds sole authority over incident response.
   - Does NOT debug or write code!
   - Delegates investigative tasks, maintains high-level situational awareness, decides on rollbacks/failovers.
2. **Operations / Technical Lead**:
   - Directs the engineering subject matter experts (SMEs).
   - Coordinates diagnostic hypotheses and executes technical mitigations.
3. **Communications Lead (Comms)**:
   - Protects technical responders from executive interruptions.
   - Posts internal updates to `#incident-broadcast` every 15–30 minutes.
   - Drafts customer-facing public status page updates (e.g. Statuspage.io).
4. **Scribe**:
   - Records chronological timeline of events, hypotheses tested, commands run, and metric changes.

---

## 2. Forensic Metrics: MTTD, MTTA, MTTR

$$\text{MTTD (Mean Time to Detect)} \longrightarrow \text{MTTA (Mean Time to Acknowledge)} \longrightarrow \text{MTTR (Mean Time to Resolve/Mitigate)}$$

- **MTTD**: Time from when customer failure began to when automated monitoring alerted. (Target: $< 3\text{ minutes}$).
- **MTTA**: Time from alert page to on-call engineer acknowledging and taking command. (Target: $< 5\text{ minutes}$).
- **MTTR**: Time from alert acknowledgment to restoring service health (mitigation, not necessarily permanent bug fix). (Target: $< 15\text{ minutes}$).

---

## 3. The Philosophy of Blameless Post-Mortems

Human error is the *symptom* of a systemic vulnerability, never the root cause:
- **Sidney Dekker's Just Culture**: Engineers come to work intending to do a good job. If an engineer ran a dangerous SQL script or pushed a buggy config, the system allowed them to do so without safety guardrails.
- **The "5 Whys" Methodology**: Dig past surface human action to uncover latent architectural, tooling, and procedural weaknesses.
- **Action Items Standard**: Action items must be concrete, assigned to specific owners, and prioritized in the very next sprint with Jira tickets.
