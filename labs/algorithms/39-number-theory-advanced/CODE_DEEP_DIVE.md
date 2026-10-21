# Code Deep Dive
PollardRho: mulMod uses BigInteger to avoid 64-bit overflow. Recursive factor splits n into d and n/d. EllipticCurve: implements add/double/multiply using modular arithmetic. ContinuedFraction: tracks m, d, a variables in standard algorithm.
