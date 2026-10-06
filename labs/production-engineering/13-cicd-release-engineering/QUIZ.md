# Lab 13: CI/CD Pipelines & Release Engineering — QUIZ

15 questions. Answer first. Target: 13/15.

---

**Q1. What is the difference between continuous delivery and continuous deployment?**
- A) They are synonyms
- B) Continuous delivery: every change that passes CI is *releasable* to production at any time, with a human or automated gate deciding when. Continuous deployment: that decision is automated and every passing change goes out by itself
- C) Continuous delivery means daily releases
- D) Continuous deployment requires feature flags

**Answer: B** — The distinction is about who holds the button. Many teams choose delivery (with progressive delivery doing the risk reduction) because some changes genuinely need human judgement.

---

**Q2. Why "build once, promote the same artifact" rather than rebuild per environment?**
- A) It is faster
- B) A rebuild can produce a different artifact (different dependency resolution, timestamp, base image digest, embedded config), so what you tested is not what you ship. Promotion must move the *same* digest
- C) CI caches require it
- D) It reduces storage

**Answer: B** — This is the core reproducible-builds argument. Verify with `sha256sum` on the promoted artifact and a digest check in the admission policy.

---

**Q3. Why is a rolling update's "safe" only relative to what you tested?**
- A) Rolling updates are always unsafe
- B) With `maxUnavailable: 0` you keep full capacity, but all instances run the new code within minutes; if the change is subtly wrong, you have fully deployed it. Progressive delivery (canary 1% → 25% → 100% with SLO gates) is what limits the blast radius
- C) Rolling updates require downtime
- D) They only update one pod

**Answer: B** — Availability and blast radius are separate concerns. Rollouts give you the first; canaries give you the second.

---

**Q4. Why does a canary need *automated* analysis rather than a human watching graphs?**
- A) Humans are bad at graphs
- B) The analysis must be a pre-declared, machine-evaluated SLO comparison (error rate, latency, saturation) against the canary and control, evaluated continuously, because the interesting failures are the subtle statistical ones nobody is watching at 03:00
- C) It is faster
- D) Tools require it

**Answer: B** — The value is not speed; it is that the decision rule was written *before* the data arrived, so it cannot be rationalised after the fact.

---

**Q5. What is the actual purpose of a feature flag?**
- A) To turn features on and off
- B) To separate *deploy* from *release*: deploy code that is inert, then enable it per user/cohort/percentage. It also enables progressive rollout of the feature itself and instant kill without a deploy
- C) To configure values
- D) To gate access

**Answer: B** — A flag without a removal date is technical debt with a toggle. Flags must have an owner and an expiry.

---

**Q6. Why is a flag read on the hot path a risk?**
- A) It is slow
- B) If the flag lookup is a network call (a remote config service), the flag store becomes a runtime dependency: its latency is in your p99, and its outage becomes your outage. Prefer locally-cached evaluation with a periodic refresh and a safe default
- C) Flags cannot be cached
- D) It consumes memory

**Answer: B** — Also: flags evaluated per-request with different values per user create cache-unfriendly behaviour and make testing harder.

---

**Q7. Expand-contract for a database change: what is the sequence?**
- A) Just run the migration
- B) Add the new column (nullable, no constraint) → deploy code that writes both and reads the old → backfill → deploy code that reads the new → add `NOT NULL`/constraints → switch reads → drop the old column later. Each step is separately reversible
- C) Rename the column in one migration
- D) Drop first, then add

**Answer: B** — The old code must keep working while both versions run, which means the new column must be additive and nullable until every writer is updated. A rename in one step guarantees downtime or a broken deploy.

---

**Q8. Why must migrations be backward compatible with the *currently deployed* code, not just the previous one?**
- A) For readability
- B) During a rolling update both versions serve traffic simultaneously, and during a rollback the old version may be redeployed after the migration is applied. So the schema must satisfy old and new code at the same time, in both directions
- C) For performance
- D) To keep the index

**Answer: B** — This is why "drop column" needs a separate, later release — after the rollback window has closed.

