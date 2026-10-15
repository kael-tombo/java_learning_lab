# Feature Stores — References

All entries are real publications. Verify editions locally.

1. Kleppmann, M. "Designing Data-Intensive Applications" (O'Reilly).
   Storage, logs, batch/stream processing behind offline/online stores.
2. Sculley, D. et al. "Hidden Technical Debt in Complex Machine
   Learning Systems" (NIPS 2015). Boundary erosion, correction
   cascades, why shared infrastructure matters.
3. Zinkevich, M. "Rules of Machine Learning: Best Practices for ML
   Engineering" (Google, living guide). Skew rules, serving-time
   logging, freshness monitoring.
4. Breck, E. et al. "The ML Test Score: A Rubric for ML Production
   Readiness" — data/model validation practices adjacent to store
   validation gates.
5. Hastie, T., Tibshirani, R., Friedman, J. "The Elements of
   Statistical Learning." Background on features vs labels; not
   store-specific but standard.

## How each source is used in this lab
- Kleppmann answers storage questions: why the offline log is
  append-only, why the online index is a derived view, and what
  breaks when the two disagree.
- Sculley et al. answers process questions: which failure anecdotes
  (entanglement, cascades) each store component is designed to stop.
- Zinkevich answers operations questions: what to monitor (skew,
  freshness, coverage drops) and who owns each feature.
- Breck et al. answers gating questions: which validation checks run
  before a backfilled version is marked live.
- Hastie et al. answers modeling questions: what features and labels
  mean once the store has delivered correct rows.

No vendor docs, no invented papers, no URLs beyond the well-known
Google rules guide already noted in the repo field notes.
