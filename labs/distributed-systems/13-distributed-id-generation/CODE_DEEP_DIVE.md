# Code Deep Dive — ID Generation

## 1. IdGenerator Interface

`java
public interface IdGenerator<T> {
    T generate();
    long extractTimestamp(T id);
}
`

## 2. Snowflake Implementation

Key fields:
- epoch: custom epoch in milliseconds
- workerIdBits: number of bits for worker ID
- sequenceBits: number of bits for sequence
- sequence: current sequence within millisecond
- lastTimestamp: last generated timestamp

### generate() Logic
1. Get current timestamp
2. If same as last: increment sequence
3. If sequence exhausted: wait for next millisecond
4. If timestamp < last: handle clock rollback
5. Compose: (timestamp - epoch) << bits | workerId << seqBits | sequence

### Clock Rollback Handling
- If drift < 10ms: spin-wait for clock to catch up
- If drift >= 10ms: throw exception (system clock is severely off)

## 3. UUID v7 Implementation

Generates RFC 9562-compliant UUID v7:
- 48-bit timestamp (milliseconds since Unix epoch)
- 4-bit version (7)
- 74 random bits (2-bit variant + 72 random)
- 12-bit variant and reserved

### Structure
`
0                   48    52    56       64
|--- timestamp ms ---| ver | rand_a |
64                  72    80       128 (not to scale)
|---- rand_b ----|-- variant -- rand_c --|
`

## 4. ULID Implementation

26-character Crockford Base32 encoding:
- First 10 chars: timestamp
- Last 16 chars: random component

### Monotonicity
Within the same millisecond, increment the random component to maintain order.
When random component overflows (80 bits), wait for next millisecond.

## 5. Testing Strategy

- Concurrent generation from multiple threads
- Verify no duplicates in large batches (10M+)
- Verify monotonic order within same node
- Verify timestamp extraction correctness
- Benchmark throughput across configurations
