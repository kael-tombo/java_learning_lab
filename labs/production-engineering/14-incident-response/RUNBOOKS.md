# RUNBOOK: Incident Management & War Room Execution
## Lab 14 | Production Engineering Academy

---

## RUNBOOK 01: Standing Up a P1/Sev-1 Incident Bridge

**Severity**: P1 / Sev-1 (Customer Impairment $> 5\%$ or Core Flow Down)

### Phase 1: Initiation (0 - 5 Minutes)
1. **Declare Incident & Severity**:
   Post in `#incident-alerts`:
   `🚨 DECLARING SEV-1 INCIDENT: Checkout API failing with 500 errors. Opening war room.`
2. **Assign Incident Roles**:
   - **Incident Commander (IC)**: [Name]
   - **Technical Lead**: [Name]
   - **Communications Lead**: [Name]
   - **Scribe**: [Name]
3. **Open Dedicated Channels**:
   - Bridge: Zoom / Google Meet link.
   - Slack: `#incident-20260930-checkout-api`.

### Phase 2: Execution (5 - 30 Minutes)
1. **Rule of One Voice**:
   - Only the IC directs the conversation. Responders state facts and hypotheses concisely.
2. **Stabilization Before Root Cause**:
   - Do NOT attempt to fix the code in production!
   - MITIGATE: Roll back deployment, toggle feature flag, fail over to alternate AZ, or shed non-critical load.
3. **Status Broadcasting**:
   - Comms Lead posts internal updates every 20 minutes to `#incident-broadcast`.

---

## RUNBOOK 02: Post-Incident Review Protocol (T+24 to T+72 Hours)
1. Scribe publishes raw event log within 12 hours.
2. Schedule a 45-minute Blameless Post-Mortem review meeting with all responders.
3. Complete standard Post-Mortem document using the academy template.
4. File Jira action items with target resolution dates.
