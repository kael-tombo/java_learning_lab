# THEORY — Testing Deep Dive

## Overview

Comprehensive Java testing: unit, integration, contract, performance, and architectural testing with modern tools.

---

## JUnit 5 (Jupiter)

### Basic Annotations

```java
@Test
@DisplayName("Should calculate total with tax")
void testCalculateTotal() {
    Order order = new Order(List.of(item1, item2));
    assertEquals(110.0, order.calculateTotal(), 0.001);
}

@BeforeEach
void setUp() { }

@AfterEach
void tearDown() { }

@BeforeAll
static void setUpAll() { }

@AfterAll
static void tearDownAll() { }
```

### Assertions

```java
// Basic
assertEquals(expected, actual);
assertNotEquals(unexpected, actual);
assertTrue(condition);
assertFalse(condition);
assertNull(obj);
assertNotNull(obj);
assertSame(expected, actual);
assertNotSame(unexpected, actual);

// Numeric
assertEquals(expected, actual, delta);
assertThrows(Exception.class, () -> risky());

// Collections
assertIterableEquals(expected, actual);
assertArrayEquals(expected, actual);
assertLinesMatch(expectedLines, actualLines);

// All (multiple assertions)
assertAll(
    "order",
    () -> assertEquals(2, order.getItems().size()),
    () -> assertEquals(110.0, order.getTotal()),
    () -> assertTrue(order.isValid())
);

// Timeout
assertTimeout(Duration.ofMillis(100), () -> slowOperation());
assertTimeoutPreemptively(Duration.ofMillis(100), () -> slowOperation());
```

### Parameterized Tests

```java
@ParameterizedTest
@ValueSource(ints = {1, 2, 3, 5, 8})
void testFibonacci(int n) {
    assertEquals(expected[n], fibonacci(n));
}

@ParameterizedTest
@CsvSource({"1, 1", "2, 1", "3, 2", "5, 5"})
void testFibonacciCsv(int n, int expected) {
    assertEquals(expected, fibonacci(n));
}

@ParameterizedTest
@MethodSource("provideTestCases")
void testWithArguments(String input, String expected) {
    assertEquals(expected, processor.process(input));
}

static Stream<Arguments> provideTestCases() {
    return Stream.of(
        Arguments.of("hello", "HELLO"),
        Arguments.of("world", "WORLD")
    );
}
```

### Dynamic Tests

```java
@TestFactory
Stream<DynamicTest> dynamicTests() {
    return Stream.of("a", "b", "c")
        .map(input -> DynamicTest.dynamicTest(
            "Test " + input,
            () -> assertTrue(processor.isValid(input))
        ));
}
```

### Extensions

```java
@ExtendWith(MockitoExtension.class)
class ServiceTest {
    @Mock UserRepository repo;
    @InjectMocks UserService service;
    
    @Test
    void testFindUser() {
        when(repo.findById(1L)).thenReturn(Optional.of(user));
        assertEquals(user, service.findUser(1L));
    }
}

// Custom extension
public class DatabaseExtension implements BeforeEachCallback, AfterEachCallback {
    @Override
    public void beforeEach(ExtensionContext context) {
        Testcontainers.start();
    }
    @Override
    public void afterEach(ExtensionContext context) {
        Testcontainers.stop();
    }
}

@ExtendWith(DatabaseExtension.class)
class IntegrationTest { }
```

---

## Mockito

### Basic Mocking

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock PaymentGateway gateway;
    @Mock InventoryService inventory;
    @InjectMocks OrderService service;
    
    @Test
    void testPlaceOrder() {
        when(gateway.charge(any())).thenReturn(new ChargeResult(true));
        when(inventory.reserve(any())).thenReturn(true);
        
        OrderResult result = service.placeOrder(order);
        
        assertTrue(result.isSuccess());
        verify(gateway).charge(argThat(c -> c.getAmount() == 100));
        verify(inventory).reserve(order.getItems());
    }
}
```

### Argument Matchers

```java
any()
anyString()
anyInt()
eq(value)
argThat(customMatcher)
argThat(c -> c.getAmount() > 0)
isNull()
isNotNull()
contains("substring")
startsWith("prefix")
endsWith("suffix")
matches("regex")
```

### Verification

```java
verify(mock).method();           // Exactly once
verify(mock, times(2)).method(); // Exact count
verify(mock, never()).method();  // Never called
verify(mock, atLeastOnce()).method();
verify(mock, atMost(3)).method();
verify(mock, timeout(100)).method();  // Within timeout

verifyNoInteractions(mock);      // No calls at all
verifyNoMoreInteractions(mock);  // No unexpected calls

InOrder inOrder = inOrder(mock1, mock2);
inOrder.verify(mock1).first();
inOrder.verify(mock2).second();
```

### Stubbing

```java
when(mock.method()).thenReturn(value);
when(mock.method()).thenReturn(v1, v2, v3);  // Sequential
when(mock.method()).thenThrow(new RuntimeException());
when(mock.method()).thenAnswer(invocation -> {
    String arg = invocation.getArgument(0);
    return compute(arg);
});

