# Mathematical Foundation: Security

## Rate Limiting Math
Token bucket: Available tokens(t) = min(capacity, token(t-Î”t) + rate * Î”t)
Probability of being rate-limited: P(block) = arrival_rate / refill_rate (assuming steady state)

## CSRF Token Entropy
Token should have at least 128 bits of entropy. Probability of guessing: P(guess) = 1 / 2^128
