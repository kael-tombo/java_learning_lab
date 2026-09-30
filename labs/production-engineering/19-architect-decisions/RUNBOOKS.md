# RUNBOOK: Architectural RFC Process & Decision Governance
## Lab 19 | Production Engineering Academy

---

## RUNBOOK 01: Creating and Reviewing an Architectural RFC / ADR

### Step 1: Identify Decision Type
- **Type 2 (Reversible)**: Team lead authors lightweight ADR; fast-tracked with 48-hour team review.
- **Type 1 (Irreversible / Multi-Team Impact)**: Requires formal Request for Comments (RFC) process.

### Step 2: Authoring the RFC / ADR
1. Create a new branch: `git checkout -b adr/add-event-streaming-model`.
2. Copy `CODE_DEEP_DIVE.md` ADR template to `/docs/adr/ADR-00XX-title.md`.
3. Fill all sections with objective, grounded data and alternatives considered.

### Step 3: Architecture Review Board (ARB) Review
1. Schedule a 45-minute ARB review meeting.
2. The decider presents the decision drivers and options matrix.
3. Review outcome recorded: `ACCEPTED`, `REJECTED`, or `CHANGES_REQUESTED`.
4. Merge ADR to `main` branch. Git commit represents formal organizational consensus.
