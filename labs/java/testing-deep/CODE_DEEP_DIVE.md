# Code Deep Dive - Deep Java Testing (testing-deep)

Six topics, each with a short mechanism note, a complete snippet, the output observed when it was run, and one pitfall.

Conventions used in this file:

- JUnit 5, Mockito, AssertJ, Testcontainers and PIT are third-party. Every snippet that uses them starts with a `// Requires <artifact>; not compiled in this repo` line (or an XML comment for Maven) and has no observed output.
- Next to each external snippet there is a JDK-only demonstration of the underlying idea: a hand-rolled test runner, table-driven checks, a dynamic proxy that records calls, a fluent assertion class, a readiness probe, and hand-written mutants. Those were extracted from this file, compiled with `javac --release 21 -proc:none`, run on JDK 23, and their output pasted verbatim.

## Snippet 1: JUnit5 lifecycle & extensions

By default JUnit Jupiter creates a new instance of the test class for every test method, runs `@BeforeEach` methods, the test, then `@AfterEach` methods, so instance fields never leak from one test to the next; `@BeforeAll`/`@AfterAll` run once and (with the default lifecycle) must be `static`. Extensions plug into those same points through callback interfaces such as `BeforeEachCallback`, `AfterEachCallback` and `ParameterResolver`, and are registered with `@ExtendWith` or `@RegisterExtension`.

```java
// Requires org.junit.jupiter:junit-jupiter (JUnit 5); not compiled in this repo
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.AfterEachCallback;
import org.junit.jupiter.api.extension.BeforeEachCallback;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.api.io.TempDir;

@ExtendWith(LifecycleTest.TimingExtension.class)
class LifecycleTest {

    static class TimingExtension implements BeforeEachCallback, AfterEachCallback {
        private static final ExtensionContext.Namespace NS = ExtensionContext.Namespace.create(TimingExtension.class);

        @Override
        public void beforeEach(ExtensionContext context) {
            context.getStore(NS).put("start", System.nanoTime());
        }

        @Override
        public void afterEach(ExtensionContext context) {
            long start = context.getStore(NS).remove("start", long.class);
            System.out.println(context.getDisplayName() + " took " + (System.nanoTime() - start) + " ns");
        }
    }

    private int counter; // reset for every test because each test gets a new instance

    @BeforeAll
    static void startSharedResource() {
        System.out.println("once before all tests");
    }

    @BeforeEach
    void setUp() {
        counter = 10;
    }

    @AfterEach
    void tearDown() {
        System.out.println("after each, counter was " + counter);
    }

    @AfterAll
    static void stopSharedResource() {
        System.out.println("once after all tests");
    }

    @Test
    @DisplayName("increment once")
    void incrementOnce() {
        counter++;
        assertEquals(11, counter);
    }

    @Test
    void writesIntoTempDir(@TempDir Path dir) throws Exception {
        Path file = Files.writeString(dir.resolve("a.txt"), "hello");
        assertEquals("hello", Files.readString(file));
    }

    @Test
    void rejectsNegative() {
        assertThrows(IllegalArgumentException.class, () -> {
            throw new IllegalArgumentException("negative");
        });
    }

    @Nested
    class WhenEmpty {
        @Test
        void startsFromParentSetUp() {
            assertEquals(10, counter); // the outer @BeforeEach also runs for nested tests
        }
    }
}
```

JDK-only miniature of the same lifecycle: a reflection-based runner with `@Test`, `@BeforeEach`, `@AfterEach`, one fresh instance per test.

