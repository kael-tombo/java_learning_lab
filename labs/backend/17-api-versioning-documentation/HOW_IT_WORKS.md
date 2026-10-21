# How It Works: API Versioning & Documentation

## How SpringDoc Generates Documentation
When the application starts, SpringDoc scans all @RestController beans. For each method with @RequestMapping, it reads annotations (@Operation, @ApiResponse), infers parameter types, and builds an OpenAPI Operation object. The OpenAPI object is serialized to JSON when /v3/api-docs is called. Swagger UI fetches this JSON and renders interactive documentation.

## How URL Versioning Works
URL versioning uses path prefixes (/v1/, /v2/). The WebMvcConfigurer's addPathPrefix method adds version prefixes based on handler type. Each controller class implements a marker interface for its version. This separates version logic from business logic.

## How Header Versioning Works
A HandlerInterceptor reads the Accept-Version header from each request. It stores the version in a ThreadLocal, which the controller reads. The service layer uses the version to decide which response format to return. This keeps URLs clean but requires clients to set headers.

## How Contract-First Development Works
You write an OpenAPI specification first, then use OpenAPI Generator to generate server interfaces and model classes. You implement the generated interfaces. This ensures the API contract is always correct and documentation is always in sync.
