# Common Mistakes: API Versioning & Documentation

## 1. Exposing Swagger UI in Production
**Mistake**: Leaving Swagger UI enabled in production
**Fix**: Disable with springdoc.swagger-ui.enabled=false or secure with auth

## 2. Breaking Changes Without New Version
**Mistake**: Removing fields from existing API responses
**Fix**: Always add new version for breaking changes

## 3. Not Documenting Deprecation
**Mistake**: Deprecating without @Deprecated or OpenAPI deprecated flag
**Fix**: Add @Deprecated annotation and deprecated=true in @Operation

## 4. Mixing Versioning Strategies
**Mistake**: Using URL versioning in some places and headers in others
**Fix**: Choose ONE strategy and apply consistently

## 5. Forgetting Sunset Headers
**Mistake**: Removing old versions without warning
**Fix**: Include Sunset header with removal date
