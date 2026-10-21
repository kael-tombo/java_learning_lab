# Build Tools — Internal Mechanics

## How Maven Works

### Maven Lifecycle Internals

Maven's build lifecycle consists of phases that bind to plugin goals:
1. `validate` — Validates project structure
2. `compile` — Binds to `maven-compiler-plugin:compile`
3. `test` — Binds to `maven-surefire-plugin:test`
4. `package` — Binds to `maven-jar-plugin:jar`
5. `verify` — Binds to integration test plugins
6. `install` — Copies artifact to local repository
7. `deploy` — Copies artifact to remote repository

### Dependency Resolution

Maven resolves dependencies through:
1. **Direct dependencies** — Declared in POM
2. **Transitive dependencies** — Dependency of direct dependencies
3. **Conflict resolution** — Nearest definition wins (shortest path)
4. **Exclusions** — Manual removal of transitive dependencies

### POM Inheritance

Maven POMs form an inheritance hierarchy:
1. **Super POM** — Default values from Maven installation
2. **Parent POM** — User-defined parent with shared configuration
3. **Effective POM** — Merged result of inheritance chain

## How Gradle Works

### Task Graph

Gradle constructs a Directed Acyclic Graph (DAG) of tasks:
1. **Configuration phase** — Evaluates build scripts, creates tasks
2. **Execution phase** — Runs tasks in dependency order
3. **Build cache** — Caches task outputs for incremental builds
