# Testing — Quiz

## Question 1
What annotation marks a method as a JUnit 5 test?
- A) @Test
- B) @Run
- C) @TestCase
- D) @Unit

**Answer: A**

## Question 2
Which annotation runs a method before each test?
- A) @BeforeAll
- B) @BeforeEach
- C) @Before
- D) @Setup

**Answer: B**

## Question 3
How do you verify a method was called exactly 3 times with Mockito?
- A) erify(mock, times(3)).method()
- B) erify(mock).method(3)
- C) erify(mock, exactly(3)).method()
- D) erify(mock).method().times(3)

**Answer: A**

## Question 4
Which assertion checks that a specific exception is thrown?
- A) ssertThrow
- B) ssertThrows
- C) expectException
- D) catchException

**Answer: B**

## Question 5
What is the correct TDD cycle order?
- A) Green → Red → Refactor
- B) Red → Green → Refactor
- C) Refactor → Red → Green
- D) Green → Refactor → Red

**Answer: B**

## Question 6
Which Mockito annotation creates a mock and injects it into the tested object?
- A) @Mock
- B) @InjectMocks
- C) @Spy
- D) @Captor

**Answer: B**

## Question 7
What does @ParameterizedTest with @ValueSource(ints = {1, 2, 3}) do?
- A) Runs the test 3 times with values 1, 2, 3
- B) Runs the test once with the array [1,2,3]
- C) Skips the test
- D) Generates random values

**Answer: A**

## Question 8
What is the purpose of erifyNoInteractions(mock)?
- A) Verifies mock has no stubs
- B) Verifies no methods were called on the mock
- C) Removes all stubs from the mock
- D) Checks mock state is clean

**Answer: B**

## Question 9
Which of these is NOT a test type in the testing pyramid?
- A) Unit test
- B) Integration test
- C) Performance test
- D) End-to-end test

**Answer: C**

## Question 10
What does ssertAll do?
- A) Runs all assertions, reporting all failures
- B) Stops at first failure
- C) Runs assertions in parallel
- D) Skips remaining assertions after first failure

**Answer: A**
