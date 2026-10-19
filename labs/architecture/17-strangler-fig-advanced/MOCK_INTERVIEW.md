# Mock Interview: Splitting the Policy Database

> Transcript. Ambler Mutual has run policy administration off one fifteen-year-old relational schema shared by underwriting, claims, and billing. The argument on the table: dual-write versus log-based capture.

---

## Opening

**Moderator**: "The team proposing dual-write calls it simpler than CDC. Your verdict."

**Candidate**: "Dual-write is two independent commits with nothing shared between them. A partial failure writes one store and not the other, and the divergence is discovered weeks later when a claim adjuster meets a missing row. Log-based capture reads the source's commit sequence and replays it, so the target cannot disagree with what actually committed — the ordering is enforced by physics, not discipline."

**Moderator**: "Backfill while the source keeps moving. Sequence it."

**Candidate**: "Record a position in the capture log, take the snapshot consistent with that position, bulk-copy it, then stream changes from the recorded position onward. Bulk and stream must overlap deliberately — the join point is where lost rows hide, and overlap makes that window impossible."

**Moderator**: "How do you ever trust the copy?"

**Candidate**: "Reconciliation, running the whole time: row counts per table and day-partition, plus rolling digests over sampled keys. Every mismatch opens a divergence ticket listing the specific offending rows. The VERIFIED state in the migration machine — untouched, backfilling, converging, verified, legacy-off — is earned by weeks of a clean reconciliation record, never asserted."

**Moderator**: "Reads move over when, and how?"

**Candidate**: "One table at a time behind an internal data-access seam, so callers never know a switch happened. Old readers tolerate the captured copy while it converges; the write cutover happens later, needing only a brief write freeze while the final log tail drains."

**Moderator**: "Which phase owns which risk?"

**Candidate**: "Uncut tables carry nearly none — the source remains authority. The dangerous window is the write cutover, so it is gated: a table neither loses nor gains the legacy write path until its verified record is weeks deep and its rollback stream is rehearsed in staging."

**Moderator**: "Rollback after writes moved — is that even possible?"

**Candidate**: "Only if prepared in the right direction: the return leg is its own capture pipeline, built and drill-tested *before* the cutover, not improvised after. Reclaiming the original authority means enabling a tested stream rather than running salvage scripts at midnight."

**Moderator**: "Biggest ongoing cost?"

**Candidate**: "Two stores to run plus the pipelines between them — budgeted from day one and retired only at the end, since the plumbing exists precisely so that it can be switched off safely later."

**Moderator**: "Give me the whole shape in a single breath."

**Candidate**: "Freeze growth of the shared schema, extract tables by agreement, capture continuously, reconcile continuously, flip reads per table, then move writes — and only with rehearsed rollback."

---

## Probes

- "CDC dies silently for a day. What says so?" — a freshness alarm on capture lag, plus the reconciliation digests themselves; both must page, because a paused pipeline is indistinguishable from a clean one unless watched.
- "Underwriting resists moving off shared tables. Answer?" — the seam lets them move last; extraction order is negotiation, not decree, and the contract is that every table eventually gets a state on the board.
- "Does capture load the source?" — reading the log is cheap, but replay into the target gets throttled to respect the source's peak window; the copy rate defers to business hours, never the reverse.
- "Column changes between the stores?" — a rename is a planned, resumable migration step, with the capture pipeline's version moving alongside it, never a surprise consumed mid-stream.
- "When may the plumbing retire?" — when the final extracted table has been verified and the legacy store no longer serves reads or writes; the same gate that closes the store closes the pipelines.

---

## Red Flag

Decommissioning the legacy write path in the same sprint that VERIFIED was first reached. Data authority changes deserve soak time; candidates who argue otherwise have never watched a reconciliation job disagree with a finance report.
