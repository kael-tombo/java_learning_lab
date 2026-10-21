# Refactoring: GraalVM Native

Before: Dynamic class loading with Class.forName
After: Explicit switch/Map-based factory

Before: Runtime proxy creation (CGLIB)
After: Interface-based proxies with config

Before: Dynamic resource loading
After: Resource declared in resource-config.json
