# Testing — Mental Models

## Model 1: The Safety Net

Think of tests as a safety net stretched beneath a tightrope walker. The tightrope walker is your code changing over time. Without the net, one slip means catastrophic failure (production bug). With the net, you can walk confidently, knowing falls are caught.

- **Unit tests**: Fine-mesh net close to the rope
- **Integration tests**: Stronger net at medium height
- **E2E tests**: Heavy-duty net at the bottom

## Model 2: The Specification Contract

Tests are legal contracts between modules. Module A promises: "If you call me with X, I return Y." The test verifies this promise. When Module A changes, its tests ensure the contract still holds — or they break, forcing the developer to update the contract.

## Model 3: The Change Detector

Each test is a sensor that detects when behavior changes. A good test suite has sensors at every critical junction:
- **Input sensors**: Tests that call public APIs with various inputs
- **State sensors**: Tests that verify object state after operations
- **Interaction sensors**: Tests that verify module interactions (Mockito verify)
- **Boundary sensors**: Tests at edge cases (zero, null, empty, max values)

## Model 4: The Regression Net

Regression is code that used to work but stopped working after a change. Tests catch regressions. Think of test coverage as a net woven from passing assertions — every hole in the net is a possible regression escape route.

## Model 5: TDD — The Design Tool

TDD is not primarily about testing — it's about design. Writing the test first forces you to think about:
- What is the public API?
- What are the inputs and outputs?
- How do I instantiate and use this class?
- What are the failure modes?

This leads to better-designed, loosely coupled, testable code from the start.
