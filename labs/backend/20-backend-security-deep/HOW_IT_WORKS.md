# How It Works: Security

CSRF tokens work by embedding a random value in forms/AJAX requests that the attacker cannot read. CORS works by the browser sending a preflight OPTIONS request to check if the target origin is allowed. Rate limiting works by tracking request counts and rejecting when limits exceed. Input validation works by checking data constraints before processing. SQL injection prevention works by separating SQL code from data using parameterized queries.
