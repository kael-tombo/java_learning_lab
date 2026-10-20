# Step by Step: API Versioning & Documentation

## Step 1: Add SpringDoc Dependency
`xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>2.5.0</version>
</dependency>
`

## Step 2: Configure OpenAPI Info
`yaml
springdoc:
  api-docs:
    path: /v3/api-docs
  swagger-ui:
    path: /swagger-ui.html
    operations-sorter: method
spring:
  application:
    name: api-versioning-demo
`

`java
@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI()
        .info(new Info()
            .title("User Management API")
            .version("2.0.0")
            .description("API for managing users")
            .contact(new Contact().name("Dev Team").email("dev@example.com")))
        .addSecurityItem(new SecurityRequirement().addList("bearer"))
        .components(new Components()
            .addSecuritySchemes("bearer", new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("bearer")
                .bearerFormat("JWT")));
}
`

## Step 3: Create Versioned Controllers
See Java source files for full implementation.

## Step 4: Configure OpenAPI Groups
`java
@Bean
public GroupedOpenApi v1Api() {
    return GroupedOpenApi.builder()
        .group("v1")
        .displayName("V1 API")
        .pathsToMatch("/v1/**")
        .addOpenApiCustomizer(openApi -> openApi
            .info(new Info().title("V1 API").version("1.0.0")))
        .build();
}

@Bean
public GroupedOpenApi v2Api() {
    return GroupedOpenApi.builder()
        .group("v2")
        .displayName("V2 API")
        .pathsToMatch("/v2/**")
        .addOpenApiCustomizer(openApi -> openApi
            .info(new Info().title("V2 API").version("2.0.0")))
        .build();
}
`

## Step 5: Test the Documentation
`ash
# Access Swagger UI
open http://localhost:8080/swagger-ui.html

# Get raw OpenAPI spec
curl http://localhost:8080/v3/api-docs
curl http://localhost:8080/v3/api-docs/v1
curl http://localhost:8080/v3/api-docs/v2
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\17-api-versioning-documentation "VISUAL_GUIDE.md") @"
# Visual Guide: API Versioning & Documentation

## Versioning Strategy Comparison

`
Strategy        | URL          | Header       | Content-Neg  | Query-Param
----------------|--------------|--------------|--------------|------------
Visibility      | High         | Low          | Low          | Medium
Cache-Friendly  | Yes          | Depends      | Yes          | No
RESTful         | Debatable    | Yes          | Yes          | No
Implementation  | Easy         | Medium       | Complex      | Easy
Browser Test    | Easy         | Needs Plugin | Needs Plugin | Easy
`

## OpenAPI Document Structure

`
openapi: 3.0.3
â”œâ”€â”€ info
â”‚   â”œâ”€â”€ title
â”‚   â”œâ”€â”€ version
â”‚   â””â”€â”€ description
â”œâ”€â”€ servers
â”‚   â””â”€â”€ url
â”œâ”€â”€ paths
â”‚   â”œâ”€â”€ /v1/users
â”‚   â”‚   â”œâ”€â”€ get (Operation)
â”‚   â”‚   â”‚   â”œâ”€â”€ parameters
â”‚   â”‚   â”‚   â”œâ”€â”€ responses
â”‚   â”‚   â”‚   â””â”€â”€ security
â”‚   â”‚   â””â”€â”€ post (Operation)
â”‚   â”‚       â”œâ”€â”€ requestBody
â”‚   â”‚       â””â”€â”€ responses
â”‚   â””â”€â”€ /v1/users/{id}
â”‚       â””â”€â”€ get
â”œâ”€â”€ components
â”‚   â”œâ”€â”€ schemas
â”‚   â”‚   â”œâ”€â”€ User
â”‚   â”‚   â””â”€â”€ Error
â”‚   â””â”€â”€ securitySchemes
â”‚       â””â”€â”€ bearerAuth
â””â”€â”€ tags
    â””â”€â”€ name, description
`

## API Version Lifecycle

`
v1.0.0 â”€â”€→ v1.1.0 â”€â”€→ v1.2.0 â”€â”€→ v2.0.0 â”€â”€→ v2.1.0
  →‘          →‘          →‘          →‘          →‘
Release   Additive   Additive   Breaking   Additive
                     Deprecate  v1.x       Deprecate
                     v1.0.0               v2.0.0

Timeline:
v1.0.0: 2024-Q1
v1.1.0: 2024-Q2 (add new endpoint)
v1.2.0: 2024-Q3 (deprecate v1.0.0 endpoint)
v2.0.0: 2024-Q4 (breaking changes, v1.x deprecated)
v2.1.0: 2025-Q1 (new features, v1.x sunset)
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\17-api-versioning-documentation "INTERNALS.md") @"
# Internals: API Versioning & Documentation

## SpringDoc Internal Architecture

### OpenAPIBuilder
The core builder traverses:
1. All @RequestMapping methods
2. Builds Operation objects from method metadata
3. Infers schemas from Java types
4. Merges with @Operation annotations
5. Assembles into OpenAPI object

### Schema Resolution
TypeResolver resolves Java types to OpenAPI schemas:
1. Check @Schema annotation
2. Check Jackson annotations
3. Introspect class fields/getters
4. Resolve generic type parameters
5. Handle inheritance and polymorphism

## OpenAPI Generator Internals

### Code Generation Pipeline
1. Parse OpenAPI YAML/JSON
2. Build in-memory model (CodegenModel, CodegenOperation)
3. Apply mustache templates
4. Generate source files
5. Write to output directory

## HandlerInterceptor Version Routing

### PreHandle Flow
1. Request arrives
2. Interceptor extracts version from header/URL/param
3. Sets version as request attribute
4. Controller method checks attribute
5. Routes to appropriate service implementation
