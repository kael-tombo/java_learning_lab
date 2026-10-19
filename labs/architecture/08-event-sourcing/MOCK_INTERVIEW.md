# Mock Interview: An Event-Sourced Rewards Ledger

> Chair-and-candidate format. TrailPoints, a loyalty program, disputes roughly every other quarter, and finance wants a complete trail of who was credited what and when.

---

## Round One

**Chair**: "State your storage shape first."

**Candidate**: "One append-only table: stream id — the account — plus a strictly increasing sequence, event type, and payload. A unique constraint on (stream, sequence) admits exactly one writer per version; two concurrent commands, one wins and the loser reloads fresh state and retries. That constraint *is* the optimistic concurrency guarantee — no separate version service needed."

**Chair**: "Withdraw requires a balance check, but there is no balance column."

**Candidate**: "Load the stream, fold the events into current state, then decide. A few thousand events in, replay costs real latency, so a snapshot is punched in every fixed number of events; a load then reads one snapshot plus the short tail."

**Chair**: "Support says March rewarded someone twice. Make it right."

**Candidate**: "March stays untouched. A new RewardReversed event referencing the original lands today; folding it corrects the balance going forward, while March keeps telling the truth. Rewriting history would erase the very audit this design exists to provide."

**Chair**: "A projection broke badly and a rebuild is ordered."

**Candidate**: "Rebuild into a scratch copy by replaying the stream, compare per-account closing balances live-versus-scratch, then switch readers. Downtime is one pointer flip, and the comparison tells us exactly which handler misbehaved."

**Chair**: "Right-to-erasure against an immutable log — reconcile those."

**Candidate**: "Honestly, they fight. The workable compromise: encrypt the account-holder's personal field per account and destroy that key when erasure is requested. Payloads remain, but they are unreadable. Teams must decide before launch, not when the first request lands."

**Chair**: "Sum up what this buys the program."

**Candidate**: "Every dispute terminates at a row, not a recollection. 'Balance as of March 3rd' is a replay, promoted from archaeology to a first-class question. New features — tier math, promo archaeology — read the existing stream instead of inventing new tables."

**Chair**: "Who may write to an account's stream?"

**Candidate**: "One owning service per aggregate type, always. The version constraint makes races safe, but the discipline is ownership: several writers to one stream means nobody owns its invariants, and the audit promise quietly dies."

**Chair**: "What about one account under furious concurrent contention?"

**Candidate**: "Review-worthy by definition: either the contended operation becomes a queue drained by a single writer per account, or it splits into independent events. A hot stream is an ownership signal, not a tuning knob."

---

## Second-Round Probes

- "Snapshots are wrong once in a while. Damage?" — bounded: rebuild the bad snapshot from the stream and compare with expected state; the log never became untrustworthy, only its cache did.
- "A handler folds events twice mid-crash. Result?" — none: folding is pure, so replay is idempotent by construction; danger only appears when a handler's side effect escapes the fold.
- "Serialization across years?" — each event carries a type and a payload version, and the fold upgrades legacy shapes on read through upcasting, so ancient rows stay loadable forever.
- "What does a dispute investigation feel like?" — open the account's stream at the date in question and read forward; every input that shaped the balance is right there, with no reconstruction from scattered logs.
- "Do we ever read our own writes?" — the command side confirms from the authoritative store; projections serve lists and dashboards, and no customer-facing decision is ever made from a view.

---

## Red Flag

Choosing event sourcing for the novelty of streams while admitting the product has no audit requirement. Replay machinery with no payoff buries the roadmap in event-schema ceremony.
