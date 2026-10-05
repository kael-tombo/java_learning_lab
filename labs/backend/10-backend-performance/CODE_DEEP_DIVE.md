# Code Deep Dive

Relevant primitives for Backend Performance:
Micrometer, async-profiler, JFR, virtual threads, connection pools

## Walkthrough
```java
@RestController
public class ExampleController {
    private final AppService service;
    public ExampleController(AppService service) { this.service = service; }

    @GetMapping("/demo")
    public ResponseEntity<Demo> demo() {
        return ResponseEntity.ok(service.run());
    }
}
```

## Service layer
```java
@Service
public class AppService {
    public Demo run() {
        // core logic for Backend Performance
        return new Demo("ok");
    }
}
```

## Tests
```java
@WebMvcTest(ExampleController.class)
class ExampleControllerTest {
    @Autowired MockMvc mvc;
    @Test void demo() throws Exception {
        mvc.perform(get("/demo")).andExpect(status().isOk());
    }
}
```

## Notes
- Bean scope is singleton by default; inject collaborators via constructor.
- Map domain errors to HTTP status at the boundary.
- Add Micrometer timers around the critical section.