```java
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

public class MiniRunnerDemo {

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    @interface Test {}

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    @interface BeforeEach {}

    @Retention(RetentionPolicy.RUNTIME)
    @Target(ElementType.METHOD)
    @interface AfterEach {}

    static class CounterTests {
        static int instances = 0;

        final int id = ++instances;
        int counter = 0;

        @BeforeEach
        void setUp() {
            System.out.println("  [instance " + id + "] beforeEach");
            counter = 10;
        }

        @AfterEach
        void tearDown() {
            System.out.println("  [instance " + id + "] afterEach, counter=" + counter);
        }

        @Test
        void incrementOnce() {
            counter++;
            check(counter == 11, "expected 11 but was " + counter);
        }

        @Test
        void incrementTwice() {
            counter += 2;
            check(counter == 12, "expected 12 but was " + counter);
        }

        @Test
        void wrongExpectation() {
            counter++;
            check(counter == 99, "expected 99 but was " + counter);
        }
    }

    static void check(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    static void invoke(Object target, Method m) throws Throwable {
        m.setAccessible(true);
        try {
            m.invoke(target);
        } catch (InvocationTargetException e) {
            throw e.getCause();
        }
    }

    static List<Method> annotated(Class<?> type, Class<? extends java.lang.annotation.Annotation> annotation) {
        return Arrays.stream(type.getDeclaredMethods())
                .filter(m -> m.isAnnotationPresent(annotation))
                .sorted(Comparator.comparing(Method::getName)) // reflection order is unspecified, so sort
                .toList();
    }

    static void run(Class<?> type) throws Exception {
        int passed = 0;
        int failed = 0;
        for (Method test : annotated(type, Test.class)) {
            Object instance = type.getDeclaredConstructor().newInstance(); // new instance per test
            System.out.println("running " + test.getName());
            try {
                for (Method before : annotated(type, BeforeEach.class)) {
                    invoke(instance, before);
                }
                invoke(instance, test);
                System.out.println("  PASS");
                passed++;
            } catch (Throwable t) {
                System.out.println("  FAIL: " + t.getMessage());
                failed++;
            } finally {
                for (Method after : annotated(type, AfterEach.class)) {
                    try {
                        invoke(instance, after);
                    } catch (Throwable t) {
                        System.out.println("  afterEach failed: " + t);
                    }
                }
            }
        }
        System.out.println("passed=" + passed + " failed=" + failed + " instancesCreated=" + CounterTests.instances);
    }

    public static void main(String[] args) throws Exception {
        run(CounterTests.class);
    }
}
```

Observed output (`java MiniRunnerDemo`):

```text
running incrementOnce
  [instance 1] beforeEach
  PASS
  [instance 1] afterEach, counter=11
running incrementTwice
  [instance 2] beforeEach
  PASS
  [instance 2] afterEach, counter=12
running wrongExpectation
  [instance 3] beforeEach
  FAIL: expected 99 but was 11
  [instance 3] afterEach, counter=11
passed=2 failed=1 instancesCreated=3
```

**Pitfall:** `@TestInstance(TestInstance.Lifecycle.PER_CLASS)` makes JUnit reuse one instance for the whole class (it also lets `@BeforeAll` be non-static). Fields set by one test then stay visible to the next, as if the three `instance` ids above had all been `1`, and since JUnit's default method order is deterministic but deliberately non-obvious, a hidden dependency between two tests stays invisible until someone adds, renames or reorders a test. Keep the default lifecycle, or reset every field in `@BeforeEach`.

## Snippet 2: parameterized tests

A parameterized test is one method run once per argument row, and each run is reported as its own test with a name built from the row; in JUnit 5 the rows come from an annotation source (`@ValueSource`, `@CsvSource`, `@EnumSource`, `@MethodSource`). A failing row does not stop the others, and the display name template (`{0}`, `{1}`, `{index}`) is what makes a failure readable.

```java
// Requires org.junit.jupiter:junit-jupiter-params (and junit-jupiter-api); not compiled in this repo
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.DayOfWeek;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.EnumSource;
import org.junit.jupiter.params.provider.MethodSource;
import org.junit.jupiter.params.provider.ValueSource;

class LeapYearTest {

    static boolean isLeap(int year) {
        return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0;
    }

    @ParameterizedTest
    @ValueSource(ints = {4, 2000, 2024})
    void leapYears(int year) {
        assertTrue(isLeap(year));
    }

    @ParameterizedTest(name = "{0} -> leap={1}")
    @CsvSource({"2024, true", "2023, false", "1900, false", "2000, true"})
    void table(int year, boolean expected) {
        assertEquals(expected, isLeap(year));
    }

    @ParameterizedTest
    @EnumSource(value = DayOfWeek.class, names = {"SATURDAY", "SUNDAY"})
    void weekend(DayOfWeek day) {
        assertTrue(day.getValue() >= 6);
    }

    static Stream<Arguments> centuries() {
        return Stream.of(Arguments.of(1800, false), Arguments.of(2400, true));
    }

    @ParameterizedTest
    @MethodSource("centuries")
    void centuryRule(int year, boolean expected) {
        assertEquals(expected, isLeap(year));
    }
}
```

