# Mental Models: JMM Foundations

## 1. The registered letter

A happens-before edge is a registered letter, not a shout. Shouting
(a plain write) may or may not be heard; the letter (volatile write,
unlock, countDown, start) is signed for on delivery (read, lock,
await, thread entry). The signature — the synchronization action both
sides agree on — is what makes the contents (all prior writes)
undeniably delivered. `LatchEdge` is the purest form: the graph rides
along with the signed receipt.

## 2. The relay baton

Hb chains are relay legs: program order runs the athlete to the line,
the synchronization rule passes the baton across teams, program order
runs it home. Drop any leg and the race is void — there is no partial
credit. StartEdge's 1000 writes are the first leg, `start()` the baton
pass, the child's reads the anchor leg. Review any handoff by naming
all three legs or conceding it is racy.

## 3. The court transcript

Sequential consistency is a court transcript: every action recorded in
one total order, each read seeing the latest write on record. DRF buys
the transcript — the court reporter (the JMM) guarantees one exists.
Racy programs have no reporter, only conflicting witness statements
(stale reads). Debugging racy code by arguing about "what really
happened" is arguing without a transcript: entertaining, inadmissible.

## 4. The inventory seal

A monitor is a storeroom with a numbered seal: each entrant breaks the
previous seal (acquire: see everything left inside), does work, and
affixes a new seal on exit (release: everything done is now inside).
The 2M-increment chain is 2M seal rotations — that is why the count is
exact. Touching the shelves without breaking the seal (unlocked access)
voids the inventory; the seal only covers what happens inside the room.

## 5. The family resemblance rule (causality)

Children resemble their parents: any value you meet must have a writer
it takes after (0..100000 in the probe, never −1, never a billion).
Strangers (42 from nowhere) are turned away at the door. But siblings
may arrive in any order, repeat visits, or skip town for a while —
resemblance constrains parentage, never scheduling. Do not mistake "all
real values" for "correct order."

## 6. The observable-behavior stage play

The audience (other threads, I/O) sees only the lit stage
(synchronization actions, external effects); backstage (plain
reorderings, eliminations) the crew rearranges freely. Two
performances with identical stage pictures are the same show by
definition — which licenses every backstage shortcut. Optimizations are
not cheating; playing a different lit scene would be.