doReturn(value).when(mock).voidMethod();
doThrow(new Exception()).when(mock).voidMethod();
doAnswer(invocation -> { ... }).when(mock).voidMethod();
doNothing().when(mock).voidMethod();
doCallRealMethod().when(mock).method();
```

### Spy (Partial Mock)

```java
List<String> spy = spy(new ArrayList<>());
spy.add("real");
when(spy.size()).thenReturn(100);  // Stubbed
spy.add("also real");
assertEquals(2, spy.size());  // Returns 100 (stubbed)
```

---

## Testcontainers (Integration Testing)

### Database

```java
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
    .withDatabaseName("test")
    .withUsername("test")
    .withPassword("test");

@DynamicPropertySource
static void configure(DynamicPropertyRegistry registry) {
    registry.add("spring.datasource.url", postgres::getJdbcUrl);
    registry.add("spring.datasource.username", postgres::getUsername);
    registry.add("spring.datasource.password", postgres::getPassword);
}
```

### Kafka

```java
@Container
static KafkaContainer kafka = new KafkaContainer("confluentinc/cp-kafka:7.5.0");

@DynamicPropertySource
static void configure(DynamicPropertyRegistry registry) {
    registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
}
```

### Redis

```java
@Container
static GenericContainer<?> redis = new GenericContainer<>("redis:7-alpine")
    .withExposedPorts(6379);
```

---

## Contract Testing (Pact)

### Consumer

```java
@ExtendWith(PactConsumerTestExt.class)
class UserClientContractTest {
    @TestTemplate
    @PactTestFor(providerName = "user-service")
    void testGetUser(MockServer mockServer) {
        UserClient client = new UserClient(mockServer.getUrl());
        User user = client.getUser("123");
        assertEquals("Alice", user.getName());
    }
}
```

### Provider

```java
@Provider("user-service")
@PactFolder("pacts")
class UserProviderContractTest {
    @TestTemplate
    @ExtendWith(PactVerificationInvocationContextProvider.class)
    void verify(PactVerificationContext context) {
        context.verifyInteraction();
    }
    
    @State("user 123 exists")
    void setupUser() {
        repo.save(new User("123", "Alice"));
    }
}
```

---

## ArchUnit (Architecture Testing)

```java
@AnalyzeClasses(packages = "com.example")
class ArchitectureTest {
    
    @ArchTest
    static final ArchRule controllers_only_in_web = classes()
        .that().resideInAPackage("..web..")
        .should().haveSimpleNameEndingWith("Controller");
    
    @ArchTest
    static final ArchRule services_not_access_repositories_directly = noClasses()
        .that().resideInAPackage("..service..")
        .should().accessClassesThat().resideInAPackage("..repository..");
    
    @ArchTest
    static final ArchRule no_cycles = slices()
        .matching("com.example.(*)..")
        .should().beFreeOfCycles();
    
    @ArchTest
    static final ArchRule only_dto_in_api = classes()
        .that().resideInAPackage("..api..")
        .should().haveSimpleNameEndingWith("DTO").or().haveSimpleNameEndingWith("Request");
}
```

---

## Performance Testing (JMH)

```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 3, time = 1)
@Measurement(iterations = 5, time = 1)
@Fork(3)
@State(Scope.Benchmark)
public class StringConcatBenchmark {
    
    @Param({"10", "100", "1000"})
    int size;
    
    List<String> strings;
    
    @Setup
    void setup() {
        strings = IntStream.range(0, size)
            .mapToObj(i -> "item" + i)
            .toList();
    }
    
    @Benchmark
    public String plus(Blackhole bh) {
        String result = "";
        for (String s : strings) result += s;
        bh.consume(result);
        return result;
    }
    
    @Benchmark
    public String builder(Blackhole bh) {
        StringBuilder sb = new StringBuilder();
        for (String s : strings) sb.append(s);
        bh.consume(sb.toString());
        return sb.toString();
    }
}
```

---

## Test Pyramid

```
        /\
       /  \  E2E / UI Tests (Few)
      /----\
     /      \  Integration Tests (Some)
    /--------\
   /          \  Unit Tests (Many)
  /------------\
```

| Level | Count | Speed | Scope |
|-------|-------|-------|-------|
| Unit | 70% | < 100ms | Single class |
| Integration | 20% | < 1s | Multiple components |
| Contract | 5% | < 5s | Service boundaries |
| E2E | 5% | < 30s | Full system |

---

## Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **One assertion per test** (or `assertAll`)
3. **Descriptive names**: `shouldReturnUserWhenExists`
4. **Test behavior, not implementation**
5. **Use `@Nested`** for organization
6. **Avoid test interdependence**
7. **Run in parallel**: `@Execution(CONCURRENT)`
8. **Tag tests**: `@Tag("slow")`, `@Tag("integration")`
9. **Clean up resources** in `@AfterEach`
10. **Deterministic tests** - no flaky tests