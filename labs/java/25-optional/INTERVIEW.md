# Interview Questions: Optional

## Company-Specific Focus

### Google
- Optional as a return type for methods that may not have a result
- Functional composition of Optional: map, flatMap, filter, orElse, orElseGet
- Optional as a monad: understanding its functional programming roots

### Microsoft
- Optional vs nullable reference types in C# 8+: design choices and differences
- Compatibility layer for null handling in the codebase

### Amazon
- Avoid Optional for fields and method parameters: causes confusion
- Using orElseThrow for clear contract on data presence
- Using flatMap to chain possibly null value dependencies in stream processing

### Meta
- The orElse vs orElseGet: orElse invalidates contract for eager eval of default
- Optional in streams: Collect to Optional

### Apple
- Prefer Optional for null-safe design
- Prefer not to use Optional of a collection for represent missing data

### Oracle
- No JEP covers `Optional` itself — it arrived in Java 8 as part of the Stream
  API work, which is a useful interview point: not every API decision had a JEP
- JLS and JVM: Optional is a simple generic class for null safety
- The Java language design decisions around this type as a return-only

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| 208 Implement Trie (Prefix Tree) | Medium | Amazon, Google, Apple | Optional for search results |
| 211 Design Add and Search Words Data Structure | Medium | Google, Amazon | Optional for fuzzy search presence |
| 285 Inorder Successor in BST | Medium | Amazon, Apple, Google | Optional for returned nulls |
| 173 Binary Search Tree Iterator | Medium | Google, Facebook, Microsoft | Using Optional for next item presence |
| 226 Invert Binary Tree | Easy | Meta | Not exactly Optional, but the pattern |

## Real Production Scenarios
- **Slack**: .orElse(method()) called every time (vs orElseGet) — causing a 10x slowdown with an expensive fallback computation
- **Uber**: Optional fields in POJO for GraphQL response — serialization issues with empty optionals appearing as null
- **Netflix**: Returning Optional<List> instead of List (empty list) caused special handling in the service client

## Interview Patterns & Tips
- **Optional is not serializable**: cannot be used in remote DTOs
- **Never use Optional for method parameters**: keep the signature clear, using overloads
- **Use orElseGet for expensive defaults**: orElse evaluates eagerly, orElseGet lazy

## Deep Dive Questions
- **JVM**: What is the size of an empty Optional in memory? (object header + value field + unshared object)
- **JIT**: Can Optional be eliminated by the JIT via escape analysis if the intermediate usage is inlined?
- **Performance**: What is the cost of the optional.ofNullable(value) pattern vs NullPointerException?
- **Boxing**: Does Optional<Integer> impose boxing overhead?
- **Memory**: How much does Optional wrapping cost in terms of GC?