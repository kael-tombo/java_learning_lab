# Common Mistakes in Testing

## 1. Testing Implementation Details

`java
// BAD — tests internal state
@Test
void addTest() {
    calc.add(2, 3);
    assertEquals(5, calc.getResult());
}

// GOOD — tests behavior
@Test
void addTest() {
    assertEquals(5, calc.add(2, 3));
}
`

Test what the code *does*, not how it *does it*. Implementation tests break when you refactor.

## 2. Mocking Everything

Not every dependency should be mocked. Mock external boundaries (network, database, filesystem). Use real objects for value types and domain logic.

## 3. Assertion Without Message

`java
// BAD
assertEquals(5, result);

// GOOD
assertEquals("Result should be 5", 5, result);
`

Messages help diagnose failures.

## 4. Forgetting to Verify Side Effects

`java
// BAD — only asserts return value
service.notifyUser(1L, "Hello");
// But did the notification actually get sent?

// GOOD — verify interaction
verify(notificationService).send(anyString(), eq("Hello"));
`

## 5. Fragile Tests

`java
// BAD — hardcoded IDs
when(repo.findById(42L)).thenReturn(user);

// BETTER — anyLong()
when(repo.findById(anyLong())).thenReturn(user);
`

Use argument matchers to make tests less brittle.

## 6. Not Testing Edge Cases

Always test: null inputs, empty collections, negative numbers, max/min values, zero, and error conditions.

## 7. Test Order Dependencies

`java
// BAD — tests depend on shared mutable state
static int counter = 0;
@Test void test1() { counter = 1; }
@Test void test2() { assertEquals(1, counter); } // May or may not pass
`

Each test should be independent. Use @BeforeEach to reset state.

## 8. Skipping the "Refactor" Phase of TDD

Going from RED to GREEN is only half the work. Always refactor to clean code before moving on.