JDK-only table-driven version, with the rows given as text in `@CsvSource` style and a deliberately buggy implementation (it forgets the 400-year rule):

```java
import java.util.ArrayList;
import java.util.List;

public class TableDrivenDemo {

    record Row(int year, boolean expected) {}

    static boolean isLeapBuggy(int year) {
        return year % 4 == 0 && year % 100 != 0; // missing: || year % 400 == 0
    }

    static List<Row> parse(String csv) {
        List<Row> rows = new ArrayList<>();
        for (String line : csv.strip().split("\n")) {
            String[] parts = line.split(",");
            rows.add(new Row(Integer.parseInt(parts[0].trim()), Boolean.parseBoolean(parts[1].trim())));
        }
        return rows;
    }

    public static void main(String[] args) {
        List<Row> rows = parse("""
                2024, true
                2023, false
                1900, false
                2000, true
                2100, false
                """);

        int failures = 0;
        for (int i = 0; i < rows.size(); i++) {
            Row row = rows.get(i);
            boolean actual = isLeapBuggy(row.year());
            String status = actual == row.expected() ? "PASS" : "FAIL";
            if (actual != row.expected()) {
                failures++;
            }
            System.out.println("[" + (i + 1) + "] " + row.year() + " -> leap=" + row.expected() + " : " + status
                    + (status.equals("FAIL") ? " (actual " + actual + ")" : ""));
        }
        System.out.println(rows.size() + " rows, " + failures + " failed; every row ran even after a failure");
    }
}
```

Observed output (`java TableDrivenDemo`):

```text
[1] 2024 -> leap=true : PASS
[2] 2023 -> leap=false : PASS
[3] 1900 -> leap=false : PASS
[4] 2000 -> leap=true : FAIL (actual false)
[5] 2100 -> leap=false : PASS
5 rows, 1 failed; every row ran even after a failure
```

**Pitfall:** a table of cases only covers what its author thought of. The failing row above (`2000`) exists only because the author remembered the century exception; with just the first three rows the buggy `isLeap` would pass. Also, `@CsvSource` converts every cell with implicit conversion rules and treats an empty cell as `null` and a quoted `''` as an empty string, so a row meant to test an empty string can silently test `null` instead. Name the rows (`name = "{0} -> leap={1}"`) so that a failure report states the input.

## Snippet 3: Mockito stubbing/verification

Mockito creates a subclass or proxy of the target type at run time, so every call goes through an interceptor that first looks for a matching stub (`when(...).thenReturn(...)`) and otherwise returns a default (`0`, `false`, `null`, or an empty collection), and in either case records the invocation so `verify(...)` can later count and inspect it. Matching on arguments uses `equals` unless you use matchers like `any()` or `eq(...)`.

