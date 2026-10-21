# Step-by-Step — Distributed ID Generation

## Step 1: Snowflake Generator
1. Define bit layout (timestamp, worker, sequence)
2. Implement timestamp extraction
3. Add sequence management
4. Handle clock rollback

## Step 2: UUID v7
1. Allocate bits per RFC 9562
2. Add timestamp component
3. Generate random component
4. Assemble 128-bit UUID

## Step 3: ULID
1. Implement timestamp encoding
2. Generate random component
3. Crockford Base32 encoding
4. Ensure monotonicity within ms

## Step 4: Testing
1. Concurrent generation tests
2. Uniqueness verification
3. Performance benchmarking
4. Monotonicity validation
