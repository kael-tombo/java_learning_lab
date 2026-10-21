# Code Deep Dive: API Versioning & Documentation

## SpringDoc Auto-Configuration

SpringDoc automatically configures:
1. OpenApiResource (REST endpoint for /v3/api-docs)
2. SwaggerUiWebMvcConfigurer (Swagger UI resources)
3. OperationBuilder (builds Operation objects from handlers)
4. RequestBodyBuilder (builds request body schemas)
5. ResponseBuilder (builds response schemas)

### OpenApiResource Implementation
`java
@RestController
public class OpenApiResource {
    @GetMapping(path = "/v3/api-docs", produces = "application/json")
    public String openapiJson(HttpServletRequest request) {
        // Build OpenAPI specification from Spring annotations
        OpenAPI openAPI = openAPIBuilder.build(request);
        return Json.pretty(openAPI);
    }
}
`

### Operation Building Process
For each @RequestMapping method:
1. Extract HTTP method and path
2. Read @Operation annotation for summary/description
3. Read @ApiResponse annotations for response codes
4. Infer parameter schemas from method parameters
5. Infer response schemas from return type
6. Build OpenAPI Operation object

## Custom Versioning Implementation

### URL Versioning via WebMvcConfigurer
`java
@Configuration
public class VersioningConfig implements WebMvcConfigurer {
    @Override
    public void addPathMatchConfigurer(PathMatchConfigurer configurer) {
        configurer.addPathPrefix("/v1", handler -> 
            handler instanceof V1ApiController);
        configurer.addPathPrefix("/v2", handler -> 
            handler instanceof V2ApiController);
    }
}
`

### Header Versioning with HandlerInterceptor
`java
public class ApiVersionInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request, 
                            HttpServletResponse response, 
                            Object handler) {
        String version = request.getHeader("Accept-Version");
        // Route to appropriate controller based on version
        request.setAttribute("apiVersion", version);
        return true;
    }
}
`

## OpenAPI Grouping for Multiple Versions

`java
@Configuration
public class OpenAPIConfig {
    @Bean
    public GroupedOpenApi v1Api() {
        return GroupedOpenApi.builder()
            .group("v1")
            .pathsToMatch("/v1/**")
            .build();
    }
    
    @Bean
    public GroupedOpenApi v2Api() {
        return GroupedOpenApi.builder()
            .group("v2")
            .pathsToMatch("/v2/**")
            .build();
    }
}
`

## Contract-First Code Generation

### OpenAPI Generator Maven Plugin
`xml
<plugin>
    <groupId>org.openapitools</groupId>
    <artifactId>openapi-generator-maven-plugin</artifactId>
    <version>7.4.0</version>
    <executions>
        <execution>
            <goals><goal>generate</goal></goals>
            <configuration>
                <inputSpec>/src/main/resources/api-spec.yml</inputSpec>
                <generatorName>spring</generatorName>
                <apiPackage>com.learning.backend17.api</apiPackage>
                <modelPackage>com.learning.backend17.model</modelPackage>
            </configuration>
        </execution>
    </executions>
</plugin>
`

### Generated Code Structure
`
target/generated-sources/
â”œâ”€â”€ com/learning/backend17/
â”‚   â”œâ”€â”€ api/
â”‚   â”‚   â”œâ”€â”€ UsersApi.java          # Interface from spec
â”‚   â”‚   â””â”€â”€ UsersApiController.java # Generated controller
â”‚   â””â”€â”€ model/
â”‚       â”œâ”€â”€ User.java               # Generated model
â”‚       â””â”€â”€ CreateUserRequest.java
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\17-api-versioning-documentation "EXERCISES.md") @"
# Exercises: API Versioning & Documentation

## Exercise 1: Basic SpringDoc Setup
**Objective**: Configure SpringDoc OpenAPI in a Spring Boot application.

### Task
1. Add springdoc-openapi dependency
2. Create a REST controller with @Operation annotations
3. Configure OpenAPI info in application.yml
4. Access Swagger UI and verify documentation appears

## Exercise 2: URL-Based Versioning
**Objective**: Implement URL-based API versioning.

### Task
1. Create V1UserController with /v1/users endpoints
2. Create V2UserController with /v2/users (additional fields)
3. Both versions must be documented via SpringDoc groups
4. Verify both versions appear in Swagger UI

## Exercise 3: Header Versioning
**Objective**: Implement header-based versioning.

### Task
1. Create a single /users endpoint
2. Implement a HandlerInterceptor to read Accept-Version header
3. Route to different service implementations based on version
4. Document both versions in OpenAPI

## Exercise 4: OpenAPI Groups
**Objective**: Configure separate OpenAPI groups for different versions.

### Task
1. Create multiple GroupedOpenApi beans
2. Each group filters by path pattern
3. Configure different info for each group
4. Verify /v3/api-docs returns separate docs per group

## Exercise 5: Contract-First Development
**Objective**: Design API from OpenAPI specification.

### Task
1. Write an OpenAPI 3.0 specification for a product API
2. Generate Spring server stub using openapi-generator
3. Implement the generated interface
4. Write tests against the generated API

## Exercise 6: Deprecation Strategy
**Objective**: Implement API deprecation.

### Task
1. Mark old endpoints with @Deprecated
2. Add @Operation(deprecated = true) in OpenAPI
3. Add sunset header in response
4. Document migration guide in OpenAPI description
