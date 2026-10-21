# Refactoring

## Common Refactoring Patterns

### 1. Extract Method

Break long methods into smaller, focused ones. Each method should do one thing and have a clear name that describes what it does.

**Before:** A 50-line method mixing validation, business logic, and persistence.
**After:** Separate validate(), process(), and persist() methods.

### 2. Replace Conditional with Polymorphism

Replace if-else chains with polymorphic dispatch. Create an interface with implementations for each case.

### 3. Introduce Parameter Object

When a method has many parameters, group them into a single object. This reduces coupling and makes the code easier to change.

### 4. Extract Class

When a class has too many responsibilities, split it. Each new class should have a single, well-defined purpose.

### 5. Replace Inheritance with Composition

Prefer composition over inheritance. Use interfaces to define contracts and delegate to composed objects.

## Refactoring Workflow

1. Identify code smells (long methods, large classes, duplicated code)
2. Choose the appropriate refactoring pattern
3. Ensure existing tests pass before starting
4. Apply changes in small, safe steps
5. Run tests after each change
6. Commit when done

## Measuring Improvement

- Reduced cyclomatic complexity
- Fewer lines per method
- Higher test coverage
- Lower coupling between classes
- Improved naming and readability
