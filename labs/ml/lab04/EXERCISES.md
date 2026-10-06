# Support Vector Machines - Exercises

**Track:** ml  |  **Lab:** lab04  |  **Level:** Advanced

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
cd lab04
javac -d out $(Get-ChildItem -Recurse -Filter *.java src | ForEach-Object { $_.FullName })
java -cp out com.ml.lab04.Main
```

## Exercise 1: Hard-margin SVM by hand, then in code

**Task.** Solve the small case analytically and reproduce it with SMO.

**Steps**
- Take 4 separable points; find the optimal w and b analytically.
- Compute the margin and identify the support vectors.
- Run your SMO and compare w, b and margin to the analytic answer.
- Assert agreement to 1e-3.

**Deliverable.** Hand derivation plus a passing test that reproduces it in code.

## Exercise 2: Implement the kernel trick

**Task.** Add polynomial and RBF kernels and confirm they change the boundary.

**Steps**
- Implement Kernels.linear, poly(r,d), rbf(gamma).
- Verify the PSD property numerically on a 5-point Gram matrix.
- Show RBF with a huge gamma fitting the training set exactly.
- Show that with a small gamma the boundary stays nearly linear.

**Deliverable.** A Gram-matrix PSD check and two boundary comparisons.

## Exercise 3: Tune C and gamma properly

**Task.** Replace eyeballing with a validation surface.

**Steps**
- Run a 5×5 grid of (C, gamma) on 5-fold CV.
- Print the validation accuracy surface as text.
- Identify the plateau, not the single peak.
- Report held-out accuracy at the chosen point.

**Deliverable.** A 5×5 surface table, a chosen (C, gamma) and a one-paragraph justification.

## Exercise 4: Support-vector forensics

**Task.** Understand which rows the model actually uses.

**Steps**
- Report the support-vector fraction for a grid of C.
- Plot support-vector fraction vs C.
- Inspect which training rows are support vectors and look for data smells.
- Remove them and refit; report the change.

**Deliverable.** A fraction-vs-C curve and a short note on what the support vectors have in common.

## Exercise 5: Margin as a calibrated input

**Task.** Wrap the SVM in Platt scaling and measure the gain.

**Steps**
- Collect margins and labels on a validation split.
- Fit a 1-D logistic regression on the margin.
- Compute ECE before and after.
- Sweep the decision threshold on the calibrated probability.

**Deliverable.** Two reliability numbers and a threshold chosen on calibrated output.

## Exercise 6: Compare SVM against the rest of the track

**Task.** Benchmark the boundary shapes head to head.

**Steps**
- Train logistic regression, a single tree, and an SVM on the same data.
- Report held-out accuracy for each.
- Plot the three boundaries on one ASCII grid.
- Explain which assumptions each model is making about the data.

**Deliverable.** A comparison table plus an ASCII overlay of three boundaries.

## Exercise 7: Scalability cliff

**Task.** Find where the kernel matrix stops fitting.

**Steps**
- Precompute the kernel matrix for n = 1k, 2k, 4k, 8k.
- Record heap usage and training time for each.
- Switch to a linear kernel above the cliff and compare accuracy.
- Write the rule you would put in a config.

**Deliverable.** A memory/time table and a documented n threshold.

## Exercise 8: Ship a margin service

**Task.** Serve predictions with their margins and support-vector counts.

**Steps**
- Serialise alphas, support vectors and the scaler stats.
- Serve POST /classify returning label, margin and s = #support vectors.
- Assert offline and served margins agree to 1e-9.
- Log gamma, C and the training date in the response.

**Deliverable.** A running endpoint, a parity test and a sample response body.


---

## Self-Check Before You Move On

- [ ] I can write the dual objective from memory
- [ ] I can explain why only alpha > 0 points matter
- [ ] My best gamma came from a validation surface
- [ ] I can state the memory ceiling in rows of data
