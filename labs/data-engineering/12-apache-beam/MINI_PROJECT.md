# Apache Beam — MINI PROJECT

## Project: One Pipeline, Three Runners

A clickstream enrichment pipeline written in the Beam Java SDK that runs
unchanged on the Direct, Flink, and Spark runners.

### Scope
- `DoFn`s: parse, normalize, enrich with a side input, sessionize with windows.
- Custom `Coder` for a domain type.
- State and timers for a per-session timeout.
- Runner flags: `--runner=DirectRunner|FlinkRunner|SparkRunner`.
- Verification: identical output checksums across runners.

### Architecture

```
TextIO.read() -> PCollection<Click>
   |
ParseClick (DoFn, custom Coder)
   |
+--> FlatMap -> ExtractItems -> CombinePerKey(sum) -> daily revenue
|
+--> Map -> KV(userId, Click) -> WindowInto(FixedWindows 30m + SessionWindows gap 30m)
                |                          |
                +--> state/timer sessionizer --> sessions PCollection
                                                          |
                                                   side input (dim) -> enrich
                                                          |
                                            ToList -> TopUsers -> TextIO.write
```

### Implementation

```java
public class ParseClick extends DoFn<String, Click> {
    private static final Coder<Click> CLICK_CODER = Coder.of(Click.class);
    private final ObjectMapper json = new ObjectMapper();

    @ProcessElement
    public void processElement(@Element String line,
                               OutputReceiver<Click> out,
                               @Timestamp Instant ts,
                               BoundedWindow window) {
        try {
            Click c = json.readValue(line, Click.class);
            // Honour the event timestamp, not the arrival time: Beam's model
            // attaches it here and windows downstream honour it automatically.
            out.withTimestamp(c.eventTs()).withOutputTag("main", c).process(c);
        } catch (JsonProcessingException e) {
            out.withOutputTag("bad", Ints.tryParse(line) == null
                    ? line : null).process(null);   // never drop silently
        }
    }
}
```

```java
public class SessionizeWithState extends DoFn<KV<String, Click>, Session> {
    @StateId("openSession") private transient StateSpec<BagState<Click>> bag;
    @TimerId("closeSession") private transient TimerSpec timer;
    @ElementId("count") private transient CountState observed;

    @ProcessElement
    public void processElement(@Element KV<String, Click> kv,
                               @Timestamp Instant ts,
                               @TimerId("closeSession") Timer timer,
                               OutputReceiver<Session> out) {
        Click c = kv.getValue();
        if (bag.read().isEmpty()) {
            bag.add(c);
            timer.set(ts.plus(Duration.ofMinutes(30)));   // session gap
        } else {
            Click prev = Iterables.getLast(bag.read());
            if (Duration.between(prev.eventTs(), c.eventTs()).toMinutes() > 30) {
                emitSession(out);
                bag.clear();
                bag.add(c);
                timer.set(ts.plus(Duration.ofMinutes(30)));
            } else {
                bag.add(c);
            }
        }
        observed.inc();
    }

    @OnTimer("closeSession")
    public void onTimer(@Timestamp Instant ts, OutputReceiver<Session> out) {
        if (observed.read() > 0) emitSession(out);         // no empty sessions
        bag.clear();
    }

    private void emitSession(OutputReceiver<Session> out) {
        BagState<Click> b = bag.read();
        if (b.isEmpty()) return;
        List<Click> clicks = Lists.newArrayList(b.read());
        Instant start = clicks.get(0).eventTs();
        Instant end = Iterables.getLast(clicks).eventTs();
        double revenue = clicks.stream().filter(c -> "purchase".equals(c.type()))
                                     .mapToDouble(Click::amount).sum();
        out.output(new Session(kv.getKey(), start, end, clicks.size(), revenue));
    }
}
```

### Side input for a dimension