---

**Q9. What does a database migration lock risk look like in practice?**
- A) It is always instant
- B) `ALTER TABLE ... ADD COLUMN ... NOT NULL DEFAULT` (or a `CREATE INDEX` without `CONCURRENTLY`) takes an `ACCESS EXCLUSIVE` lock for the duration; on a large table that is seconds to minutes of blocked writes, which reads as an outage and can queue every query behind it
- C) It only affects reads
- D) It is a disk-space issue

**Answer: B** — Lock timeout is the mitigation that prevents a queue pile-up, and `CONCURRENTLY` (plus a check for invalid indexes) prevents the lock entirely. Verify your database's exact lock behaviour for your version.

---

**Q10. Why is rollback not always available?**
- A) Kubernetes cannot roll back
- B) If the change is a destructive migration, a data transformation, or a change to an event contract, the previous version cannot read the new state — so "roll forward with a fix" is the only option. This is why expand-contract exists and why you decide the rollback story before writing the migration
- C) Rollback is slow
- D) Images are immutable

**Answer: B** — Rollback is a capability you build or lose. The `kubectl rollout undo` of an incompatible schema is how you turn a bug into an outage.

---

**Q11. What makes a pipeline fast enough that people use it?**
- A) More runners
- B) Feedback latency: run the checks that fail most often first (compile + unit tests), parallelise independent stages, cache dependencies, run the expensive suites in parallel with the fast feedback, and fail fast. Target: fast feedback under ~10 minutes, full pipeline under ~20
- C) Skipping tests
- D) Bigger build machines

**Answer: B** — A pipeline nobody waits for gets bypassed. Measure per-stage duration and the queue wait, not just total time.

---

**Q12. What does a pipeline cache actually key on?**
- A) The source file only
- B) The lockfile (plus toolchain/JDK/Gradle image digest, flags, and plugin versions). Keying on the wrong inputs gives you a stale-artifact bug that looks like a flake
- C) The branch name
- D) The timestamp

**Answer: B** — For Maven, the checksum of `pom.xml` plus the effective resolved dependency set; for Gradle, `gradle.lockfile`. Include the JDK and base-image digest.

---

**Q13. In GitOps, what does drift mean and why does it matter?**
- A) Git and the cluster are the same
- B) The live state differs from the desired state in Git — someone changed it manually, or a controller failed. GitOps makes the cluster converge to Git continuously, so drift is detected and corrected automatically, and Git remains the only source of truth and audit record
- C) It means a failed sync
- D) It means version skew in dependencies

**Answer: B** — The value is not the sync tool; it is that the desired state is versioned, reviewed, and auditable. A manual `kubectl edit` becomes an event that gets reverted and logged.

---

**Q14. What is the "build metadata is environment" mistake?**
- A) Passing an env name at build time
- B) Embedding environment, secrets, or feature configuration into the image, so promotion requires a rebuild. The same artifact must be promotable; configuration belongs at runtime (env vars, mounted config, feature-flag service)
- C) Using multiple Dockerfiles
- D) Tagging images with the environment

**Answer: B** — This destroys the "build once" guarantee. It's also how credentials end up inside image layers, where they are readable by anyone who pulls the image.

---

**Q15. The single most common reason a release causes an incident is?**
- A) A bad developer
- B) A change that was never observed under production-like conditions — no canary, no SLO gate, no automatic rollback, and a rollout fast enough to reach 100% before anyone noticed. The fix is progressive delivery with pre-declared, machine-evaluated analysis
- C) A failed unit test
- D) A slow build

**Answer: B** — Speed of rollout is a risk multiplier. The single highest-leverage change most teams can make is a canary with automatic SLO analysis and automatic rollback.

---

## Scorecard
- 15–13: excellent — proceed to MINI_PROJECT and build a real pipeline.
- 12–10: revisit expand-contract, progressive delivery, and artifact promotion; redo EXERCISES 2–5.
- <10: re-read THEORY + ARCHITECTURE_DECISIONS cold and retake in 48 hours.
