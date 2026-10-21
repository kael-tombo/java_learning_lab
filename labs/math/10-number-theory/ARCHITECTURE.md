# Architecture: Number Theory Implementation

## Package Structure

`
com.math10/
    number theory.java     # Main implementation class
`

## Design Principles

### 1. Functional Design
- All methods are static utility functions
- No mutable state in the class
- Immutable input/output patterns

### 2. Error Handling
- Validate all inputs
- Throw specific exceptions for invalid inputs
- Use Java's standard exception hierarchy

### 3. Numerical Stability
- Use double precision for floating point
- Guard against division by zero
- Handle degenerate cases explicitly

### 4. Extensibility
- Methods accept functional interfaces (Function, BiFunction)
- Easy to add new algorithms
- Consistent API naming conventions

## Dependencies

- Java 21+ standard library
- java.util.function for functional interfaces
- java.math.BigInteger for arbitrary precision
- No external dependencies

## Class Diagram

The main class provides a collection of static methods organized by algorithm type. Each method is independent and thread-safe.