```java
PCollectionView<Map<String, String>> dim =
        pipeline.apply("readDim", TextIO.read().from("dims/*.tsv"))
                .apply("toKv", MapElements.into(
                        TypeDescriptors.tuple(String.class, String.class))
                        .via((MapElements.Via<String, String, KV<String, String>>) (line, out) -> {
                            String[] p = line.split("\t");
                            out.output(KV.of(p[0], p[1]));   // country code -> name
                        })));

PCollection<Enriched> enriched = clicks.apply(
        MapElements.into(Enriched.coder())
            .via(Enrichment.withCountry(dim)));            // side input: broadcast, no shuffle
```

### Running on three runners from one code path

```java
public static void main(String[] args) {
    PipelineOptions opts = PipelineOptionsFactory.fromArgs(args).create();
    Pipeline p = Pipeline.create(opts);

    PCollection<Click> clicks = p
            .apply("Read", TextIO.read().from(optionsInput(opts)))
            .apply("Parse", ParDo.of(new ParseClick()))
            .setCoder(Coder.of(Click.class));

    // Branch 1: batch-style aggregate. Identical code, three runners.
    PCollection<KV<String, Double>> daily = clicks
            .apply("Extract", ParDo.of(new ExtractAmount()))
            .apply("Sum", Sum.doublesByKey())
            .setCoder(KvCoders.of(StringCoder.of(), DoubleCoder.of()));

    // Branch 2: stateful sessionization
    PCollection<Session> sessions = clicks
            .apply("KeyBy", MapElements.into(KvCoders.of(StringCoder.of(), CLICK_CODER))
                    .via((Click c) -> KV.of(c.userId(), c)))
            .apply("Window", Window.into(new Sessions<>(Duration.ofMinutes(30))))
            .apply("Sessionize", ParDo.of(new SessionizeWithState()));

    PipelineResult result = p.run();

    // Verify identical output regardless of runner: a checksum, not a diff of logs.
    result.waitUntilFinish();
    System.out.println("runner=" + opts.getRunner()
            + " sessions=" + result.metrics.counter("sessions").getCommitted());
}
```

```bash
# Same code, three runners
mvn -q package
java -cp target/classes:$(cat cp.txt) com.example.Pipeline --runner=DirectRunner  --input=data/clicks
java -cp target/classes:$(cat cp.txt) com.example.Pipeline --runner=FlinkRunner   --flinkMaster=local[*] --input=data/clicks
java -cp target/classes:$(cat cp.txt) com.example.Pipeline --runner=SparkRunner   --input=data/clicks
```

### Test It

```java
@Rule public final transient TestPipeline pipeline = TestPipeline.create();

@Test void sessionizesOnGap() {
    PCollection<Session> sessions = pipeline
            .apply(Create.of(click("u1", 0), click("u1", 600),
                             click("u1", 3600), click("u1", 3700)))
            .apply(ParDo.of(new SessionizeWithState()))
            .setCoder(Session.coder());
    PAssert.that(sessions).satisfies(elementsAreEquivalentTo(
            anyViewsHaving("sessions", 2)));      // gap at 3600s splits them
}

@Test void samePipelineOnTwoRunners() {
    // run the identical pipeline twice via TestPipeline with different options
    // and assert the collected output sets are equal
}
```

### Stretch
- Add a trigger (early/fire/late) to a window and observe when output is emitted.
- Measure the portability tax: add a `Flink` extension, compare fusion and stage counts.
- Implement a custom `CombineFn` with an accumulator and check memory behaviour.

## Deliverables
- [ ] One pipeline running on Direct, Flink, and Spark with matching output checksums
- [ ] Custom `Coder` for a domain type
- [ ] `DoFn` with `StateSpec`, `TimerSpec`, and an empty-session guard
- [ ] Side input enrichment with no extra shuffle
- [ ] Bad-record side output with a reason, no silent drops
- [ ] Test suite with `PAssert` and a cross-runner equivalence test
- [ ] Written note on when you would drop Beam and use the engine's own API
