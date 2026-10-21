# Security Considerations

1. Validate query ranges
2. Handle empty arrays gracefully
3. Limit array size to prevent O(n log n) memory exhaustion
4. Use long for index/offset calculations to prevent overflow
5. Validate that data type can represent the operation result
