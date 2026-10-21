# Company Interview Guide — Java Version Knowledge

> How different companies test Java version knowledge, what they care about, and how to prepare.

---

## Oracle

**Focus areas**: Licensing, JDK distributions, Long-Term Support strategy, Java SE vs OpenJDK.

**Typical questions**:
1. "Explain the difference between Oracle JDK and OpenJDK."
2. "What changed in Java licensing from Java 8 to Java 17?"
3. "When would you choose Oracle JDK over OpenJDK or another distribution?"
4. "What is the NFTC license and what does it cover?"
5. "How does Oracle's 6-month release cadence work with LTS versions?"

**Key talking points**:
- Oracle JDK 8 was free for development but required a commercial license for business use from April 2019.
- Oracle JDK 11 under commercial license; OpenJDK free (GPL+CE).
- Oracle JDK 17+ under NFTC (No-Fee Terms and Conditions) — free for all uses, including production.
- Oracle JDK includes some commercial features (e.g., Java Flight Recorder, Java Mission Control) but these were open-sourced in later versions.
- Support lifecycle: Oracle Premier Support for LTS versions (8, 11, 17, 21, 25) typically 3-8 years depending on agreement.
- Companies migrating from Java 8 often skip 11 and go to 17 or 21.
- For Oracle positions, emphasize understanding of licensing implications, migration planning, and support timelines.

**Preparation**: Read Oracle's Java SE licensing FAQ. Know the differences between Oracle JDK, OpenJDK, and other builds (Corretto, Zulu, Adoptium).

---

## Google

**Focus areas**: Internal Java usage, Guava vs JDK features, Android Java compatibility, large-scale JVM management.

**Typical questions**:
1. "What Java version does Google use internally?"
2. "How do you choose between Guava and JDK standard library features?"
3. "What are the Android-specific Java limitations?"
4. "How would you design a Java service at Google scale?"
5. "How does Google's internal JDK differ from standard OpenJDK?"

**Key talking points**:
- Google has its own JDK distribution (based on OpenJDK) with custom GC and performance patches.
- Google contributed significantly to OpenJDK (G1 GC improvements, etc.).
- Guava predates many JDK features: ImmutableList (pre-List.of), Optional (pre-java.util.Optional), MoreCollectors (pre-Collectors.toList), Joiner/Splitter (pre-String.join/split), Preconditions (pre-Objects.requireNonNull).
- Android uses a subset of Java: API level-dependent. Java 8 features (lambdas, streams, Optional, try-with-resources) are well-supported. Java 9+ features (var, records, sealed classes) depend on API level and desugar support.
- Google's internal build system (Bazel) handles multi-version Java compilation.
- For Google positions, emphasize understanding of library evolution (Guava to JDK), scale considerations, and performance tuning.

**Preparation**: Familiarize with Guava's key classes vs JDK equivalents. Understand Android's Java feature support per API level.

---

## Amazon

**Focus areas**: Amazon Corretto, AWS Lambda Java, cost implications of version upgrades, large-scale distributed Java services.

**Typical questions**:
1. "What is Amazon Corretto and why does Amazon maintain it?"
2. "Why does AWS Lambda support specific Java versions?"
3. "How does Java version affect Lambda cold start times?"
4. "What is Lambda SnapStart and how does it relate to Java versions?"
5. "How would you reduce Java Lambda deployment size and startup time?"
6. "What GC configuration would you use for a low-latency Amazon service?"

**Key talking points**:
- Amazon Corretto is a free, multi-platform, production-ready OpenJDK distribution. Amazon provides long-term support with quarterly security updates.
- Corretto benefits: aarch64 (Graviton) performance tuning, backported security fixes, FIPS support.
- AWS Lambda supports Java 8, 11, 17, 21. Each requires specific runtime support.
- Lambda SnapStart (Java 11+) uses VM snapshots for faster cold starts (reducing from seconds to sub-second).
- jlink (Java 9+) reduces custom runtime size for Lambda deployments.
- Virtual threads (Java 21+) help Lambda functions handle concurrent requests more efficiently.
- For Amazon positions, emphasize Serverless Java patterns, cold start optimization, and Corretto's benefits.

**Preparation**: Build a Java Lambda function, experiment with SnapStart, compare cold start times across versions. Read AWS Java developer blogs.

---

## Microsoft

**Focus areas**: Adoptium (Eclipse Temurin), Azure Java support, VS Code Java toolchain, cross-platform Java.

**Typical questions**:
1. "What is Microsoft's involvement with Adoptium?"
2. "How does Azure support Java in App Service and Functions?"
3. "What are the benefits of VS Code for Java development?"
4. "How do you develop Java on Windows vs Linux?"
5. "What Java version does Azure recommend and why?"

**Key talking points**:
- Microsoft employs several OpenJDK contributors and maintains the Microsoft Build of OpenJDK.
- Adoptium (Eclipse Temurin) is the recommended OpenJDK distribution by Microsoft. GPL+CE licensed, TCK-tested.
- Azure App Service, Azure Functions, Azure Spring Apps, and Azure Kubernetes Service all support Java.
- VS Code Java Extension Pack provides IntelliSense, debugging, refactoring, Maven/Gradle integration, and test runner.
- For Microsoft positions, emphasize cross-platform development experience, containerized Java on Azure, and toolchain fluency.

