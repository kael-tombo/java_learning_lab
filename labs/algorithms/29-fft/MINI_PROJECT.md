# Mini-Project: Frequency Detector

## Goal

Detect the dominant frequency bin of fixed 8-point test signals using the
radix-2 FFT from this lab, verified against hand-computed spectra.

## Inputs

- Signal A: constant [1,1,1,1,1,1,1,1] (all energy in bin 0).
- Signal B: alternating [1,-1,1,-1,1,-1,1,-1] (all energy in bin 4).
- No file input; magnitudes computed from complex outputs.

## Steps

1. Reuse the recursive radix-2 routine with interleaved complex arrays.
2. Transform signal A; compute bin magnitudes from real/imag parts.
3. Assert bin 0 magnitude is 8 and all other bins are below 1e-9.
4. Transform signal B; compute bin magnitudes the same way.
5. Assert bin 4 magnitude is 8 and all other bins are below 1e-9.
6. Print both magnitude spectra as rounded integer rows.
7. Roundtrip-check: inverse-transform A and compare within 1e-9.
8. State the bin-to-frequency mapping rule in two sentences.

## Acceptance criteria

1. Signal A reports peak bin 0 with magnitude 8.
2. Signal B reports peak bin 4 with magnitude 8.
3. Off-peak bins all below 1e-9 on both signals.
4. Both spectra printed as 8 rounded integers each.
5. Roundtrip error on signal A below 1e-9 per sample.
6. Mapping statement mentions sample rate over n explicitly.
7. All output uses plain ASCII characters.

## Grading note

- Peak bin 0 for signal A and peak bin 4 for signal B, magnitude 8.
- Off-peak bins below 1e-9 on both signals.
- Roundtrip error below 1e-9 per sample on signal A.

## Stretch

- Add signal C [1,0,-1,0,1,0,-1,0] and predict its peak before running.
- Halve the amplitude and confirm magnitudes scale linearly.
