# Refactoring: API Versioning & Documentation

## 1. Adding Versioning to Unversioned API

Before:
`java
@RestController
@RequestMapping("/users")
public class UserController { ... }
`

After:
`java
@RestController
@RequestMapping("/v1/users")
public class V1UserController { ... }

@RestController
@RequestMapping("/v2/users")
public class V2UserController { ... }
`

## 2. Migrating from Swagger 2 to OpenAPI 3

Before (SpringFox):
`xml
<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-swagger2</artifactId>
    <version>3.0.0</version>
</dependency>
`

After (SpringDoc):
`xml
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
</dependency>
`

## 3. Consolidating Duplicate Version Code

Before:
`java
@Service
public class V1UserService { ... }
@Service
public class V2UserService { ... }
`

After:
`java
@Service
public class UserService {
    public UserDTO get(String id, int version) {
        return switch(version) {
            case 1 -> toV1(userById(id));
            case 2 -> toV2(userById(id));
            default -> throw new UnsupportedVersionException(version);
        };
    }
}
`
"@

Write-DocFile (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\17-api-versioning-documentation "DEBUGGING.md") @"
# Debugging: API Versioning & Documentation

## 1. Swagger UI Not Loading
- Check springdoc.swagger-ui.enabled is true
- Verify no security filter blocking /swagger-ui/**
- Check browser console for CORS errors

## 2. Missing Endpoints in Docs
- Verify controller is in scanned package
- Check @RequestMapping annotation
- Verify @Operation annotation issues

## 3. Wrong Schema Displayed
- Check Java object fields match expected
- Verify @Schema annotations
- Check Jackson serialization configuration

## 4. Version Routing Issues
- Test each version endpoint directly
- Check interceptor version parsing
- Verify path pattern matching