```java
// Requires org.mockito:mockito-core and org.mockito:mockito-junit-jupiter (plus org.junit.jupiter:junit-jupiter); not compiled in this repo
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    interface PriceService {
        double priceOf(String sku);

        void audit(String message);
    }

    static class OrderService {
        private final PriceService prices;

        OrderService(PriceService prices) {
            this.prices = prices;
        }

        double total(List<String> skus) {
            double sum = 0;
            for (String sku : skus) {
                sum += prices.priceOf(sku);
            }
            prices.audit("total=" + sum);
            return sum;
        }
    }

    @Mock
    PriceService prices;

    @InjectMocks
    OrderService orders;

    @Test
    void sumsPricesAndAuditsOnce() {
        when(prices.priceOf("A")).thenReturn(2.5);
        when(prices.priceOf("B")).thenReturn(4.0);

        assertEquals(6.5, orders.total(List.of("A", "B")));

        verify(prices, times(2)).priceOf(anyString());
        ArgumentCaptor<String> message = ArgumentCaptor.forClass(String.class);
        verify(prices).audit(message.capture());
        assertEquals("total=6.5", message.getValue());
        verify(prices, never()).priceOf(eq("C"));
        verifyNoMoreInteractions(prices);
    }

    @Test
    void propagatesAuditFailure() {
        when(prices.priceOf("A")).thenReturn(1.0);
        doThrow(new IllegalStateException("audit down")).when(prices).audit(anyString());

        org.junit.jupiter.api.Assertions.assertThrows(IllegalStateException.class, () -> orders.total(List.of("A")));
    }
}
```

JDK-only version of the mechanism: a `java.lang.reflect.Proxy` with an `InvocationHandler` that returns stubbed values, defaults otherwise, and records every call.

```java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class RecordingProxyDemo {

    interface PriceService {
        double priceOf(String sku);

        void audit(String message);
    }

    static class OrderService {
        private final PriceService prices;

        OrderService(PriceService prices) {
            this.prices = prices;
        }

        double total(List<String> skus) {
            double sum = 0;
            for (String sku : skus) {
                sum += prices.priceOf(sku);
            }
            prices.audit("total=" + sum);
            return sum;
        }
    }

    static final class Recorder implements InvocationHandler {
        final Map<String, Object> stubs = new HashMap<>();
        final List<String> calls = new ArrayList<>();

        static String key(String method, Object... args) {
            return method + Arrays.toString(args);
        }

        void stub(Object value, String method, Object... args) {
            stubs.put(key(method, args), value);
        }

        @Override
        public Object invoke(Object proxy, java.lang.reflect.Method method, Object[] args) {
            String key = key(method.getName(), args == null ? new Object[0] : args);
            calls.add(key);
            if (stubs.containsKey(key)) {
                return stubs.get(key);
            }
            Class<?> type = method.getReturnType();
            if (type == double.class) {
                return 0.0;
            }
            if (type == int.class) {
                return 0;
            }
            if (type == boolean.class) {
                return false;
            }
            return null; // void and object returns
        }

        long count(String key) {
            return calls.stream().filter(key::equals).count();
        }

        void verifyTimes(int expected, String key) {
            long actual = count(key);
            if (actual != expected) {
                throw new AssertionError("Wanted " + expected + " time(s) " + key + " but was " + actual);
            }
        }
    }

    static <T> T mock(Class<T> type, Recorder recorder) {
        return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] {type}, recorder));
    }

    public static void main(String[] args) {
        Recorder recorder = new Recorder();
        recorder.stub(2.5, "priceOf", "A");
        recorder.stub(4.0, "priceOf", "B");
        PriceService prices = mock(PriceService.class, recorder);

        double total = new OrderService(prices).total(List.of("A", "B", "C"));
        System.out.println("total = " + total + " (C was never stubbed, so it returned the default 0.0)");
        System.out.println("recorded calls: " + recorder.calls);

        recorder.verifyTimes(1, "audit[total=6.5]");
        System.out.println("verify(audit total=6.5, times(1)) passed");
        try {
            recorder.verifyTimes(2, "priceOf[A]");
        } catch (AssertionError e) {
            System.out.println("verify failed: " + e.getMessage());
        }

        try {
            mock(OrderService.class, recorder);
        } catch (IllegalArgumentException e) {
            System.out.println("proxy of a class: " + e.getMessage());
        }
    }
}
```

Observed output (`java RecordingProxyDemo`):

```text
total = 6.5 (C was never stubbed, so it returned the default 0.0)
recorded calls: [priceOf[A], priceOf[B], priceOf[C], audit[total=6.5]]
verify(audit total=6.5, times(1)) passed
verify failed: Wanted 2 time(s) priceOf[A] but was 1
proxy of a class: RecordingProxyDemo$OrderService is not an interface
```

