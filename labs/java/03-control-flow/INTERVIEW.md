# Interview Questions: Control Flow

## Company-Specific Focus

### Google
- Advanced `switch` expression exhaustiveness checking and pattern matching interaction
- Loop unrolling and optimization: how does the JIT treat counted vs uncounted loops?
- `if`-heavy code refactoring into polymorphic dispatch for performance in latency-critical services

### Microsoft
- `switch` expression as a replacement for if-else chains in pipeline processing
- Guarded patterns in `when` clauses: similarity to C# pattern matching
- Nullable value types and flow analysis around `if (x != null)` patterns

### Amazon
- Loop optimization in high-throughput services: how for-each loop over an ArrayList compiles to indexed loop
- Avoid branching in hot paths: using arrays as jump tables
- Using `break` and `continue` with labels for multi-level loop control in graph traversals

### Meta
- Performance consequences of deep if-else chains on branch prediction
- For-each loop performance with different collection types in hot paths
- Short-circuit evaluation: impact on null-safety and performance

### Apple
- Using enhanced switch with sealed types for exhaustive pattern matching
- Preferring switch expressions over if-else for better control flow readability
- Definite assignment analysis: how the compiler checks variables are initialized before use

### Oracle
- Evolution of switch from statement to expression (JEP 325 preview → 354 → 361
  standard in 14), then pattern matching in switch (JEP 406 preview in 17 →
  441 standard in 21)
- Pattern matching for switch: JEP 441 in Java 21, combining type checking and destructuring
- How do switch on String, enum, and integer differ in compiled bytecode?
- Lambda control flow: restrictions on `break` and `continue` in lambdas

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| 20 Valid Parentheses | Easy | Amazon, Google, Microsoft | Stack + if-else for matching |
| 71 Simplify Path | Medium | Facebook, Apple | Splitting and switch on token types |
| 22 Generate Parentheses | Medium | Amazon, Bloomberg | Recursive backtracking with pruning |
| 394 Decode String | Medium | Google, Apple | Stack-based parsing with if-else conditions |
| 726 Number of Atoms | Hard | Amazon, Google | Control flow for tokenization and recursion |

## Real Production Scenarios
- **Stripe**: Outage caused by floating-point comparison in control flow — `if (x == y)` for computed doubles left edge cases unhandled
- **Twitter**: Deep statement-level if-else in payment flow caused a bug when a new region was introduced; refactored to enum-based dispatch
- **Netflix**: Switch on enum dropped a new case causing fall-through bug to a default handler; unreachable branch not caught at compile time

## Interview Patterns & Tips
- **Switch vs if-else**: Switch with String/Enum is compiled differently; the JVM uses tableswitch for dense int values, lookupswitch for sparse. JIT then optimizes further based on profile data
- **Fall-through in switch**: Unless you use the arrow form, the previous `break`-less semantics are preserved and can cause bugs
- **Try-with-resources**: Not just a syntax sugar: the compiler generates hidden code for exception suppression, which is critical for correct resource handling
- **For-each is not always safe**: If you modify the list in the loop (add/remove), you get `ConcurrentModificationException` — but only with fail-fast iterators
- **Labeled break**: Rarely used but very effective in nested loops; prevents the need for flags

## Deep Dive Questions
- **Compilation of switch**: How is a switch on String compiled? Show the process using hashcode lookup with collision verification.
- **JVM spec**: How does the JVM handle the difference between tableswitch and lookupswitch? When does it use each?
- **JIT optimization**: How does the JIT compiler handle a for loop with a variable upper bound vs a constant one? Loop unrolling, vectorization, null-check elimination.
- **Java 21+**: How does pattern matching in switch change the internal representation of switch expressions? What is the impact on the constant pool size?
- **Threading**: Are `break`, `continue`, and `return` inside a lambda body safe in a concurrent context? What happens to captured variables?
