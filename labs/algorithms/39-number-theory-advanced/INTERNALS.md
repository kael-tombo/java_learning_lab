# Internals
PollardRho: uses BigInteger for modular multiplication to avoid overflow. Miller-Rabin deterministic primality test for 64-bit (bases 2,3,5,7,11,13,17). EllipticCurve: modular inverse via BigInteger.modInverse. Point at infinity as identity element.
