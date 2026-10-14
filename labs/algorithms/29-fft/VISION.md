# Vision: FFT

## Direction

This lab covers the fast Fourier transform at use level: bit-reversal
ordering, radix-2 Cooley-Tukey combine with twiddle factors, inverse via
negated angles, and convolution through pointwise multiplication. The
practical skill is running a 4-point transform by hand and stating the
O(n log n) bound against naive O(n^2).

## What to learn

- Bit-reversal: why iterative radix-2 starts from permuted input.
- Combine step: even/odd halves joined with twiddle-factor weights.
- Inverse: negated-angle transform plus 1/n scaling, verified by roundtrip.
- Convolution theorem: time convolution equals frequency multiplication.
- Padding: zero-pad to a power of two covering the full result length.

## Non-coverage

- This lab does not cover number-theoretic transforms or finite fields.
- It does not cover 2D transforms or image-processing pipelines.
- It does not cover windowing, leakage, or spectral estimation practice.
- It does not cover FFTW-style planning or vectorized implementations.
- All signals here are 4-8 point teaching vectors with exact spectra.

## How to use this lab

Hand-reverse 3-bit indices before running Q1, verify the [1,1,1,1] spectrum
of Q2 against a naive DFT sum, then check the convolution of Q3 by direct
multiplication before trusting the transform path.

## Pitfalls

- Forgetting the 1/n scale after the inverse transform.
- Circular wraparound when padding is shorter than the true result.
- Rounding noise mistaken for signal; round only for display.

## Done when

- You can write the 8-index bit-reversal from memory.
- You can state the combine formula and the twiddle role.
- You can convert a convolution into transform-multiply-invert steps.
- You can name both padding rules (power of two, result length).
