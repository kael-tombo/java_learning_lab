# How It Works: GraalVM Native

GraalVM native-image tool analyzes your application at build time to determine all code that is reachable from the main method. It compiles this code directly to machine code using the GraalVM compiler. The result is a standalone executable that includes a minimal VM (SubstrateVM) with just enough runtime to execute the compiled code. Reflection, resources, and serialization must be declared via configuration files because the static analysis can't determine them automatically. Spring Boot's AOT engine generates these configurations automatically.
