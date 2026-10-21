# Refactoring: Security

Before: Disabling CSRF globally
After: Selective CSRF for specific path patterns

Before: Loose CORS (*)
After: Specific allowed origins

Before: String concatenation in SQL
After: Parameterized queries
