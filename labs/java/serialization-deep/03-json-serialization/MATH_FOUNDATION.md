# JSON Serialization — Mathematical Foundation

## 1. String Encoding and Escaping

### Unicode Code Points
JSON strings are Unicode sequences encoded in UTF-8, UTF-16, or UTF-32:
- ASCII characters (U+0000-U+007F): 1 byte in UTF-8
- Latin-1 Supplement (U+0080-U+07FF): 2 bytes in UTF-8
- BMP (U+0800-U+FFFF): 3 bytes in UTF-8
- Supplementary (U+10000-U+10FFFF): 4 bytes in UTF-8 (surrogate pairs)

### Escape Sequences
Characters requiring escaping in JSON strings:
- Quotation mark: \u0022 -> 6 bytes
- Reverse solidus: \u005C -> 6 bytes  
- Control characters (U+0000-U+001F): \u00XX -> 6 bytes
- These effectively expand to 2-6 bytes in output

## 2. Number Handling

### JSON Number Format
JSON numbers are decimal literals:
- Integer: [+-]?[0-9]+
- Fraction: [+-]?[0-9]+\.[0-9]+
- Exponent: [+-]?[0-9]+(\.[0-9]+)?[eE][+-]?[0-9]+

### Precision Considerations
- Java double: 53-bit mantissa (~15-17 decimal digits)
- Java float: 24-bit mantissa (~6-9 decimal digits)
- JSON does not distinguish integer from floating-point
- Numbers beyond 2^53 lose precision when parsed as double

## 3. Array and Object Complexity

### Array Encoding
Array: [element1, element2, ..., elementN]
- Minimum overhead: 2 bytes ([] for empty array)
- Per-element separator: 1 byte (comma)
- Whitespace optional for compact output

### Object Encoding
Object: {"key1":value1, "key2":value2, ..., "keyN":valueN}
- Minimum overhead: 2 bytes ({} for empty object)  
- Per-field: key_string + "" + : + value + optional , 
- Key quoting and colon add 3 bytes per field minimum

## 4. Nesting Depth and Stack Usage

### Recursive Descent Parsing
For a JSON document with depth D:
- Recursive parser uses O(D) stack space
- Iterative parser uses O(D) heap space or O(1) with explicit stack
- Jackson default max depth: 1000 (configurable)

### Document Size vs Depth
Maximum depth typically log(n) for balanced structures but O(n) for degenerate cases.

## 5. Pretty Printing Mathematics

### Indentation Overhead
Pretty printing adds whitespace for readability:
- Each level: 2-4 spaces * line count
- Newlines after each element
- Typical overhead: 30-100% increase in document size

## Summary
JSON serialization mathematics involve string encoding, number precision, and structural overhead calculations essential for understanding serialization costs.
