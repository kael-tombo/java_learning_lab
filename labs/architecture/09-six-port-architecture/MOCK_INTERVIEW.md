# Mock Interview: Classifying a Module onto the Six Ports

> Exercise format. The panellist hands you components; you classify each and defend what the taxonomy buys. On-SiteOps, a facilities-management back office, is adopting the six-port numbering for its work-order module.

---

## The Exercise

"Nine candidates," the interviewer says, "name the port type for each, then tell me why the distinction earns its keep."

1. `POST /work-orders` controller — inbound driving: a human at a screen initiates an operation and expects a synchronously shaped reply; the system is the passenger.
2. Work-order persistence — outbound driven: the module's own durable state, serving no outside caller of its own.
3. Call-out to a rostering partner — outbound driving: we initiate against a foreign system and care about its answer.
4. Listener on the building-sensor stream — inbound event: messages arrive at their own pace, and the module reacts without having asked.
5. WorkOrderCompleted onto the notification bus — outbound event: we emit a fact and take no author on it.
6. A platform timer poking the module each minute to age stale jobs — inbound driven by our reckoning: the trigger originates inside the estate rather than as a foreign fact stream, though an interviewer may argue otherwise; the defensible position is to pick one convention and apply it consistently.
7. A retry of a failed rostering call, triggered from inside the module — still outbound driving: classify the hop, not the chain, since each port answers what a single call does, and the sweep merely re-enters the port the original caller used.

---

## Why the Taxonomy Buys Anything

- Test budgets differ per family: driving ports get scenario-level calls, driven ports get fakes, event ports get recorded streams. Rehearsal infrastructure follows the port type.
- Review depth follows the same split — an outbound driving port can spend money, so it earns the strictest review.
- Ownership becomes arguable in vocabulary: "the rostering adapter is slow" pinpoints a column of the design instead of a vague complaint.
- Rewiring order is derivable: classify before you migrate, and the driven ports show up as quick wins because fakes replace their real counterparts on day one.

---

## The Nuance Question

8. "A partner webhook lands: inbound event or inbound driving?"
   It is an external actor initiating and it wants an answer, which argues driving-side; but it arrives message-shaped, which argues event. The honest answer names both readings, picks inbound driving because a response is owed, and logs the decision. Interviewers want the reasoning, not the label.

9. "Can two ports share one adapter?"
   Rarely, and only where the technologies genuinely coincide. Merged adapters blur the review and test budgets that the taxonomy exists to preserve, so I treat the urge as a smell.

---

## Red Flag

Collapsing event ports into plain method calls "because a message is just a function call over a wire". That erases the ordering and delivery guarantees the design deliberately isolates, and with them the failure drills.

## Closing Question

"Defend the taxonomy in a sentence."

"It names risk precisely: saying 'the outbound driving surface grew' in a review is an actionable sentence, where 'the module feels complicated' never was."
