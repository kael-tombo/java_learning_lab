# Interview: API Versioning & Documentation

Q1: What API versioning strategy would you recommend? A: URL-based for external APIs (explicit), header-based for internal APIs (clean URLs). Use content negotiation for RESTful purity.

Q2: How do you handle breaking changes? A: Create new version, maintain old version with deprecation notice, provide migration guide, set sunset date.

Q3: What is the difference between SpringFox and SpringDoc? A: SpringDoc works with Spring Boot 3.x, uses OpenAPI 3.0 natively, has better Spring Boot integration, and is actively maintained.

Q4: How do you document different API versions? A: Use GroupedOpenApi to create separate OpenAPI groups per version, each with its own path matcher and metadata.
