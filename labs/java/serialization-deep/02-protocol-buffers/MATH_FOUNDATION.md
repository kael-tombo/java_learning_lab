# Protocol Buffers — Mathematical Foundation

## 1. Varint Encoding

### Variable-Length Integer Representation
Varint encoding uses 7 bits per byte for the value and 1 bit to indicate continuation:
- Each byte: 7 data bits + 1 continuation bit (MSB)
- Continuation bit = 1 means more bytes follow
- Continuation bit = 0 means this is the last byte

### Size Function
bytes(n) = floor(log2(n+1) / 7) + 1, for n >= 0

### Examples
- n = 0: 00000000 -> 1 byte
- n = 1: 00000001 -> 1 byte
- n = 127: 01111111 -> 1 byte
- n = 128: 10000000 00000001 -> 2 bytes
- n = 16383: 11111111 01111111 -> 2 bytes
- n = 2^32-1 (max uint32): 5 bytes
- n = 2^64-1 (max uint64): 10 bytes

## 2. ZigZag Encoding

### Signed Integer Mapping
ZigZag maps signed integers to unsigned integers:
- sint32: n -> (n << 1) ^ (n >> 31)
- sint64: n -> (n << 1) ^ (n >> 63)

### Examples
| Original | ZigZag | Varint Bytes |
|----------|--------|-------------|
| 0 | 0 | 1 |
| -1 | 1 | 1 |
| 1 | 2 | 1 |
| -2 | 3 | 1 |
| 2 | 4 | 1 |
| 2^30 | 2^31 | 5 |
| -2^30 | 2^31-1 | 5 |

## 3. Wire Type Mathematics

### Field Key Encoding
Each field in the stream is prefixed by a key:
key = (field_number << 3) | wire_type

### Wire Types
| Type | Number | Meaning | Used For |
|------|--------|---------|----------|
| Varint | 0 | int32, int64, uint32, uint64, sint32, sint64, bool, enum |
| 64-bit | 1 | fixed64, sfixed64, double |
| Length-delimited | 2 | string, bytes, embedded messages, packed repeated fields |
| Start group | 3 | groups (deprecated) |
| End group | 4 | groups (deprecated) |
| 32-bit | 5 | fixed32, sfixed32, float |

## 4. Message Size Calculation

### Single Field Size
- Varint field: key_size + value_size (varint)
- Fixed 64-bit: key_size + 8 bytes
- Length-delimited: key_size + length_varint + data_size
- Fixed 32-bit: key_size + 4 bytes

### Packed Repeated Fields
When using packed=true, repeated scalar fields are written as a single length-delimited blob:
packed_size = key_size + length_varint + Σ(field_value_sizes)

## 5. Default Value Optimization

### Omission of Default Values
In proto3, fields with default values are omitted from the serialized output:
- Numeric types: 0 is default (omitted)
- bool: false is default (omitted)
- string: empty string is default (omitted)
- enum: first value (0) is default (omitted)

### Impact
For a message where 80% of fields have default values, the serialized size can be reduced by 60-70%.

## 6. Hash Computation for Field Lookup

### Field Number Assignment
Field numbers 1-15 use 1-byte keys (favored for frequently used fields)
Field numbers 16-2047 use 2-byte keys
Field numbers 19000-19999 are reserved

## Summary
The mathematical foundation of Protocol Buffers centers on efficient integer encoding, enabling compact wire format with minimal overhead.
