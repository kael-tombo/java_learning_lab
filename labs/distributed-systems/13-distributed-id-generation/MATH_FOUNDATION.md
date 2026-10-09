# Mathematical Foundations — ID Generation

## 1. Collision Probability (Birthday Problem)

The probability of at least one collision when generating k random IDs from a space of N possibilities:

P(collision) ≈ 1 - e^(-k(k-1)/(2N))

For UUID v4 (N = 2^122):
- k = 10^12: P ≈ 5.4e-15
- k = 10^15: P ≈ 0.0054

## 2. Snowflake ID Structure

`
0 | 00000000000000000000000 | 0000000000 | 000000000000
1 | 41-bit timestamp        | 10-bit ID  | 12-bit seq
`

Maximum IDs per second: 1024 × 4096 = 4,194,304

## 3. Timestamp Representation

Unix epoch in milliseconds: ~2^41 ms = 69.7 years from epoch

For post-epoch start (e.g., 2020-01-01):
41 bits from custom epoch: ~69.7 years from custom start

## 4. Encoding Efficiency

| Encoding | Bits/char | 128-bit length |
|----------|-----------|----------------|
| Hex | 4 | 32 chars |
| Base32 (Crockford) | 5 | 26 chars |
| Base62 | 5.95 | ~22 chars |
| Base64 | 6 | ~22 chars |

## 5. Monotonicity Guarantees

For time-based IDs, monotonicity requires:
- Clock skew ≤ sequence number capacity per millisecond
- If clock goes back: wait, use special sequence, or error

## 6. K-Ordered IDs

An ID scheme is k-ordered if IDs generated within k milliseconds of each other maintain order. Snowflake is 1-ordered (millisecond precision). Higher k means looser ordering guarantees.
