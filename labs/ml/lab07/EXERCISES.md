# K-Means & Hierarchical Clustering - Exercises

**Track:** ml  |  **Lab:** lab07  |  **Level:** Intermediate

> Companion notes to the runnable lab. Everything here is grounded in the source under `src/`, so a claim you cannot reproduce is a claim you do not ship.

| Doc | Read it when you want |
|---|---|
| `THEORY.md` | the mental model and the assumptions |
| `MATH_FOUNDATION.md` | the formulas, the derivations, the numerical traps |
| `CODE_DEEP_DIVE.md` | the Java implementation, line by line |
| `EXERCISES.md` | deliberate practice, one deliverable at a time |
| `QUIZ.md` | to find the gaps before an interview |
| `FLASHCARDS.md` | spaced repetition on the day before a review |
| `VISION.md` | the career-level context and the anti-patterns to avoid |
| `MINI_PROJECT.md` | a self-contained build you finish in one sitting |
| `REAL_WORLD_PROJECT.md` | the production system, on-call runbook included |

## How To Work These

Work in order. Each exercise builds the next; do not skip ahead.
Every exercise ends with a *deliverable* you can show someone - code that compiles, a number you can defend, or a table you can regenerate.

Run the lab as you go:

```bash
cd lab07
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.ml.lab07.Main
```

## Exercise 1: Implement k-means from scratch

**Task.** Lloyd's algorithm plus k-means++ seeding.

**Steps**
- Implement k-means++ seeding.
- Implement assignment and update with an inertia cache.
- Verify on 3 synthetic blobs that k = 3 recovers them.
- Compare 1 restart against 10 on a harder dataset.

**Deliverable.** A verified implementation and an inertia comparison.

## Exercise 2: Choose k with evidence

**Task.** Elbow plus silhouette plus a business constraint.

**Steps**
- Compute inertia for k = 1..10 and print the curve.
- Compute mean silhouette for the same range.
- Print cluster sizes at each k.
- Pick k using all three and write the justification.

**Deliverable.** A curve table, size distributions and a written k decision.

## Exercise 3: Agglomerative with four linkages

**Task.** See the difference the linkage makes.

**Steps**
- Implement single, average, complete and Ward.
- Cluster a dataset with a bridging intermediate point.
- Print the dendrogram merges with heights for each linkage.
- Explain which linkage fails and why.

**Deliverable.** Four dendrograms and a written explanation of chaining.

## Exercise 4: Cut the dendrogram as a variance budget

**Task.** Turn the dendrogram into a decision.

**Steps**
- Implement cut(dendrogram, k) and cutByHeight().
- Find the height where Ward merge cost exceeds a variance budget.
- Compare that cut against cut-by-k.
- Check whether the resulting clusters agree.

**Deliverable.** Two cut strategies compared with an agreement metric.

## Exercise 5: Stability under resampling

**Task.** The only real validation available without labels.

**Steps**
- Bootstrap the data 20 times; recluster each sample.
- Match clusters across runs by maximum overlap (Hungarian-style greedy).
- Report the adjusted Rand index per pair.
- Conclude whether the segmentation is stable.

**Deliverable.** An ARI distribution and a stability verdict.

## Exercise 6: Outlier detection from cluster geometry

**Task.** Use the clustering to find rows worth inspecting.

**Steps**
- Compute each point's distance to its centroid.
- Flag points beyond the 99th percentile.
- Inspect the flagged rows for data-quality problems.
- Compare flags against a rule-based range check.

**Deliverable.** A flagged-row table and a note on whether they are bugs or genuine rare cases.

## Exercise 7: k-means++ versus random seeding

**Task.** Quantify the initialisation effect.

**Steps**
- Run 100 single-restart fits with random seeding.
- Run 100 single-restart fits with k-means++.
- Compare worst-case and mean final inertia.
- Compute the effective restart count needed.

**Deliverable.** A distribution comparison with a recommendation.

## Exercise 8: Ship a segment service

**Task.** Serve cluster assignments with an explanation payload.

**Steps**
- Serialise centroids and the scaler.
- Serve POST /segment returning cluster id, distance to centroid and the top distinguishing features.
- Assert assignments match offline.
- Log cluster population per day for drift.

**Deliverable.** A running endpoint and a population-by-day chart.


---

## Self-Check Before You Move On

- [ ] I chose k with a reason I can write down
- [ ] I print cluster sizes next to any quality score
- [ ] I can state the spherical assumption and when it fails
- [ ] My results are reproducible from a seed
