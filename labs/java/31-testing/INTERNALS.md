# Testing — Internal Mechanics

## JUnit 5 Architecture

JUnit 5 is composed of three modules:
- **junit-platform-engine**: Core API for test discovery and execution
- **junit-jupiter-engine**: Implementation of the Jupiter programming model
- **junit-vintage-engine**: Adapter for JUnit 3/4 tests

### Test Discovery (Launcher API)

`java
LauncherDiscoveryRequest request = LauncherDiscoveryRequestBuilder.request()
    .selectors(selectPackage("com.example"))
    .filters(includeTags("fast"))
    .build();

Launcher launcher = LauncherFactory.create();
SummaryGeneratingListener listener = new SummaryGeneratingListener();
launcher.execute(request, listener);
TestPlan plan = listener.getSummary();
`

The Launcher discovers TestEngine implementations via ServiceLoader. Each engine scans classpath for its annotated tests.

### Jupiter Extension Model

Extensions replace JUnit 4's test runners. Common extension points:

| Extension Point | Interface | Example |
|----------------|-----------|---------|
| Test instantiation | TestInstanceFactory | DI frameworks |
| Parameter resolution | ParameterResolver | MockitoExtension |
| Lifecycle callbacks | BeforeEachCallback | SpringExtension |
| Exception handling | TestExecutionExceptionHandler | Database clean-up |
| Condition evaluation | ExecutionCondition | @EnabledOnOs |

MockitoExtension implements ParameterResolver and BeforeEachCallback to create and inject mocks.

### Test Execution Engine

`java
// Simplified engine execution
for (TestDescriptor test : engine.discoverTests(request)) {
    EngineExecutionListener listener = new EngineExecutionListener();
    engine.execute(new ExecutionRequest(test, listener, config));
}
`

Each TestDescriptor is a tree node: container (class) or leaf (method). Execution traverses:
1. BeforeAll callbacks
2. For each leaf: BeforeEach callbacks, test invoker, AfterEach callbacks
3. AfterAll callbacks

## Mockito Internals

### Bytecode Generation

Mockito mocks are created via bytecode generation (ByteBuddy or CGLIB):
1. Read the original class bytecode
2. Generate a subclass overriding all non-final methods
3. Each override checks a MethodInterceptor that consults the stub registry
4. If a stub exists, return it; otherwise return the default value

### Stub Registry

`java
// Simplified stub storage
class MockHandler {
    Map<Invocation, Answer<?>> stubs = new LinkedHashMap<>();
    
    Object handle(Invocation invocation) {
        Answer<?> answer = findStub(invocation);
        if (answer != null) return answer.answer(invocation);
        return defaultReturnValue(invocation.getMethod().getReturnType());
    }
}
`

### Verification

Mockito records every invocation in a linked list. When erify(mock).method() is called:
1. Query the invocation log for matching invocations
2. If count >= minimum (default 1), pass
3. Otherwise, throw TooLittleActualInvocations

The matcher stack (nyInt(), eq("foo")) is tracked per-thread using ThreadLocal.
