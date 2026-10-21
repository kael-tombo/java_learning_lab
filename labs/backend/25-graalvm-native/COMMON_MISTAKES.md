# Common Mistakes: GraalVM Native

1. Missing reflection configuration (Runtime reflection errors)
2. Dynamic class loading (Class.forName)
3. Missing resource registration (file not found)
4. Missing serialization registration (SerializationException)
5. Unsupported proxies (Javassist, CGLIB)
6. Missing META-INF services (ServiceLoader)
7. Lambda serialization without config
8. Not testing native image in CI
