# Mini-Project: Step-Size Explorer

## Goal

Run gradient descent on f(x) = (x-3)^2 from x=0 with three step sizes and
show which converges, which crawls, and which diverges.

## Inputs

- Fixed function f(x) = (x-3)^2, gradient 2(x-3), 20 iterations each.
- Step sizes 0.1 (small), 0.4 (good), 1.1 (overshoot).

## Steps

1. Implement descent as a function of start, step, and iteration count.
2. Run with step 0.1; record final x and f.
3. Run with step 0.4; record final x and f.
4. Run with step 1.1; record final x and f (expect blowup or oscillation).
5. Print a table of (step, final x, final f).
6. Assert step 0.4 lands within 1e-6 of x=3.
7. Assert step 1.1 ends farther than it started (divergence check).
8. Write a three-sentence verdict on step-size choice.

## Acceptance criteria

1. Table contains all three step sizes with final x and f.
2. Step 0.4 row shows x within 1e-6 of 3.0.
3. Step 1.1 row shows |x - 3| greater than the starting distance 3.
4. Descent function reused for all three runs (no copy-paste loops).
5. Verdict names overshoot as the divergence mechanism.
6. Iteration count fixed at 20 for every run.
7. All output uses plain ASCII characters.

## Grading note

- Table must hold all three step sizes with final x and f.
- Step 0.4 within 1e-6 of 3.0; step 1.1 farther than start.
- One shared descent function; copy-paste loops fail review.

## Stretch

- Add step 0.9 and locate the stability boundary by bisection in words.
- Plot f per iteration as ASCII bars for the 0.4 run.
