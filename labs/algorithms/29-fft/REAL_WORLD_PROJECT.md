# Real-World Project: Signal Smoother

## Problem

A sensor emits short noisy bursts sampled at 8 points. Operators want a
smoothed burst via convolution with a fixed [1,2,1] kernel. Build a smoother
that convolves with FFT and cross-checks against the naive sum.

## Inputs

- `bursts.txt`: one burst per line, 8 comma-separated decimals.
- Kernel fixed to [1,2,1]; divisor 4 applied after convolution.
- Power-of-two length 16 assumed with zero padding documented.

## Steps

1. Parse each line into exactly 8 decimals; reject malformed rows.
2. Zero-pad burst and kernel to length 16 (covers result length 10).
3. Forward-transform both with the radix-2 routine from this lab.
4. Pointwise-multiply the spectra and inverse-transform with 1/16 scaling.
5. Recompute the same convolution naively in O(nk) as the oracle.
6. Assert per-sample agreement within 1e-6 between FFT and naive paths.
7. Emit `smoothed.csv` with one smoothed burst per line (10 values).
8. Write a two-paragraph note on burst edges and kernel edge effects.

## Acceptance criteria

1. Reference burst [1,0,0,0,0,0,0,0] smooths to [1,2,1] over 4 divisor.
2. FFT and naive paths agree within 1e-6 on every accepted burst.
3. Output rows hold exactly 10 values (8 + 3 - 1).
4. Malformed rows exit with a message naming the line number.
5. Divisor documented in the file header and applied exactly once.
6. `smoothed.csv` contains one row per accepted input burst.
7. All output uses plain ASCII characters.

## Constraints

- Plain Java only, no external libraries; deterministic single run.
- Lengths fixed at 8 and 3; padding rule stated, not configurable.
- Naive oracle must stay in the submission, not a throwaway script.
