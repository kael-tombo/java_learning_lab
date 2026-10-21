# Quiz: API Versioning & Documentation

## Question 1
Which API versioning strategy uses the Accept header?
A) URL-based
B) Header-based
C) Query parameter
D) Content negotiation

**Answer: B** - Header-based versioning uses a custom header like Accept-Version.

## Question 2
What annotation provides operation-level documentation in SpringDoc?
A) @ApiOperation
B) @Operation
C) @Doc
D) @Describe

**Answer: B** - @Operation annotation provides operation summary and description.

## Question 3
Which OpenAPI version is current as of 2024?
A) 2.0
B) 3.0
C) 3.1
D) 4.0

**Answer: B** - OpenAPI 3.0 is the most widely adopted stable version. 3.1 exists but adoption is growing.

## Question 4
What is the default path for SpringDoc OpenAPI spec?
A) /api-docs
B) /v2/api-docs
C) /v3/api-docs
D) /openapi.json

**Answer: C** - /v3/api-docs is the default path.

## Question 5
What is the purpose of GroupedOpenApi in SpringDoc?
A) Group endpoints by controller
B) Group endpoints by version
C) Group endpoints by HTTP method
D) Group endpoints by response type

**Answer: B** - GroupedOpenApi allows separating API documentation by version or domain.

## Question 6
Which HTTP status code indicates a deprecated endpoint is still functional?
A) 301
B) 410
C) 200
D) 308

**Answer: C** - 200 OK (or appropriate success code). Deprecation doesn't change functionality.

## Question 7
What is the correct media type for versioned JSON?
A) application/json
B) application/vnd.company.v1+json
C) application/v1+json
D) application/json;version=1

**Answer: B** - Vendor-specific media types use application/vnd.{org}.{version}+json format.

## Question 8
Which header should be returned with deprecated API responses?
A) X-Deprecated
B) Sunset
C) Retry-After
D) Warning

**Answer: B** - Sunset header indicates when the deprecated API will be removed.

## Question 9
What does the @Schema annotation define in OpenAPI?
A) Database schema
B) Model property metadata
C) Security schema
D) URL schema

**Answer: B** - @Schema describes model properties for OpenAPI documentation.

## Question 10
Which tool generates code from OpenAPI specifications?
A) Swagger UI
B) OpenAPI Generator
C) Postman
D) Insomnia

**Answer: B** - OpenAPI Generator creates server/client code from OpenAPI specs.
