# Interview Questions: Build Tools

## Company-Specific Focus

### Google
- Maven vs Gradle: phases vs tasks, XML vs Groovy/Kotlin DSL
- Dependency management: transitive dependencies, conflict resolution, exclusions
- Multi-module builds: managing large-scale Java projects

### Microsoft
- Maven build tool vs MSBuild in .NET ecosystem
- Integration with Azure DevOps: Maven deploy, CI/CD pipelines
- Gradle incremental builds for faster local development

### Amazon
- Gradle vs Maven in the AWS SDK codebase
- Custom Gradle plugins for internal tooling
- Build optimization: parallel execution, daemon, cache

### Meta
- Build caching: how to speed up 100k+ module builds
- Dependency convergence: preventing classpath conflicts
- Lombok, annotation processors, and build configuration

### Apple
- Maven for Java modules on macOS
- Build portability: cross platform builds
- Gradle vs Xcode build: different world

### Oracle
- Maven Standard Directory Layout
- The build phase lifecycle: compile, test, package, deploy
- Build tools and the Java module system: modular JARs

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems - but build tool patterns apply to project design) |

## Real Production Scenarios
- **Netflix**: A transitive dependency conflict caused a NoSuchMethodError at runtime — resolved with dependency constraint in Gradle
- **Uber**: A multi-module build took 30 minutes — migrated from Maven to Gradle, reduced to 8 minutes
- **Twitter**: Build artifacts from CI had inconsistent versions across modules — fixed by BOM (Bill of Materials) management

## Interview Patterns & Tips
- **Maven**: POM.XML, dependency management, transitive dependency resolution
- **Gradle**: Groovy/Kotlin DSL, incremental build, build cache
- **Plugin**: maven-compiler-plugin, maven-surefire-plugin
- **Version management**: BOM for consistent transitive dependencies

## Deep Dive Questions
- **JVM**: How does Maven/Gradle execute tests? Forked JVM per test suite
- **Memory**: How much memory does the build daemon consume when building large projects?
- **Performance**: What are the benefits of Gradle's build cache for CI performance?
- **Module system**: How to build modular JARs with module-info.java
- **Java 21+**: Toolchain support for multiple JDK versions within one build