# Mental Models: API Versioning & Documentation

## 1. The Building Renovation Model
An API is like a building. V1 is the original structure. Adding rooms (endpoints) without changing structure is a MINOR update. Knocking down walls (breaking changes) requires V2. Tenants (clients) in the old wing need time to move before you demolish it. The sunset header is the eviction notice.

## 2. The Menu Model
OpenAPI is like a restaurant menu. It lists all available dishes (endpoints), their ingredients (parameters), and prices (responses). Swagger UI is the customer-facing menu display. Different API versions are like different menu editions — old regulars might still want last year's dishes.

## 3. The Contract Model
An API specification is a legal contract between provider and consumer. Breaking changes without versioning is like changing contract terms without notice. Versioning is like contract amendments. Specification-first development is like signing the contract before building the house.

## 4. The Museum Model
Old API versions are like museum exhibits. They're preserved for historical reference but not actively updated. Eventually they're decommissioned (sunset). The migration guide is like the explanatory plaque next to each exhibit.

## 5. The Rosetta Stone Model
API documentation translates between human intent and machine execution. OpenAPI is the Rosetta Stone — it contains the same information in human-readable (YAML/JSON) and machine-readable formats. Code generation from specs is like translating from one language to another.