**Pitfall:** the unstubbed `priceOf("C")` returned `0.0` and the order silently totalled without it. Mockito's default answers behave the same way (`0`, `false`, `null`, empty collections, not an error), so a mock created with plain `mock(...)` and an incomplete stub can pass for the wrong reason. `MockitoExtension` is stricter: its strict stubs report stubs that were never used and calls to a stubbed method with different arguments, but a method that has no stub at all still just returns the default. A second failure mode is argument matchers: in Mockito, if any argument in a call uses a matcher, all of them must (`when(map.put(any(), "x"))` throws `InvalidUseOfMatchersException`; write `when(map.put(any(), eq("x")))`). And as the last line shows, a JDK proxy can only stand in for an interface; Mockito's own class mocking relies on bytecode generation instead.

## Snippet 4: AssertJ fluent assertions

`assertThat(actual)` returns a type-specific assertion object (`ListAssert`, `StringAssert`, `ObjectAssert`, ...) whose methods each check one property, return `this` so checks chain, and build the failure message from the actual and expected values. The check happens in the chained call, not in `assertThat` itself. `SoftAssertions` swaps "throw on first failure" for "collect and throw all at the end".

```java
// Requires org.assertj:assertj-core; not compiled in this repo
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.within;

import java.util.List;
import org.assertj.core.api.SoftAssertions;
import org.junit.jupiter.api.Test;

class AssertionsTest {

    record Person(String name, int age) {}

    @Test
    void fluentChains() {
        List<String> names = List.of("ada", "bob", "cy");

        assertThat(names)
                .hasSize(3)
                .contains("ada")
                .doesNotContain("eve")
                .startsWith("ada")
                .containsExactly("ada", "bob", "cy");

        List<Person> people = List.of(new Person("ada", 36), new Person("bob", 41));
        assertThat(people).extracting(Person::name).containsExactly("ada", "bob");
        assertThat(people.get(0)).usingRecursiveComparison().isEqualTo(new Person("ada", 36));

        assertThat(0.1 + 0.2).isCloseTo(0.3, within(1e-9));
    }

    @Test
    void exceptions() {
        assertThatThrownBy(() -> Integer.parseInt("x"))
                .isInstanceOf(NumberFormatException.class)
                .hasMessageContaining("x");
    }

    @Test
    void softAssertions() {
        SoftAssertions.assertSoftly(softly -> {
            softly.assertThat("ada".length()).isEqualTo(3);
            softly.assertThat("bob".toUpperCase()).isEqualTo("BOB");
        });
    }
}
```

JDK-only fluent assertion class with a hard mode (throws immediately) and a soft mode (collects every failure):

```java
import java.util.ArrayList;
import java.util.List;

public class FluentAssertDemo {

    static final class ListCheck<T> {
        private final List<T> actual;
        private final List<String> failures;
        private final boolean soft;

        private ListCheck(List<T> actual, List<String> failures, boolean soft) {
            this.actual = actual;
            this.failures = failures;
            this.soft = soft;
        }

        static <T> ListCheck<T> assertThat(List<T> actual) {
            return new ListCheck<>(actual, new ArrayList<>(), false);
        }

        static <T> ListCheck<T> softly(List<T> actual, List<String> sink) {
            return new ListCheck<>(actual, sink, true);
        }

        private ListCheck<T> fail(String message) {
            if (!soft) {
                throw new AssertionError(message);
            }
            failures.add(message);
            return this;
        }

        ListCheck<T> hasSize(int expected) {
            return actual.size() == expected ? this
                    : fail("Expecting size <" + expected + "> but was <" + actual.size() + "> in " + actual);
        }

        ListCheck<T> contains(T element) {
            return actual.contains(element) ? this : fail("Expecting " + actual + " to contain <" + element + ">");
        }

        ListCheck<T> doesNotContain(T element) {
            return !actual.contains(element) ? this : fail("Expecting " + actual + " not to contain <" + element + ">");
        }

        ListCheck<T> containsExactly(List<T> expected) {
            return actual.equals(expected) ? this : fail("Expecting " + actual + " to be exactly " + expected);
        }
    }

    public static void main(String[] args) {
        List<String> names = List.of("ada", "bob");

        ListCheck.assertThat(names).hasSize(2).contains("ada").doesNotContain("eve").containsExactly(List.of("ada", "bob"));
        System.out.println("passing chain: ok");

        try {
            ListCheck.assertThat(names).contains("ada").hasSize(3).contains("zed");
        } catch (AssertionError e) {
            System.out.println("hard mode stops at the first failure: " + e.getMessage());
        }

        List<String> collected = new ArrayList<>();
        ListCheck.softly(names, collected).contains("ada").hasSize(3).contains("zed").doesNotContain("bob");
        System.out.println("soft mode collected " + collected.size() + " failures:");
        collected.forEach(f -> System.out.println("  - " + f));
    }
}
```