**Preparation**: Install VS Code Java extension pack, deploy a Java app to Azure App Service, understand Azure Functions Java model.

---

## Netflix

**Focus areas**: Java upgrade at scale, GC tuning per version, chaos engineering with JVM, microservices.

**Typical questions**:
1. "How does Netflix manage Java version upgrades across thousands of services?"
2. "What GC configurations does Netflix use for different workloads?"
3. "How did Netflix benefit from migrating from Java 8 to Java 17?"
4. "What Java features improved Netflix's streaming reliability?"
5. "How does Netflix test pre-release JDK builds?"

**Key talking points**:
- Netflix manages upgrades as a service-team responsibility, not central mandate.
- They use golden AMIs with JDK pre-installed; teams pull latest base image.
- Netflix runs early-access JDK builds to catch issues before GA.
- Uses canary analysis comparing old vs new JVMs in production.
- GC tuning is workload-specific: Zuul (gateway) uses different GC than Cassandra services.
- They contributed to JDK improvements: G1 GC tuning, container support, CDS for faster startup.
- Virtual threads (Java 21) are evaluated for high-throughput request processing.
- For Netflix positions, emphasize experience with large-scale JVM operations, GC tuning, and safe migration strategies.

**Preparation**: Read Netflix Tech Blog articles on Java. Study JVM memory management and GC tuning.

---

## Apple

**Focus areas**: Java on macOS, deprecation history, Apple Silicon (ARM) compatibility, Metal rendering pipeline.

**Typical questions**:
1. "What is Apple's history with Java on macOS?"
2. "How does Java run on Apple Silicon (M1/M2/M3)?"
3. "What Java version do you use for macOS development and why?"
4. "How has Apple's deprecation of Java affected macOS development?"
5. "What rendering pipeline does Java use on macOS and how has it evolved?"

**Key talking points**:
- Apple maintained its own Java 6 JDK for macOS (pre-2010). Deprecated in 2010, handed to Oracle.
- macOS 10.7 (Lion) removed Java runtime pre-installation. macOS 10.10 (Yosemite) removed Java 6 entirely.
- Current recommendation: download JDK from Adoptium, Azul, or Oracle.
- Java 11+ runs natively on Apple Silicon (ARM64). Oracle JDK 17+ has native M1 support.
- Java 17 introduced a new macOS rendering pipeline using Apple's Metal framework (replacing OpenGL).
- macOS is a popular development platform for Java, but server deployment is Linux.
- For Apple positions, emphasize platform-specific issues: windowing, packaging (jpackage for DMG), and performance.

**Preparation**: Test JDK on Apple Silicon, verify jpackage creates valid DMGs, understand macOS-specific AWT/Swing behavior.

---

## Other Companies by Industry

### Banking/Finance (Goldman Sachs, JPMorgan, Morgan Stanley)
- **Focus**: GC tuning, low-latency, stability, long LTS support
- **Key versions**: Java 8 legacy, Java 17/21 current
- **Questions**: "What GC would you use for a trading system?" "How do you minimize GC pauses?" "What Java version do you run in production and why?"
- **Strategy**: Emphasize ZGC/Shenandoah for low-latency, G1 for throughput. Discuss CMS removal impact. Know their preference for LTS versions with extended support contracts.
- **Interview tip**: These companies value stability over new features. Show judgment about when to upgrade and when to stay.

### E-Commerce (Shopify, eBay, Etsy)
- **Focus**: Throughput, GC efficiency, containerized Java, cost optimization
- **Key versions**: Java 11/17/21
- **Questions**: "How do you optimize Java containers for cost?" "What's your Java upgrade strategy for a 500-service architecture?"
- **Strategy**: Discuss container-awareness of modern JDK (cgroup support, memory limits), jlink for image size reduction, G1/ZGC in containers.
- **Interview tip**: Connect Java version features to cost savings and operational efficiency.

### Big Data (Databricks, Snowflake, Confluent)
- **Focus**: Performance, large heap sizes, GC, data pipelines
- **Key versions**: Java 17/21, experimenting with Valhalla (value types)
- **Questions**: "How do you tune GC for 100GB heaps?" "How would virtual threads benefit a data pipeline?"
- **Strategy**: Discuss G1 GC tuning (region size, max G1 pause target), ZGC for large heaps, value types for reduced memory footprint.
- **Interview tip**: Show deep GC knowledge and understanding of how language features affect data processing performance.

---

## General Strategy for Company-Specific Interviews

1. **Research the company's Java stack**: Read their engineering blogs, open-source projects, and job postings.
2. **Match version knowledge to their pain points**: Netflix cares about scale, Oracle cares about licensing, Amazon cares about serverless.
3. **Show pragmatic judgment**: Don't advocate for the newest version just because it's new. Show you consider stability, migration cost, and team readiness.
4. **Acknowledge tradeoffs**: Every version has pros and cons. A mature engineer acknowledges them.
5. **Prepare a "your company" answer**: Have a 2-minute answer about how you'd approach Java version strategy specifically at the company interviewing you.
6. **Know their JDK distribution**: Use Adoptium if interviewing with Microsoft-affiliated companies; Corretto for Amazon; Oracle JDK for Oracle; Zulu for Azul.
7. **Bring up their open source contributions**: Mentioning a company's JDK contributions shows research and genuine interest.
