# Interview: GraalVM Native

Q: What are the main benefits of native images? A: Instant startup, lower memory, smaller size.

Q: What are the limitations? A: Longer build time, no dynamic class loading, must declare reflection, slightly lower peak throughput.

Q: When to use native images? A: Serverless functions, microservices in containers, CLI tools, where fast startup matters.

Q: How does Spring Boot AOT help? A: Automated generation of native-image config (reflection, resources, serialization) for Spring beans.