Observed output (`java FluentAssertDemo`):

```text
passing chain: ok
hard mode stops at the first failure: Expecting size <3> but was <2> in [ada, bob]
soft mode collected 3 failures:
  - Expecting size <3> but was <2> in [ada, bob]
  - Expecting [ada, bob] to contain <zed>
  - Expecting [ada, bob] not to contain <bob>
```

**Pitfall:** because the check lives in the chained call, an `assertThat(x)` with nothing after it, or an `assertThatThrownBy(...)` without `isInstanceOf`/`hasMessage...`, asserts nothing and passes. In the class above, `ListCheck.assertThat(names)` with no method call would likewise never fail. Floating-point is the other classic: `assertThat(0.1 + 0.2).isEqualTo(0.3)` fails because the sum is not exactly 0.3, which is why the example uses `isCloseTo(0.3, within(1e-9))`.

## Snippet 5: Testcontainers

Testcontainers starts a real Docker container for the test (a database, a broker), maps each exposed container port to a random free host port, and blocks until a wait strategy says the service is ready, so the test never needs a fixed port or a sleep. Container lifecycle follows the JUnit extension: a `static @Container` field starts once per class, an instance field starts once per test method. It needs a reachable Docker daemon.

```java
// Requires org.testcontainers:junit-jupiter, org.testcontainers:postgresql and a running Docker daemon; not compiled in this repo
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.sql.Connection;
import java.sql.DriverManager;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

@Testcontainers
class DatabaseIT {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Container
    static GenericContainer<?> redis = new GenericContainer<>("redis:7-alpine")
            .withExposedPorts(6379)
            .waitingFor(Wait.forListeningPort());

    @Test
    void connectsOnTheMappedPort() throws Exception {
        try (Connection c = DriverManager.getConnection(
                postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword())) {
            assertTrue(c.isValid(2));
        }
        int hostPort = redis.getMappedPort(6379); // random host port, never hardcode 6379
        assertTrue(hostPort > 0);
    }
}
```

For Spring Boot, the JDBC URL is injected with `@DynamicPropertySource` (from `spring-test`), because the port is only known after the container starts:

```java
// Requires org.springframework:spring-test and org.testcontainers:postgresql; not compiled in this repo
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;

class DatabaseProperties {

    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    static {
        postgres.start();
    }

    @DynamicPropertySource
    static void register(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
}
```

JDK-only version of the two ideas Testcontainers automates: a dynamically allocated port, and a readiness probe instead of a sleep. A "service" is started 300 ms after the test begins; connecting immediately fails, polling succeeds.

