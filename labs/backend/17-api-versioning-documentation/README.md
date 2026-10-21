# Lab 17: API Versioning & Documentation

## Overview
Learn API versioning strategies and documentation generation with OpenAPI 3.0 and SpringDoc. Master API contract design, version negotiation, and automated documentation.

## Topics Covered
- OpenAPI 3.0 specification
- SpringDoc OpenAPI integration
- URL-based versioning (/v1/, /v2/)
- Header-based versioning (Accept-Version)
- Content negotiation versioning
- API contract-first development
- Spring REST Docs integration

## Prerequisites
- Java 21+
- Spring Boot 3.3+
- REST API knowledge

## Getting Started
`ash
mvn spring-boot:run
# OpenAPI UI: http://localhost:8080/swagger-ui.html
# OpenAPI Spec: http://localhost:8080/v3/api-docs
`

## Key Dependencies
`xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.5.0</version>
</dependency>
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\17-api-versioning-documentation "THEORY.md") @"
# Theory: API Versioning & Documentation

## 1. API Versioning Strategies

### URL-Based Versioning
`
GET /v1/users
GET /v2/users
`
- Explicit and easy to understand
- Clutters URL space
- Requires routing configuration
- Hard to maintain multiple versions

### Header-Based Versioning
`
GET /users
Accept-Version: 1
`
- Clean URLs
- Less visible to developers
- Custom header required
- Caching considerations

### Content Negotiation Versioning
`
GET /users
Accept: application/vnd.company.v1+json
`
- RESTful and standards-based
- Complex to implement
- Client needs to specify media type
- Good for backward compatibility

### Query Parameter Versioning
`
GET /users?version=1
`
- Simple to implement
- URI not unique (caching issues)
- Pollutes query parameters
- Easy to test

## 2. OpenAPI 3.0 Specification

### Core Components
- **OpenAPI Object**: Root document
- **Info Object**: API metadata
- **Paths Object**: Endpoints
- **Components Object**: Reusable schemas
- **Security Schemes**: Authentication methods

### Document Structure
`yaml
openapi: 3.0.3
info:
  title: User API
  version: 2.0.0
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: Successful response
components:
  schemas:
    User:
      type: object
      properties:
        id: integer
        name: string
`

## 3. SpringDoc Annotations

`java
@Operation(summary = "Create user", description = "Creates a new user")
@ApiResponses(value = {
    @ApiResponse(responseCode = "201", description = "User created"),
    @ApiResponse(responseCode = "400", description = "Invalid input")
})
@Schema(description = "User entity")
`

## 4. API Contract-First Development

### Workflow
1. Define OpenAPI specification
2. Generate server stub from spec
3. Implement business logic
4. Generate client libraries
5. Version the contract

### Tools
- OpenAPI Generator
- Swagger Codegen
- Contract testing with Spring Cloud Contract

## 5. Version Lifecycle

### Deprecation Strategy
1. Announce deprecation in documentation (v1)
2. Maintain backward compatibility (v1 + v2)
3. Set sunset date for old version
4. Migrate clients with sufficient notice
5. Remove old version after sunset

### Version Compatibility
- Additive changes are backward compatible
- Breaking changes require new version
- Use semantic versioning for APIs
- Document migration guides