```java
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ConnectException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.ServerSocket;
import java.net.Socket;

public class ReadinessProbeDemo {

    static boolean probe(int port) {
        try (Socket s = new Socket()) {
            s.connect(new InetSocketAddress(InetAddress.getLoopbackAddress(), port), 100);
            return true;
        } catch (IOException e) {
            return false;
        }
    }

    public static void main(String[] args) throws Exception {
        int port;
        try (ServerSocket reserve = new ServerSocket(0)) { // ask the OS for any free port
            port = reserve.getLocalPort();
        }
        System.out.println("dynamic port allocated: " + (port > 0));

        Thread service = new Thread(() -> {
            try {
                Thread.sleep(300); // the "container" needs time to boot
                try (ServerSocket server = new ServerSocket(port, 50, InetAddress.getLoopbackAddress())) {
                    while (true) {
                        try (Socket client = server.accept()) {
                            BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
                            String line = in.readLine(); // null for a bare readiness probe
                            if ("ping".equals(line)) {
                                new PrintWriter(client.getOutputStream(), true).println("pong");
                                return;
                            }
                        }
                    }
                }
            } catch (Exception e) {
                System.out.println("service failed: " + e);
            }
        });
        service.start();

        try (Socket s = new Socket(InetAddress.getLoopbackAddress(), port)) {
            System.out.println("connected immediately");
        } catch (ConnectException e) {
            System.out.println("no wait: ConnectException (service not up yet)");
        }

        int refused = 0;
        long deadline = System.nanoTime() + 5_000_000_000L;
        while (!probe(port)) {
            refused++;
            if (System.nanoTime() > deadline) {
                throw new IllegalStateException("service never became ready");
            }
            Thread.sleep(50);
        }
        System.out.println("probes refused before ready: " + (refused > 0));

        try (Socket s = new Socket(InetAddress.getLoopbackAddress(), port)) {
            new PrintWriter(s.getOutputStream(), true).println("ping");
            System.out.println("reply = " + new BufferedReader(new InputStreamReader(s.getInputStream())).readLine());
        }
        service.join();
    }
}
```

Observed output (`java ReadinessProbeDemo`):

```text
dynamic port allocated: true
no wait: ConnectException (service not up yet)
probes refused before ready: true
reply = pong
```

**Pitfall:** the first failure the demo prints is the exact flake Testcontainers' wait strategies exist to remove: the process is "started" long before it accepts connections, so a test that connects straight away fails intermittently, depending on machine speed. The same mistake appears when `Wait` is left at the default for an image whose ready log line appears late, or when a non-static `@Container` field restarts the database for every test method and makes a suite of 200 tests take minutes. CI hosts without a Docker socket (many managed runners) fail every such test at startup, so integration tests are usually kept in a separate Maven/Gradle phase.

## Snippet 6: mutation testing

A mutation tool such as PIT makes small, deliberate edits to compiled code (flip `>=` to `>`, negate a condition, replace a return value with a constant), re-runs the tests against each mutant, and reports a mutant as killed if some test fails and as survived if all tests still pass. A surviving mutant means the tests do not pin that behaviour down, regardless of line coverage.

```xml
<!-- Requires org.pitest:pitest-maven and org.pitest:pitest-junit5-plugin; not compiled in this repo. Run: mvn org.pitest:pitest-maven:mutationCoverage -->
<plugin>
  <groupId>org.pitest</groupId>
  <artifactId>pitest-maven</artifactId>
  <version>${pitest.version}</version>
  <dependencies>
    <dependency>
      <groupId>org.pitest</groupId>
      <artifactId>pitest-junit5-plugin</artifactId>
      <version>${pitest.junit5.plugin.version}</version>
    </dependency>
  </dependencies>
  <configuration>
    <targetClasses>
      <param>com.example.billing.*</param>
    </targetClasses>
    <targetTests>
      <param>com.example.billing.*Test</param>
    </targetTests>
    <mutators>
      <mutator>CONDITIONALS_BOUNDARY</mutator>
      <mutator>NEGATE_CONDITIONALS</mutator>
      <mutator>RETURN_VALS</mutator>
    </mutators>
    <mutationThreshold>80</mutationThreshold>
  </configuration>
</plugin>
```

JDK-only demonstration with hand-written mutants of `age >= 18`, run against three test suites:

```java
import java.util.ArrayList;
import java.util.List;
import java.util.function.IntPredicate;

public class MutantDemo {

    record Mutant(String name, IntPredicate impl) {}

    record TestCase(int input, boolean expected) {}

    static boolean isAdult(int age) {
        return age >= 18; // the code under test
    }

    static boolean killed(Mutant mutant, List<TestCase> suite, boolean assertResults) {
        for (TestCase t : suite) {
            boolean actual = mutant.impl().test(t.input());
            if (assertResults && actual != t.expected()) {
                return true; // some test failed: mutant killed
            }
        }
        return false; // every test still passed: mutant survived
    }

    static void report(String suiteName, List<TestCase> suite, boolean assertResults, List<Mutant> mutants) {
        System.out.println(suiteName);
        int kills = 0;
        for (Mutant m : mutants) {
            boolean k = killed(m, suite, assertResults);
            if (k) {
                kills++;
            }
            System.out.println("  " + (k ? "KILLED   " : "SURVIVED ") + m.name());
        }
        System.out.println("  mutation score " + kills + "/" + mutants.size());
    }

    public static void main(String[] args) {
        List<Mutant> mutants = new ArrayList<>();
        mutants.add(new Mutant("age >= 18  ->  age > 18   (boundary)", a -> a > 18));
        mutants.add(new Mutant("age >= 18  ->  age < 18   (negated)", a -> a < 18));
        mutants.add(new Mutant("return age >= 18  ->  return true", a -> true));
        mutants.add(new Mutant("return age >= 18  ->  return false", a -> false));

        // sanity check: the real code passes every suite
        List<TestCase> weak = List.of(new TestCase(5, false), new TestCase(30, true));
        List<TestCase> strong = List.of(new TestCase(5, false), new TestCase(30, true),
                new TestCase(17, false), new TestCase(18, true));
        for (TestCase t : strong) {
            if (isAdult(t.input()) != t.expected()) {
                throw new IllegalStateException("original code fails " + t);
            }
        }

        report("suite A: ages 5 and 30", weak, true, mutants);
        report("suite B: adds the boundary ages 17 and 18", strong, true, mutants);
        report("suite C: calls isAdult for 5, 30, 17, 18 but asserts nothing", strong, false, mutants);
    }
}
```

Observed output (`java MutantDemo`):

```text
suite A: ages 5 and 30
  SURVIVED age >= 18  ->  age > 18   (boundary)
  KILLED   age >= 18  ->  age < 18   (negated)
  KILLED   return age >= 18  ->  return true
  KILLED   return age >= 18  ->  return false
  mutation score 3/4
suite B: adds the boundary ages 17 and 18
  KILLED   age >= 18  ->  age > 18   (boundary)
  KILLED   age >= 18  ->  age < 18   (negated)
  KILLED   return age >= 18  ->  return true
  KILLED   return age >= 18  ->  return false
  mutation score 4/4
suite C: calls isAdult for 5, 30, 17, 18 but asserts nothing
  SURVIVED age >= 18  ->  age > 18   (boundary)
  SURVIVED age >= 18  ->  age < 18   (negated)
  SURVIVED return age >= 18  ->  return true
  SURVIVED return age >= 18  ->  return false
  mutation score 0/4
```

**Pitfall:** suite C executes every line of `isAdult`, so a line-coverage report says 100%, yet it kills 0 of 4 mutants because nothing is asserted; suite A has the same coverage and still lets the boundary mutant live, which is the classic off-by-one bug (`>=` vs `>`) that only the test for age 18 can catch. The other real limit is equivalent mutants: some mutations (for example changing `<` to `<=` in a comparison whose two operands can never be equal) do not change observable behaviour, so no test can kill them and a score of 100% is usually unreachable; set a threshold such as `mutationThreshold` rather than demanding all kills.

## Verification notes

- Compiled and run (6 total): `MiniRunnerDemo`, `TableDrivenDemo`, `RecordingProxyDemo`, `FluentAssertDemo`, `ReadinessProbeDemo`, `MutantDemo`, each with `javac --release 21 -proc:none` and `java`.
- Not compiled (need external artifacts): `LifecycleTest`, `LeapYearTest`, `OrderServiceTest`, `AssertionsTest`, `DatabaseIT`, `DatabaseProperties`, and the PIT Maven plugin block.
- The timing line printed by `TimingExtension` in the JUnit example is machine dependent and therefore not shown; nothing printed by the JDK-only demos depends on timing.
